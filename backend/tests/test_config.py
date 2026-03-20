"""
Tests for configuration management.
"""
import pytest
from ..config import settings, is_sqlite_db


class TestConfiguration:
    """Test suite for configuration settings."""

    def test_settings_exist(self):
        """Test that settings object is created."""
        assert settings is not None

    def test_default_values(self):
        """Test default configuration values."""
        assert settings.PROJECT_NAME == "Consulta Processual API"
        assert settings.VERSION == "0.1.0"
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]
        assert settings.DATAJUD_TIMEOUT > 0

    def test_allowed_origins_list(self):
        """Test that CORS origins are parsed correctly."""
        origins = settings.allowed_origins_list
        assert isinstance(origins, list)
        assert len(origins) > 0
        assert all(isinstance(o, str) for o in origins)

    def test_is_sqlite_db_detection(self):
        """Test SQLite database detection."""
        result = is_sqlite_db()
        assert isinstance(result, bool)
        # Should be True if using default SQLite database
        if "sqlite" in settings.DATABASE_URL.lower():
            assert result is True

    def test_environment_variable_types(self):
        """Test that configuration values have correct types."""
        assert isinstance(settings.DATABASE_URL, str)
        assert isinstance(settings.DATABASE_ECHO, bool)
        assert isinstance(settings.DATAJUD_TIMEOUT, int)
        assert isinstance(settings.LOG_LEVEL, str)
        assert isinstance(settings.RATE_LIMIT_ENABLED, bool)
        assert isinstance(settings.DEBUG, bool)

    def test_datajud_configuration(self):
        """Test DataJud API configuration."""
        assert settings.DATAJUD_BASE_URL.startswith("http")
        assert settings.DATAJUD_TIMEOUT >= 10
        assert isinstance(settings.DATAJUD_API_KEY, str)
