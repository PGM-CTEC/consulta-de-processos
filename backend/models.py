import json as _json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index, event
from sqlalchemy.orm import relationship, declarative_mixin
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.sql import func
from .database import Base


@declarative_mixin
class SoftDeleteMixin:
    """Mixin providing soft delete functionality with deleted_at timestamp."""

    deleted_at = Column(DateTime, nullable=True, index=True)

    def soft_delete(self):
        """Mark as deleted without removing from database."""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None

    @property
    def is_deleted(self):
        """Check if record is soft-deleted."""
        return self.deleted_at is not None

class Process(Base, SoftDeleteMixin):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True, nullable=False)
    
    # Metadata fields extracted from DataJud
    class_nature = Column(String, nullable=True) # Classe processual
    subject = Column(String, nullable=True)      # Assunto principal
    court = Column(String, nullable=True)        # Unified court field (legacy)
    tribunal_name = Column(String, nullable=True) # Ex: TJRJ
    court_unit = Column(String, nullable=True)    # Ex: 6ª Vara Cível
    district = Column(String, nullable=True)     # Comarca
    
    distribution_date = Column(DateTime(timezone=True), nullable=True)
    phase = Column(String, nullable=True)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Raw JSON data from DataJud for future proofing
    raw_data = Column(JSON, nullable=True)

    movements = relationship("Movement", back_populates="process", cascade="all, delete-orphan")

class Movement(Base, SoftDeleteMixin):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id"))
    
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=False)
    code = Column(String, nullable=True) # Código do movimento no CNJ
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    process = relationship("Process", back_populates="movements")

    __table_args__ = (
        Index('idx_movement_code', 'code'),
        Index('idx_movement_date', 'date'),
        Index('idx_movement_process_date', 'process_id', 'date'),
    )

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True, nullable=False)
    court = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=True)
    action = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(Text, nullable=True)     # JSON serializado
    new_values = Column(Text, nullable=True)     # JSON serializado
    user_id = Column(String, nullable=True)      # Futuro: sistema de auth
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.table_name}#{self.record_id}>"


def _serialize(obj):
    """Serializa um model SQLAlchemy para dict JSON-safe."""
    if obj is None:
        return None
    result = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name, None)
        if isinstance(val, datetime):
            val = val.isoformat()
        result[col.name] = val
    return _json.dumps(result)


@event.listens_for(Process, 'after_insert')
def _audit_process_insert(mapper, connection, target):
    connection.execute(
        AuditLog.__table__.insert(),
        {
            "table_name": "processes",
            "record_id": target.id,
            "action": "INSERT",
            "old_values": None,
            "new_values": _serialize(target),
            "timestamp": datetime.utcnow(),
        }
    )


@event.listens_for(Process, 'after_update')
def _audit_process_update(mapper, connection, target):
    state = sa_inspect(target)
    old = {}
    for attr in state.attrs:
        hist = attr.history
        if hist.has_changes() and hist.deleted:
            old[attr.key] = hist.deleted[0]
    connection.execute(
        AuditLog.__table__.insert(),
        {
            "table_name": "processes",
            "record_id": target.id,
            "action": "UPDATE",
            "old_values": _json.dumps({
                k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                for k, v in old.items()
            }),
            "new_values": _serialize(target),
            "timestamp": datetime.utcnow(),
        }
    )


@event.listens_for(Process, 'after_delete')
def _audit_process_delete(mapper, connection, target):
    connection.execute(
        AuditLog.__table__.insert(),
        {
            "table_name": "processes",
            "record_id": target.id,
            "action": "DELETE",
            "old_values": _serialize(target),
            "new_values": None,
            "timestamp": datetime.utcnow(),
        }
    )
