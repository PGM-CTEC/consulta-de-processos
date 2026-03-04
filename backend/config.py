"""
Centralized configuration management using Pydantic Settings.
All environment variables and application settings are defined here.

SECURITY NOTE: Sensitive values are now managed via SecretsManager.
- Secrets are loaded from environment variables via python-dotenv
- Never hardcode secrets in this file
- All sensitive values should be in .env (git-ignored)
- See backend/secrets_manager.py for secrets access patterns
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')


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

    # Database (loaded from secrets manager)
    DATABASE_URL: str = "sqlite:///./consulta_processual.db"
    DATABASE_ECHO: bool = False

    # DataJud Integration (secrets loaded via SecretsManager)
    DATAJUD_API_KEY: str = ""  # Will be loaded from secrets manager
    DATAJUD_TIMEOUT: int = 30
    DATAJUD_BASE_URL: str = "https://api-publica.datajud.cnj.jus.br"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_API_KEYS: bool = False  # NEVER log API keys in production

    # Rate Limiting (optional, disabled by default)
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60

    # Bulk Processing (Story: PERF-ARCH-001)
    BULK_MAX_CONCURRENT: int = 10  # Max concurrent DataJud API calls
    BULK_REQUEST_DELAY: float = 0.2  # Segundos entre chamadas DataJud no bulk (evita throttling)

    # Authentication (optional, disabled by default for development)
    REQUIRE_AUTH: bool = False
    VALID_API_KEYS: str = ""  # Comma-separated API keys for simple auth

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True

    # Monitoring (optional)
    SENTRY_DSN: str = ""  # Empty = Sentry disabled

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
