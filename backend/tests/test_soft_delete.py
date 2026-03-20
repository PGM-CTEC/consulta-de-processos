"""Tests for soft delete functionality."""

from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from backend.models import SoftDeleteMixin

Base = declarative_base()


class MockProcess(Base, SoftDeleteMixin):
    """Mock model for testing soft delete."""
    __tablename__ = 'test_processes'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


def test_soft_delete_marks_timestamp():
    """Soft delete should set deleted_at timestamp."""
    process = MockProcess()
    assert process.is_deleted is False

    process.soft_delete()

    assert process.is_deleted is True
    assert process.deleted_at is not None
    assert isinstance(process.deleted_at, datetime)


def test_restore_clears_deleted_at():
    """Restore should clear the deleted_at timestamp."""
    process = MockProcess()
    process.soft_delete()

    assert process.is_deleted is True

    process.restore()

    assert process.is_deleted is False
    assert process.deleted_at is None


def test_is_deleted_property():
    """is_deleted property should return correct status."""
    process = MockProcess()

    assert process.is_deleted is False

    process.deleted_at = datetime.utcnow()

    assert process.is_deleted is True

    process.deleted_at = None

    assert process.is_deleted is False


def test_soft_delete_workflow():
    """Complete soft delete and restore workflow."""
    process = MockProcess()

    # Initial state
    assert process.is_deleted is False
    assert process.deleted_at is None

    # Soft delete
    process.soft_delete()
    assert process.is_deleted is True
    assert process.deleted_at is not None
    deleted_at = process.deleted_at

    # Restore
    process.restore()
    assert process.is_deleted is False
    assert process.deleted_at is None
