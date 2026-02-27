from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Process(Base):
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

class Movement(Base):
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
