"""Sensitive data redaction utilities."""

import re
from typing import Any, Dict


# Patterns for sensitive data
REDACTION_PATTERNS = {
    'cpf': r'\d{3}\.\d{3}\.\d{3}-\d{2}',
    'api_key': r'[a-zA-Z0-9]{40,}',
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
}


def redact_value(value: str) -> str:
    """
    Redact sensitive patterns in a string.

    Args:
        value: String to redact

    Returns:
        String with sensitive data replaced
    """
    if not isinstance(value, str):
        return value

    for pattern_name, pattern in REDACTION_PATTERNS.items():
        value = re.sub(pattern, f'[REDACTED-{pattern_name.upper()}]', value)

    return value


def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively redact sensitive data in a dictionary.

    Args:
        data: Dictionary to redact

    Returns:
        Dictionary with sensitive values redacted
    """
    if not isinstance(data, dict):
        return data

    redacted = {}
    for key, value in data.items():
        if isinstance(value, str):
            redacted[key] = redact_value(value)
        elif isinstance(value, dict):
            redacted[key] = redact_dict(value)
        elif isinstance(value, (list, tuple)):
            redacted[key] = [
                redact_dict(item) if isinstance(item, dict) else
                redact_value(item) if isinstance(item, str) else
                item
                for item in value
            ]
        else:
            redacted[key] = value

    return redacted
