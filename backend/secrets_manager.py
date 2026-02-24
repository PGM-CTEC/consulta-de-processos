"""
Secrets Management Module

This module provides a centralized interface for accessing secrets.
Supports multiple backends:
- Environment variables (development)
- .env file with dotenv (development)
- AWS Secrets Manager (production)
- dotenv-vault (production)

SECURITY GUIDELINES:
1. Never hardcode secrets in code
2. Never log secrets (use masked values)
3. Always use this module to access secrets
4. Rotate secrets regularly
"""

import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv


class SecretsManager:
    """Centralized secrets management interface."""

    def __init__(self):
        """Initialize secrets manager."""
        # Load .env file if it exists (development)
        if os.path.exists('.env'):
            load_dotenv('.env')

    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """
        Get a secret value.

        Priority order:
        1. Environment variable (highest priority)
        2. AWS Secrets Manager (if AWS_REGION set)
        3. dotenv-vault (if DOTENV_KEY set)
        4. Default value
        5. Raise KeyError (if no default)

        Args:
            key: Secret key name
            default: Default value if secret not found

        Returns:
            Secret value

        Raises:
            KeyError: If secret not found and no default provided
        """
        # Try environment variable first (always takes priority)
        if key in os.environ:
            return os.environ[key]

        # Try AWS Secrets Manager
        if os.getenv('AWS_REGION'):
            try:
                return self._get_aws_secret(key)
            except Exception:
                pass  # Fall through to next option

        # Try dotenv-vault
        if os.getenv('DOTENV_KEY'):
            try:
                return self._get_vault_secret(key)
            except Exception:
                pass  # Fall through to next option

        # Return default or raise error
        if default is not None:
            return default
        raise KeyError(f"Secret '{key}' not found")

    def _get_aws_secret(self, key: str) -> str:
        """
        Get secret from AWS Secrets Manager.

        Implementation requires: boto3

        Args:
            key: Secret key name (maps to secret id in AWS)

        Returns:
            Secret value
        """
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 required for AWS Secrets Manager")

        client = boto3.client(
            'secretsmanager',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

        try:
            response = client.get_secret_value(SecretId=key)
            if 'SecretString' in response:
                secret = json.loads(response['SecretString'])
                if isinstance(secret, dict):
                    return secret.get('value', secret)
                return secret
            else:
                return response['SecretBinary'].decode('utf-8')
        except client.exceptions.ResourceNotFoundException:
            raise KeyError(f"Secret '{key}' not found in AWS Secrets Manager")

    def _get_vault_secret(self, key: str) -> str:
        """
        Get secret from dotenv-vault.

        Implementation requires: dotenv-vault

        Args:
            key: Secret key name

        Returns:
            Secret value
        """
        try:
            from dotenv_vault import load_dotenv as vault_load_dotenv
        except ImportError:
            raise ImportError("dotenv-vault required")

        # Load from .env.vault
        vault_load_dotenv('.env.vault')
        return os.getenv(key)

    def get_secrets_dict(self, keys: list[str]) -> Dict[str, str]:
        """
        Get multiple secrets as dictionary.

        Args:
            keys: List of secret key names

        Returns:
            Dictionary with key -> secret mappings
        """
        return {key: self.get_secret(key) for key in keys}


# Global secrets manager instance
secrets = SecretsManager()


# Common secrets helper functions
def get_database_url() -> str:
    """Get database connection URL."""
    return secrets.get_secret('DATABASE_URL', 'sqlite:///./consulta_processual.db')


def get_datajud_api_key() -> str:
    """Get DataJud API key."""
    key = secrets.get_secret('DATAJUD_API_KEY', None)
    if not key:
        raise KeyError("DATAJUD_API_KEY not configured. Set it in .env file.")
    return key


def get_sentry_dsn() -> Optional[str]:
    """Get Sentry DSN for error tracking (optional)."""
    return secrets.get_secret('SENTRY_DSN', None)


def is_secrets_configured() -> bool:
    """Check if secrets are properly configured."""
    try:
        get_datajud_api_key()
        return True
    except KeyError:
        return False
