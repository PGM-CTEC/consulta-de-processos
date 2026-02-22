"""
Tests for SQLIntegrationService - Phase 5 Coverage Extension
Story: REM-017 - Backend Unit Tests (70% Coverage)

Test Categories:
- Connection string building
- Database connection testing
- Process number extraction
- Error handling
- Different SQL drivers
"""

from unittest.mock import MagicMock, patch, Mock
from backend import schemas
from backend.services.sql_integration_service import SQLIntegrationService


class TestSQLIntegrationServiceConnectionString:
    """Tests for connection string building (3 tests)."""

    def test_build_connection_string_postgresql(self):
        """TC-1: Build PostgreSQL connection string."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="secret123",
            database="processes_db",
            query="SELECT number FROM processes"
        )
        service = SQLIntegrationService(config)

        assert service.connection_string == "postgresql://admin:secret123@localhost:5432/processes_db"

    def test_build_connection_string_mysql(self):
        """TC-2: Build MySQL connection string."""
        config = schemas.SQLConnectionConfig(
            driver="mysql+pymysql",
            host="db.example.com",
            port=3306,
            user="root",
            password="mysql_pass",
            database="legal_db",
            query="SELECT numero FROM processos"
        )
        service = SQLIntegrationService(config)

        assert service.connection_string == "mysql+pymysql://root:mysql_pass@db.example.com:3306/legal_db"

    def test_build_connection_string_mssql(self):
        """TC-3: Build MSSQL connection string."""
        config = schemas.SQLConnectionConfig(
            driver="mssql+pyodbc",
            host="sqlserver.local",
            port=1433,
            user="sa",
            password="MsSQL@2024",
            database="courts_db",
            query="SELECT ProcessNumber FROM tbl_processes"
        )
        service = SQLIntegrationService(config)

        assert service.connection_string == "mssql+pyodbc://sa:MsSQL@2024@sqlserver.local:1433/courts_db"


class TestSQLIntegrationServiceConnection:
    """Tests for connection testing (4 tests)."""

    def test_test_connection_success(self):
        """TC-4: Test successful database connection."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT number FROM processes LIMIT 5"
        )

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("0000001-01.0000.1.00.0001",),
            ("0000002-01.0000.1.00.0002",),
            ("0000003-01.0000.1.00.0003",),
        ]

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value = mock_result

            service = SQLIntegrationService(config)
            response = service.test_connection()

            assert response.success is True
            assert "Conexão bem-sucedida" in response.message
            assert "3" in response.message
            assert len(response.sample_data) == 3
            assert response.sample_data[0] == "0000001-01.0000.1.00.0001"

    def test_test_connection_failure(self):
        """TC-5: Test failed database connection."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="invalid.host",
            port=5432,
            user="admin",
            password="wrong",
            database="db",
            query="SELECT number FROM processes"
        )

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_engine.connect.side_effect = Exception("Connection refused")

            service = SQLIntegrationService(config)
            response = service.test_connection()

            assert response.success is False
            assert "Erro de conexão" in response.message
            mock_engine.dispose.assert_called_once()

    def test_test_connection_with_empty_result(self):
        """TC-6: Test connection with empty result set."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT number FROM processes WHERE 1=0"
        )

        mock_result = MagicMock()
        mock_result.fetchall.return_value = []

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value = mock_result

            service = SQLIntegrationService(config)
            response = service.test_connection()

            assert response.success is True
            assert "Encontrados 0 registros" in response.message
            assert response.sample_data == []

    def test_test_connection_with_many_results(self):
        """TC-7: Test connection with more than 5 results (samples first 5)."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT number FROM processes"
        )

        # Create 10 result rows
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (f"000000{i}-01.0000.1.00.000{i}",)
            for i in range(10)
        ]

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value = mock_result

            service = SQLIntegrationService(config)
            response = service.test_connection()

            assert response.success is True
            assert "Encontrados 10 registros" in response.message
            assert len(response.sample_data) == 5  # Only first 5 samples


class TestSQLIntegrationServiceExtraction:
    """Tests for process number extraction (3 tests)."""

    def test_get_process_numbers_success(self):
        """TC-8: Extract process numbers from database."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT number FROM processes"
        )

        numbers = [
            "0000001-01.0000.1.00.0001",
            "0000002-01.0000.1.00.0002",
            "0000003-01.0000.1.00.0003",
        ]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [(n,) for n in numbers]

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value = mock_result

            service = SQLIntegrationService(config)
            extracted = service.get_process_numbers()

            assert len(extracted) == 3
            assert extracted == numbers

    def test_get_process_numbers_with_whitespace(self):
        """TC-9: Extract process numbers and strip whitespace."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT number FROM processes"
        )

        # Numbers with leading/trailing whitespace
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("  0000001-01.0000.1.00.0001  ",),
            ("\t0000002-01.0000.1.00.0002\t",),
            (" 0000003-01.0000.1.00.0003 ",),
        ]

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value = mock_result

            service = SQLIntegrationService(config)
            extracted = service.get_process_numbers()

            # All should be stripped
            assert extracted[0] == "0000001-01.0000.1.00.0001"
            assert extracted[1] == "0000002-01.0000.1.00.0002"
            assert extracted[2] == "0000003-01.0000.1.00.0003"

    def test_get_process_numbers_failure(self):
        """TC-10: Handle error when extracting process numbers."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT * FROM invalid_table"
        )

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.side_effect = Exception("Table not found")

            service = SQLIntegrationService(config)

            try:
                service.get_process_numbers()
                assert False, "Should have raised exception"
            except Exception as e:
                assert "Table not found" in str(e)
            finally:
                mock_engine.dispose.assert_called_once()


class TestSQLIntegrationServiceConfiguration:
    """Tests for configuration handling (2 tests)."""

    def test_config_storage(self):
        """TC-11: Configuration is properly stored."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT * FROM processes"
        )

        service = SQLIntegrationService(config)

        assert service.config == config
        assert service.config.driver == "postgresql"
        assert service.config.user == "admin"
        assert service.config.query == "SELECT * FROM processes"

    def test_different_drivers(self):
        """TC-12: Support different SQL drivers."""
        drivers = [
            "postgresql",
            "mysql+pymysql",
            "mssql+pyodbc",
            "sqlite",
            "oracle+cx_oracle"
        ]

        for driver in drivers:
            config = schemas.SQLConnectionConfig(
                driver=driver,
                host="localhost",
                port=5432,
                user="user",
                password="pass",
                database="db",
                query="SELECT id FROM table"
            )

            service = SQLIntegrationService(config)
            assert driver in service.connection_string


class TestSQLIntegrationServiceEngineManagement:
    """Tests for engine lifecycle management (2 tests)."""

    def test_engine_disposal_on_success(self):
        """TC-13: Engine is disposed after successful connection."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="localhost",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT number FROM processes LIMIT 1"
        )

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("0000001-01.0000.1.00.0001",)]

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value = mock_result

            service = SQLIntegrationService(config)
            response = service.test_connection()

            # Engine should be disposed
            mock_engine.dispose.assert_called_once()

    def test_engine_disposal_on_error(self):
        """TC-14: Engine is disposed even on error."""
        config = schemas.SQLConnectionConfig(
            driver="postgresql",
            host="invalid",
            port=5432,
            user="admin",
            password="pass",
            database="db",
            query="SELECT * FROM processes"
        )

        with patch('backend.services.sql_integration_service.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            mock_engine.connect.side_effect = Exception("Connection error")

            service = SQLIntegrationService(config)
            response = service.test_connection()

            # Engine should still be disposed
            mock_engine.dispose.assert_called_once()
            assert response.success is False
