"""Tests for foreign key constraint behavior (REM-044)."""

import pytest
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, event
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class TestProcess(Base):
    __tablename__ = 'fk_test_processes'
    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True)
    searches = relationship("TestSearchHistory", back_populates="process", cascade="all, delete-orphan")


class TestSearchHistory(Base):
    __tablename__ = 'fk_test_search_history'
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey("fk_test_processes.id", ondelete="CASCADE"))
    search_term = Column(String)
    process = relationship("TestProcess", back_populates="searches")


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    # Enable SQLite FK enforcement
    event.listen(engine, "connect", lambda c, _: c.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_cascade_delete(session):
    """Deleting process should delete related search_history."""
    process = TestProcess(number="0001234-56.2020.1.26.0100")
    session.add(process)
    session.flush()

    history = TestSearchHistory(process_id=process.id, search_term="test")
    session.add(history)
    session.commit()

    assert session.query(TestSearchHistory).count() == 1

    session.delete(process)
    session.commit()

    assert session.query(TestSearchHistory).count() == 0


def test_invalid_process_id_rejected(session):
    """Inserting search_history with invalid process_id should fail."""
    invalid_history = TestSearchHistory(process_id=99999, search_term="test")
    session.add(invalid_history)

    with pytest.raises(IntegrityError):
        session.commit()


def test_valid_foreign_key_works(session):
    """Valid FK reference should succeed."""
    process = TestProcess(number="valid-process")
    session.add(process)
    session.flush()

    history = TestSearchHistory(process_id=process.id, search_term="valid search")
    session.add(history)
    session.commit()

    assert session.query(TestSearchHistory).count() == 1
