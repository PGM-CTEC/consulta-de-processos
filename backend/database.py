from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from contextlib import contextmanager
from sqlalchemy.exc import IntegrityError
from config import settings, is_sqlite_db

# Configure database engine with conditional SQLite args
connect_args = {}
engine_kwargs = {"echo": settings.DATABASE_ECHO}

if is_sqlite_db():
    # SQLite-specific: Static pool + allow multiple threads to access the same connection
    # Story: REM-010 (DB-011) - Connection Pooling
    engine_kwargs["poolclass"] = StaticPool
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def transaction_scope(db: Session):
    """
    Provide a transactional scope with automatic rollback on error.

    Usage:
        with transaction_scope(db) as session:
            session.add(obj)
            session.flush()
            # ... more operations
        # Automatic commit on success, rollback on exception
    """
    try:
        yield db
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise
