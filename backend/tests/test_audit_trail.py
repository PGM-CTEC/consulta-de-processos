"""Tests for LGPD Audit Trail — REM-026"""
import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Process, AuditLog


@pytest.fixture
def test_db():
    """In-memory SQLite database for tests."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_audit_log_table_exists(test_db):
    """AuditLog model should be importable and table should exist."""
    count = test_db.query(AuditLog).count()
    assert count == 0


def test_insert_process_creates_audit_entry(test_db):
    """Inserting a Process should create an INSERT entry in audit_log."""
    process = Process(number="0001234-56.2024.8.19.0001")
    test_db.add(process)
    test_db.commit()

    logs = test_db.query(AuditLog).filter_by(table_name="processes", action="INSERT").all()
    assert len(logs) == 1
    assert logs[0].record_id == process.id
    assert logs[0].action == "INSERT"


def test_update_process_creates_audit_entry(test_db):
    """Updating a Process should create an UPDATE entry in audit_log."""
    process = Process(number="0001234-56.2024.8.19.0002")
    test_db.add(process)
    test_db.commit()

    process.phase = "Execução"
    test_db.commit()

    logs = test_db.query(AuditLog).filter_by(table_name="processes", action="UPDATE").all()
    assert len(logs) == 1
    assert logs[0].table_name == "processes"


def test_delete_process_creates_audit_entry(test_db):
    """Deleting a Process should create a DELETE entry in audit_log."""
    process = Process(number="0001234-56.2024.8.19.0003")
    test_db.add(process)
    test_db.commit()
    pid = process.id

    test_db.delete(process)
    test_db.commit()

    logs = test_db.query(AuditLog).filter_by(table_name="processes", action="DELETE").all()
    assert len(logs) == 1
    assert logs[0].record_id == pid


def test_audit_log_has_timestamp(test_db):
    """Each audit entry must have a timestamp."""
    process = Process(number="0001234-56.2024.8.19.0004")
    test_db.add(process)
    test_db.commit()

    log = test_db.query(AuditLog).first()
    assert log.timestamp is not None
