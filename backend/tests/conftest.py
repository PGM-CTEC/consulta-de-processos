"""
Pytest configuration and shared fixtures for backend tests.
Story: TEST-ARCH-001 - Backend Unit & Integration Tests
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.config import Settings
from backend import models
from backend.services.process_service import ProcessService
from backend.services.datajud import DataJudClient


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing."""
    # In-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    engine.dispose()


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_datajud_client():
    """Create mock DataJud client."""
    client = AsyncMock(spec=DataJudClient)

    # Default mock responses
    client.get_process = AsyncMock(return_value={
        "numeroProcesso": "00000001010000100001",
        "classe": {"codigo": "0001", "nome": "Ação de Cobrança"},
        "tribunal": "TJSP",
        "orgaoJulgador": {"nome": "1ª Vara Cível", "codigoMunicipioIBGE": "3550308"},
        "assuntos": [{"nome": "Cobrança"}],
        "dataAjuizamento": "20200101000000",
        "movimentos": [
            {
                "dataHora": "2020-01-15T10:00:00.000Z",
                "descricao": "Distribuição",
                "orgaoJulgador": {"nome": "1ª Vara Cível"}
            }
        ],
        "grau": "G1"
    })

    client.get_process_instances = AsyncMock(return_value=(
        {
            "numeroProcesso": "00000001010000100001",
            "classe": {"codigo": "0001", "nome": "Ação de Cobrança"},
            "tribunal": "TJSP",
            "grau": "G1",
            "movimentos": []
        },
        {"instances_count": 1, "selected_index": 0, "instances": []}
    ))

    return client


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return MagicMock(spec=Settings)


@pytest.fixture
def process_service(test_db):
    """Create ProcessService with test database."""
    return ProcessService(test_db)


@pytest.fixture
def sample_process_data():
    """Sample DataJud API response for testing."""
    return {
        "numeroProcesso": "00000001010000100001",
        "classe": {
            "codigo": "0001",
            "nome": "Ação de Cobrança"
        },
        "tribunal": "TJSP",
        "orgaoJulgador": {
            "nome": "1ª Vara Cível",
            "codigoMunicipioIBGE": "3550308"
        },
        "assuntos": [
            {"nome": "Cobrança"}
        ],
        "dataAjuizamento": "20200101000000",
        "movimentos": [
            {
                "dataHora": "2020-01-15T10:00:00.000Z",
                "descricao": "Distribuição",
                "orgaoJulgador": {"nome": "1ª Vara Cível"}
            }
        ],
        "grau": "G1"
    }


@pytest.fixture
def sample_bulk_numbers():
    """Sample CNJ numbers for bulk testing."""
    return [
        f"0000000{i:02d}010000100001" for i in range(1, 6)
    ]


# ============================================================================
# DATABASE RECORD FIXTURES
# ============================================================================

@pytest.fixture
def sample_process_db(test_db):
    """Create sample process in database."""
    process = models.Process(
        number="00000001010000100001",
        class_nature="Ação de Cobrança",
        subject="Cobrança",
        court="TJSP - 1ª Vara Cível",
        tribunal_name="TJSP",
        court_unit="1ª Vara Cível",
        district="3550308",
        phase="02"
    )
    test_db.add(process)
    test_db.commit()
    test_db.refresh(process)
    return process


@pytest.fixture
def sample_movement_db(test_db, sample_process_db):
    """Create sample movement for process."""
    movement = models.Movement(
        process_id=sample_process_db.id,
        date="2020-01-15",
        code="000",
        description="Distribuição"
    )
    test_db.add(movement)
    test_db.commit()
    test_db.refresh(movement)
    return movement


@pytest.fixture
def sample_history_db(test_db):
    """Create sample search history."""
    history = models.SearchHistory(
        number="00000001010000100001",
        court="TJSP"
    )
    test_db.add(history)
    test_db.commit()
    test_db.refresh(history)
    return history


# ============================================================================
# MARKERS
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# ============================================================================
# HELPERS
# ============================================================================

def assert_process_valid(process):
    """Assert process has required fields."""
    assert process.id is not None
    assert process.number is not None
    assert len(process.number) == 20


def assert_movement_valid(movement):
    """Assert movement has required fields."""
    assert movement.id is not None
    assert movement.process_id is not None
    assert movement.date is not None or movement.description is not None
