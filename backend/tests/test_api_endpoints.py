"""
Tests for API Endpoints - Phase 4 Coverage Completion
Story: REM-017 - Backend Unit Tests (70% Coverage)

Test Categories:
- Health checks (/health, /ready)
- Process retrieval (GET /processes/{number})
- Bulk processing (POST /processes/bulk)
- Statistics (GET /stats)
- Search history (GET /history, DELETE /history)
- Root endpoint (GET /)
"""

from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient

from backend.main import app
from backend import models
from backend.database import get_db


def override_get_db_mock():
    """Provide mock database for testing."""
    mock_db = MagicMock()
    mock_db.execute = MagicMock(return_value=True)
    yield mock_db


class TestHealthCheckEndpoints:
    """Tests for health and readiness endpoints (2 tests)."""

    def test_health_check_success(self):
        """TC-1: Health check returns healthy status when DB is connected."""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db_mock

        try:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
        finally:
            app.dependency_overrides.clear()

    def test_readiness_check_success(self):
        """TC-2: Readiness check returns ready status when DB is connected."""
        client = TestClient(app)
        app.dependency_overrides[get_db] = override_get_db_mock

        try:
            response = client.get("/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["ready"] is True
            assert "version" in data
        finally:
            app.dependency_overrides.clear()


class TestProcessEndpoints:
    """Tests for process retrieval endpoints (5 tests)."""

    def test_get_process_success(self, test_db):
        """TC-3: Get single process returns process data."""
        client = TestClient(app)
        process_number = "0000001-01.0000.1.00.0001"

        # Create test process in DB
        process = models.Process(
            number=process_number,
            tribunal_name="TJSP",
            class_nature="Ação de Cobrança",
            subject="Cobrança",
            court="TJSP - Foro Central",
            phase="01",
            raw_data={}
        )
        test_db.add(process)
        test_db.commit()

        app.dependency_overrides[get_db] = lambda: test_db

        with patch('backend.services.process_service.ProcessService.get_or_update_process') as mock_method:
            mock_method.return_value = process
            try:
                response = client.get(f"/processes/{process_number}")
                assert response.status_code == 200
                data = response.json()
                assert data["number"] == process_number
                assert data["tribunal_name"] == "TJSP"
            finally:
                app.dependency_overrides.clear()

    def test_get_process_not_found(self, test_db):
        """TC-4: Get process returns 404 when not found."""
        client = TestClient(app)
        process_number = "9999999-99.9999.9.99.9999"

        app.dependency_overrides[get_db] = lambda: test_db

        with patch('backend.services.process_service.ProcessService.get_or_update_process') as mock_method:
            mock_method.return_value = None
            try:
                response = client.get(f"/processes/{process_number}")
                assert response.status_code == 404
            finally:
                app.dependency_overrides.clear()

    def test_get_process_instances_success(self, test_db):
        """TC-5: Get process instances returns list of instances."""
        client = TestClient(app)
        process_number = "0000002-01.0000.1.00.0002"

        instances_response = {
            "process_number": process_number,
            "instances_count": 2,
            "selected_index": 0,
            "instances": [
                {"index": 0, "grau": "G1", "tribunal": "TJSP", "orgao_julgador": "Vara 1"},
                {"index": 1, "grau": "G2", "tribunal": "TJSP", "orgao_julgador": "Apelação"}
            ]
        }

        app.dependency_overrides[get_db] = lambda: test_db

        with patch('backend.services.process_service.ProcessService.get_all_instances') as mock_method:
            mock_method.return_value = instances_response
            try:
                response = client.get(f"/processes/{process_number}/instances")
                assert response.status_code == 200
                data = response.json()
                assert data["instances_count"] == 2
                assert len(data["instances"]) == 2
            finally:
                app.dependency_overrides.clear()

    def test_get_process_instance_detail_success(self, test_db):
        """TC-6: Get specific instance returns detailed process data."""
        client = TestClient(app)
        process_number = "0000003-01.0000.1.00.0003"
        instance_index = 0

        instance_response = {
            "id": 1,
            "number": process_number,
            "tribunal_name": "TJSP",
            "class_nature": "Ação Cível",
            "movements": [],
            "last_update": datetime.now()
        }

        app.dependency_overrides[get_db] = lambda: test_db

        # Patch the constructor to return a mock service
        with patch('backend.main.ProcessService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_process_instance = AsyncMock(return_value=instance_response)
            mock_service_class.return_value = mock_service
            try:
                response = client.get(f"/processes/{process_number}/instances/{instance_index}")
                assert response.status_code == 200
                data = response.json()
                assert data["number"] == process_number
            finally:
                app.dependency_overrides.clear()


class TestBulkProcessEndpoint:
    """Tests for bulk processing endpoint (2 tests)."""

    def test_bulk_request_schema_validation(self):
        """TC-7: Bulk request validates input schema."""
        # Test that bulk request schema is properly defined
        numbers = ["0000001-01.0000.1.00.0001", "0000002-01.0000.1.00.0002"]
        request_data = {"numbers": numbers}
        # Should be valid according to BulkProcessRequest
        from backend.schemas import BulkProcessRequest
        bulk_req = BulkProcessRequest(**request_data)
        assert bulk_req.numbers == numbers

    def test_bulk_response_schema_definition(self):
        """TC-8: Bulk response schema has correct fields."""
        # Test that bulk response schema is properly defined
        from backend.schemas import BulkProcessResponse
        from inspect import signature

        # Check that BulkProcessResponse has results and failures fields
        bulk_resp = BulkProcessResponse(results=[], failures=[])
        assert hasattr(bulk_resp, 'results')
        assert hasattr(bulk_resp, 'failures')
        assert bulk_resp.results == []
        assert bulk_resp.failures == []


class TestStatsEndpoint:
    """Tests for statistics endpoint (1 test)."""

    def test_get_stats_success(self, test_db):
        """TC-9: Get database statistics returns aggregated data."""
        client = TestClient(app)

        app.dependency_overrides[get_db] = lambda: test_db

        stats_response = {
            "total_processes": 1,
            "total_movements": 1,
            "tribunals": [{"tribunal_name": "TJSP", "count": 1}],
            "phases": [{"phase": "01", "count": 1}],
            "timeline": [{"month": "2024-01", "count": 1}]
        }

        with patch('backend.main.StatsService') as mock_stats_class:
            mock_stats = MagicMock()
            mock_stats.get_database_stats = MagicMock(return_value=stats_response)
            mock_stats_class.return_value = mock_stats
            try:
                response = client.get("/stats")
                assert response.status_code == 200
                data = response.json()
                assert data["total_processes"] == 1
                assert len(data["tribunals"]) == 1
                assert len(data["phases"]) == 1
                assert len(data["timeline"]) == 1
            finally:
                app.dependency_overrides.clear()


class TestSearchHistoryEndpoint:
    """Tests for search history endpoints (2 tests)."""

    def test_get_search_history_success(self, test_db):
        """TC-10: Get search history returns recent searches."""
        client = TestClient(app)

        # Create test history entries
        for i in range(3):
            history = models.SearchHistory(
                number=f"000000{i}-01.0000.1.00.000{i}",
                court="TJSP"
            )
            test_db.add(history)
        test_db.commit()

        app.dependency_overrides[get_db] = lambda: test_db

        try:
            response = client.get("/history")
            assert response.status_code == 200
            data = response.json()
            assert len(data) >= 3
        finally:
            app.dependency_overrides.clear()

    def test_clear_search_history_success(self, test_db):
        """TC-11: Clear search history removes all entries."""
        client = TestClient(app)

        # Create test history
        history = models.SearchHistory(
            number="0000001-01.0000.1.00.0001",
            court="TJSP"
        )
        test_db.add(history)
        test_db.commit()

        app.dependency_overrides[get_db] = lambda: test_db

        try:
            response = client.delete("/history")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
        finally:
            app.dependency_overrides.clear()


class TestRootEndpoint:
    """Tests for root endpoint (1 test)."""

    def test_root_endpoint_success(self):
        """TC-12: Root endpoint returns welcome message."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestLogsEndpoint:
    """Tests for logs endpoint (1 test)."""

    def test_receive_logs_success(self):
        """TC-13: Receive logs endpoint accepts and processes logs."""
        client = TestClient(app)

        logs = [
            {"message": "Test log 1", "level": "info"},
            {"message": "Test log 2", "level": "error"}
        ]

        response = client.post("/api/logs", json=logs)

        assert response.status_code == 200
        data = response.json()
        assert data["received"] == 2


class TestErrorHandling:
    """Tests for error handling in endpoints (2 tests)."""

    def test_invalid_bulk_request_empty(self):
        """TC-14: Invalid bulk request with empty list returns validation error."""
        client = TestClient(app)

        # Send empty numbers list - should return 422 validation error
        response = client.post("/processes/bulk", json={"numbers": []})
        # Pydantic validates min_length=1
        assert response.status_code == 422

    def test_root_endpoint_no_auth_needed(self):
        """TC-15: Root endpoint doesn't require authentication."""
        client = TestClient(app)
        response = client.get("/")
        # Root endpoint should be accessible without any DB
        assert response.status_code == 200
        assert "message" in response.json()
