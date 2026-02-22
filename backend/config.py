"""
Centralized configuration management using Pydantic Settings.
All environment variables and application settings are defined here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable validation."""

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Consulta Processual API"
    VERSION: str = "0.1.0"

    # Security - CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"  # Comma-separated list

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Database
    DATABASE_URL: str = "sqlite:///./consulta_processual.db"
    DATABASE_ECHO: bool = False

    # DataJud Integration
    DATAJUD_API_KEY: str = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
    DATAJUD_TIMEOUT: int = 30
    DATAJUD_BASE_URL: str = "https://api-publica.datajud.cnj.jus.br"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_API_KEYS: bool = False  # NEVER log API keys in production

    # Rate Limiting (optional, disabled by default)
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60

    # Authentication (optional, disabled by default for development)
    REQUIRE_AUTH: bool = False
    VALID_API_KEYS: str = ""  # Comma-separated API keys for simple auth

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()


# Helper function to check if using SQLite
def is_sqlite_db() -> bool:
    """Check if the database is SQLite."""
    return "sqlite" in settings.DATABASE_URL.lower()
