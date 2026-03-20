"""
Design patterns for backend services.

Includes:
- Circuit Breaker: Protection against cascading failures
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerException,
    CircuitState,
    CircuitBreakerRegistry,
    get_registry,
    create_breaker,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerException",
    "CircuitState",
    "CircuitBreakerRegistry",
    "get_registry",
    "create_breaker",
]
