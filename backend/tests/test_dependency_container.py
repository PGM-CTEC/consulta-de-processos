"""
Tests for Dependency Container - Phase 5 Coverage Extension
Story: REM-017 - Backend Unit Tests (70% Coverage)

Test Categories:
- ServiceContainer initialization
- Dependency injection and lazy loading
- DataJudClient factory
- PhaseAnalyzer factory
- ProcessService creation with dependencies
- Factory function create_process_service
"""

from unittest.mock import MagicMock, AsyncMock

from backend.services.dependency_container import ServiceContainer, create_process_service
from backend.services.datajud import DataJudClient
from backend.services.phase_analyzer import PhaseAnalyzer
from backend.services.process_service import ProcessService


class TestServiceContainerInitialization:
    """Tests for ServiceContainer initialization (2 tests)."""

    def test_service_container_init_with_db_only(self, test_db):
        """TC-1: ServiceContainer initializes with only database session."""
        container = ServiceContainer(test_db)

        assert container.db == test_db
        assert container._client is None
        assert container._phase_analyzer is None

    def test_service_container_init_with_mocks(self, test_db):
        """TC-2: ServiceContainer initializes with mock dependencies."""
        mock_client = MagicMock(spec=DataJudClient)
        mock_analyzer = MagicMock(spec=PhaseAnalyzer)

        container = ServiceContainer(
            test_db,
            client=mock_client,
            phase_analyzer=mock_analyzer
        )

        assert container.db == test_db
        assert container._client == mock_client
        assert container._phase_analyzer == mock_analyzer


class TestServiceContainerDataJudClient:
    """Tests for DataJudClient factory (2 tests)."""

    def test_datajud_client_lazy_creation(self, test_db):
        """TC-3: DataJudClient is created on first access."""
        container = ServiceContainer(test_db)

        assert container._client is None

        client = container.datajud_client()

        assert client is not None
        assert isinstance(client, DataJudClient)
        assert container._client == client

    def test_datajud_client_returns_same_instance(self, test_db):
        """TC-4: DataJudClient returns same instance on repeated access."""
        container = ServiceContainer(test_db)

        client1 = container.datajud_client()
        client2 = container.datajud_client()

        assert client1 is client2


class TestServiceContainerPhaseAnalyzer:
    """Tests for PhaseAnalyzer factory (2 tests)."""

    def test_phase_analyzer_lazy_creation(self, test_db):
        """TC-5: PhaseAnalyzer is created on first access."""
        container = ServiceContainer(test_db)

        assert container._phase_analyzer is None

        analyzer = container.phase_analyzer()

        assert analyzer is not None
        assert analyzer == PhaseAnalyzer

    def test_phase_analyzer_returns_same_instance(self, test_db):
        """TC-6: PhaseAnalyzer returns same instance on repeated access."""
        container = ServiceContainer(test_db)

        analyzer1 = container.phase_analyzer()
        analyzer2 = container.phase_analyzer()

        assert analyzer1 is analyzer2


class TestServiceContainerProcessService:
    """Tests for ProcessService creation (3 tests)."""

    def test_process_service_creation_with_defaults(self, test_db):
        """TC-7: ProcessService is created with default dependencies."""
        container = ServiceContainer(test_db)

        service = container.process_service()

        assert isinstance(service, ProcessService)
        assert service.db == test_db
        assert service.client is not None
        assert isinstance(service.client, DataJudClient)

    def test_process_service_creation_with_mocks(self, test_db):
        """TC-8: ProcessService is created with injected mocks."""
        mock_client = MagicMock(spec=DataJudClient)
        mock_analyzer = MagicMock(spec=PhaseAnalyzer)

        container = ServiceContainer(
            test_db,
            client=mock_client,
            phase_analyzer=mock_analyzer
        )

        service = container.process_service()

        assert isinstance(service, ProcessService)
        assert service.client == mock_client
        assert service.phase_analyzer == mock_analyzer

    def test_process_service_reuses_created_dependencies(self, test_db):
        """TC-9: ProcessService reuses dependencies across calls."""
        container = ServiceContainer(test_db)

        service1 = container.process_service()
        service2 = container.process_service()

        # Both services share the same lazily-created client
        assert service1.client is service2.client


class TestCreateProcessServiceFactory:
    """Tests for create_process_service factory function (4 tests)."""

    def test_create_process_service_with_defaults(self, test_db):
        """TC-10: Factory creates ProcessService with defaults."""
        service = create_process_service(test_db)

        assert isinstance(service, ProcessService)
        assert service.db == test_db
        assert service.client is not None
        assert isinstance(service.client, DataJudClient)

    def test_create_process_service_with_custom_client(self, test_db):
        """TC-11: Factory accepts custom DataJudClient."""
        mock_client = MagicMock(spec=DataJudClient)

        service = create_process_service(test_db, client=mock_client)

        assert service.client == mock_client
        assert isinstance(service, ProcessService)

    def test_create_process_service_with_custom_analyzer(self, test_db):
        """TC-12: Factory accepts custom PhaseAnalyzer."""
        mock_analyzer = MagicMock(spec=PhaseAnalyzer)

        service = create_process_service(test_db, phase_analyzer=mock_analyzer)

        assert service.phase_analyzer == mock_analyzer
        assert isinstance(service, ProcessService)

    def test_create_process_service_with_all_mocks(self, test_db):
        """TC-13: Factory accepts both custom client and analyzer."""
        mock_client = MagicMock(spec=DataJudClient)
        mock_analyzer = MagicMock(spec=PhaseAnalyzer)

        service = create_process_service(
            test_db,
            client=mock_client,
            phase_analyzer=mock_analyzer
        )

        assert service.db == test_db
        assert service.client == mock_client
        assert service.phase_analyzer == mock_analyzer
        assert isinstance(service, ProcessService)


class TestDependencyContainerEdgeCases:
    """Tests for edge cases and integration (2 tests)."""

    def test_container_with_mixed_dependencies(self, test_db):
        """TC-14: Container with one mock and one default dependency."""
        mock_client = MagicMock(spec=DataJudClient)

        container = ServiceContainer(test_db, client=mock_client)

        # Phase analyzer should be created on demand
        analyzer = container.phase_analyzer()
        assert analyzer == PhaseAnalyzer

        # Client should use the mock
        assert container.datajud_client() == mock_client

        # Process service should have both
        service = container.process_service()
        assert service.client == mock_client
        assert service.phase_analyzer == analyzer

    def test_multiple_containers_independence(self, test_db):
        """TC-15: Multiple containers maintain independent instances."""
        container1 = ServiceContainer(test_db)
        container2 = ServiceContainer(test_db)

        client1 = container1.datajud_client()
        client2 = container2.datajud_client()

        # Different containers create different client instances
        assert client1 is not client2

        # But same container reuses
        assert container1.datajud_client() is client1
