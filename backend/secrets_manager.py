"""
Secrets Manager Module

Provides secure access to secrets with support for multiple backends:
- Local environment variables (.env file)
- AWS Secrets Manager (future)
- dotenv-vault (future)

This abstraction allows seamless migration between secret backends.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()


class SecretsManager:
    """
    Centralized secrets management with backend abstraction.

    Supports multiple backends for storing secrets:
    - Environment variables (current)
    - AWS Secrets Manager (planned)
    - HashiCorp Vault (planned)
    - dotenv-vault (planned)
    """

    def __init__(self, backend: str = "env"):
        """
        Initialize secrets manager.

        Args:
            backend: Backend type ('env', 'aws', 'vault', 'dotenv-vault')
        """
        self.backend = backend
        self._cache: Dict[str, Any] = {}

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from configured backend.

        Args:
            key: Secret key/name
            default: Default value if secret not found

        Returns:
            Secret value or default
        """
        if self.backend == "env":
            return self._get_from_env(key, default)
        elif self.backend == "aws":
            return self._get_from_aws_secrets(key, default)
        else:
            logger.warning(f"Unsupported backend: {self.backend}. Falling back to env.")
            return self._get_from_env(key, default)

    def _get_from_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variables."""
        return os.getenv(key, default)

    def _get_from_aws_secrets(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from AWS Secrets Manager.

        Requires:
        - boto3 installed
        - AWS credentials configured
        - Secret exists in AWS Secrets Manager
        """
        try:
            import boto3
            import json

            client = boto3.client('secretsmanager', region_name='us-east-1')
            response = client.get_secret_value(SecretId=f'consulta-processo/{key}')

            # Parse JSON secret if applicable
            try:
                secret = json.loads(response['SecretString'])
                return secret.get(key, default)
            except json.JSONDecodeError:
                return response['SecretString']

        except Exception as e:
            logger.error(f"Failed to get secret {key} from AWS: {e}")
            logger.info("Falling back to environment variable")
            return os.getenv(key, default)

    def list_secrets_keys(self) -> list:
        """Get list of all secret keys (for audit purposes)."""
        required_keys = [
            'DATAJUD_APIKEY',
            'DATABASE_URL',
            'SENTRY_DSN'
        ]
        found_keys = [key for key in required_keys if os.getenv(key)]
        return found_keys

    def validate_secrets(self) -> Dict[str, bool]:
        """
        Validate that all required secrets are configured.

        Returns:
            Dict with validation status for each secret
        """
        required_secrets = {
            'DATAJUD_APIKEY': 'DataJud API Key',
            'DATABASE_URL': 'Database connection URL',
            'SENTRY_DSN': 'Sentry DSN (optional)'
        }

        validation = {}
        for key, description in required_secrets.items():
            is_set = bool(os.getenv(key))
            validation[key] = is_set
            status = "✓" if is_set else "✗"
            logger.info(f"{status} {key}: {description}")

        return validation


# Global instance
_secrets_manager = None


def get_secrets_manager(backend: str = "env") -> SecretsManager:
    """Get or create global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager(backend=backend)
    return _secrets_manager


# Convenience functions
def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret value."""
    manager = get_secrets_manager()
    return manager.get_secret(key, default)


def validate_all_secrets() -> Dict[str, bool]:
    """Validate all required secrets are set."""
    manager = get_secrets_manager()
    return manager.validate_secrets()


if __name__ == "__main__":
    # Audit secrets configuration
    logger.basicConfig(level=logging.INFO)
    manager = get_secrets_manager()

    print("\n=== SECRETS CONFIGURATION AUDIT ===\n")
    validation = manager.validate_secrets()

    found = sum(1 for v in validation.values() if v)
    total = len(validation)

    print(f"\nSecrets found: {found}/{total}")
    print(f"\nBackend: {manager.backend}")
    print(f"Status: {'READY' if found >= 2 else 'INCOMPLETE'}")
