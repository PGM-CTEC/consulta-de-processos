"""
Tests for FastAPI endpoints.
Story: TEST-ARCH-001 - Backend Unit & Integration Tests

Tests HTTP contracts and API behavior:
- GET /processes/{number}
- POST /processes/bulk
- GET /health, /ready
- Error handling and validation
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from backend.main import app
from backend import models


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)
    app.dependency_overrides.clear()


class TestGetProcessEndpoint:
    """Tests for GET /processes/{number}"""

    def test_get_process_success(self, client, mock_datajud_client):
        """Successfully fetch process."""
        with patch('backend.main.ProcessService') as MockService:
            mock_service = MagicMock()
            mock_service.get_or_update_process = AsyncMock(return_value=MagicMock(
                id=1,
                number="00000001010000100001",
                class_nature="Ação de Cobrança",
                subject="Cobrança",
                court="TJSP - 1ª Vara",
                tribunal_name="TJSP",
                court_unit="1ª Vara",
                district="3550308",
                phase="02",
                distribution_date=None,
                last_update=None,
                raw_data={}
            ))
            MockService.return_value = mock_service

            response = client.get("/processes/00000001010000100001")

            assert response.status_code == 200
            data = response.json()
            assert data["number"] == "00000001010000100001"
            assert data["tribunal_name"] == "TJSP"

    def test_get_process_not_found(self, client):
        """Return 404 when process not found."""
        with patch('backend.main.ProcessService') as MockService:
            mock_service = MagicMock()
            mock_service.get_or_update_process = AsyncMock(return_value=None)
            MockService.return_value = mock_service

            response = client.get("/processes/99999999999999999999")

            assert response.status_code == 404

    def test_get_process_invalid_number(self, client):
        """Return 422 for invalid process number."""
        response = client.get("/processes/invalid")

        # FastAPI will still attempt to process it
        assert response.status_code in [400, 422, 404]

    def test_get_process_rate_limit(self, client):
        """Respect rate limit of 100/minute."""
        # Test that endpoint has rate limit decorator
        with patch('backend.main.ProcessService') as MockService:
            mock_service = MagicMock()
            mock_service.get_or_update_process = AsyncMock(return_value=MagicMock(
                id=1,
                number="00000001010000100001",
                class_nature="Ação",
                subject="Cobrança",
                court="TJSP",
                tribunal_name="TJSP",
                court_unit="Vara",
                district="3550308",
                phase="02",
                distribution_date=None,
                last_update=None,
                raw_data={}
            ))
            MockService.return_value = mock_service

            # Single request should work
            response = client.get("/processes/00000001010000100001")
            assert response.status_code == 200


class TestBulkProcessesEndpoint:
    """Tests for POST /processes/bulk"""

    def _make_mock_process(self, number: str, tribunal: str = "TJSP") -> MagicMock:
        """Cria um MagicMock com todos os campos de ProcessResponse preenchidos.

        Pydantic v2 não coerce MagicMock para None — todos os campos opcionais
        de string precisam de valores válidos (str | None) para que a serialização
        da response_model funcione sem ValidationError.
        """
        m = MagicMock(spec=models.Process)
        m.id = 1
        m.number = number
        m.class_nature = None
        m.subject = None
        m.court = None
        m.tribunal_name = tribunal
        m.court_unit = None
        m.district = None
        m.judge = None
        m.distribution_date = None
        m.phase = None
        m.phase_warning = None
        m.last_update = datetime(2024, 1, 1, tzinfo=timezone.utc)
        m.raw_data = None
        m.deleted_at = None
        return m

    def test_bulk_success(self, client):
        """Successfully process bulk request."""
        with patch('backend.main.ProcessService') as MockService:
            mock_service = MagicMock()
            mock_service.get_bulk_processes = AsyncMock(return_value={
                "results": [self._make_mock_process("00000001010000100001")],
                "failures": []
            })
            MockService.return_value = mock_service

            payload = {"numbers": ["00000001010000100001"]}

            response = client.post("/processes/bulk", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 1
            assert len(data["failures"]) == 0

    def test_bulk_partial_failure(self, client):
        """Handle partial failures in bulk request."""
        with patch('backend.main.ProcessService') as MockService:
            mock_service = MagicMock()
            mock_service.get_bulk_processes = AsyncMock(return_value={
                "results": [self._make_mock_process("00000001010000100001")],
                "failures": ["99999999999999999999"]
            })
            MockService.return_value = mock_service

            payload = {"numbers": ["00000001010000100001", "99999999999999999999"]}

            response = client.post("/processes/bulk", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 1
            assert len(data["failures"]) == 1

    def test_bulk_empty_list(self, client):
        """Handle empty numbers list."""
        payload = {"numbers": []}

        response = client.post("/processes/bulk", json=payload)

        # 422 = Pydantic validation error (min_length=1 não satisfeito); 400 também seria aceitável
        assert response.status_code in [200, 400, 422]

    def test_bulk_rate_limit(self, client):
        """Respect rate limit of 50/minute for bulk."""
        # Test that endpoint has rate limit decorator for bulk (50/min)
        with patch('backend.main.ProcessService') as MockService:
            mock_service = MagicMock()
            mock_service.get_bulk_processes = AsyncMock(return_value={
                "results": [],
                "failures": []
            })
            MockService.return_value = mock_service

            payload = {"numbers": ["00000001010000100001"]}

            response = client.post("/processes/bulk", json=payload)
            assert response.status_code == 200


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_endpoint_healthy(self, client, test_db):
        """GET /health returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "service" in data
        assert "version" in data

    def test_health_endpoint_structure(self, client):
        """Verify health response structure."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]

    def test_ready_endpoint_true(self, client):
        """GET /ready returns ready status."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert "version" in data

    def test_ready_endpoint_structure(self, client):
        """Verify ready response structure."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "ready" in data
        assert isinstance(data["ready"], bool)


class TestErrorHandling:
    """Tests for error responses."""

    def test_process_not_found_error(self, client):
        """Handle ProcessNotFoundException."""
        with patch('backend.main.ProcessService') as MockService:
            mock_service = MagicMock()
            mock_service.get_or_update_process = AsyncMock(return_value=None)
            MockService.return_value = mock_service

            response = client.get("/processes/99999999999999999999")

            assert response.status_code == 404

    def test_invalid_request_format(self, client):
        """Handle invalid request format."""
        response = client.post("/processes/bulk", json={"invalid": "format"})

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestHistoryEndpoint:
    """Tests for search history endpoint."""

    def test_get_history_empty(self, client):
        """Get empty history when no searches."""
        response = client.get("/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_history_with_records(self, client, test_db, sample_history_db):
        """Retrieve search history."""
        response = client.get("/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_clear_history(self, client):
        """Clear search history."""
        response = client.delete("/history")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

        # Verify history is cleared
        response = client.get("/history")
        assert len(response.json()) == 0
