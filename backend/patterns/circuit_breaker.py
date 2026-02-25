"""
Circuit Breaker Pattern Implementation

Protects against cascading failures when calling external services (DataJud API).

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Too many failures, requests blocked immediately
- HALF_OPEN: Testing if service recovered, limited requests allowed

Usage:
    breaker = CircuitBreaker(
        failure_threshold=5,          # Failures before opening
        recovery_timeout=60,          # Seconds before half-open
        expected_exception=Exception
    )

    @breaker
    async def call_external_api():
        return await some_api_call()
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Optional, Callable, Any, Type
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, block requests
    HALF_OPEN = "half_open" # Testing recovery


class CircuitBreakerException(Exception):
    """Raised when circuit is open and request is blocked."""
    pass


class CircuitBreaker:
    """
    Circuit Breaker for protecting external service calls.

    Monitors call failures and temporarily blocks calls when failure rate is too high.
    Automatically attempts recovery after timeout.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception,
        name: Optional[str] = None
    ):
        """
        Initialize Circuit Breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to count as failure
            name: Name for logging and identification
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name or "CircuitBreaker"

        # State management
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._opened_at = None

        logger.info(f"Circuit breaker '{self.name}' initialized")

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self._state == CircuitState.OPEN

    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self._state == CircuitState.CLOSED

    def is_half_open(self) -> bool:
        """Check if circuit is half-open."""
        return self._state == CircuitState.HALF_OPEN

    def allow_request(self) -> bool:
        """
        Check if a new request should be allowed through.
        Handles OPEN -> HALF_OPEN transition automatically.
        Returns True if request can proceed, False if blocked.
        """
        if self._should_attempt_reset():
            logger.info(f"Circuit '{self.name}': Attempting recovery (half-open state)")
            self._state = CircuitState.HALF_OPEN
            self._failure_count = 0
        return self._state != CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if it's time to attempt recovery from open state."""
        if self._state != CircuitState.OPEN:
            return False

        if self._opened_at is None:
            return False

        elapsed = time.time() - self._opened_at
        return elapsed >= self.recovery_timeout

    def record_success(self):
        """Record a successful call."""
        logger.debug(f"Circuit '{self.name}': recording success (state={self._state})")

        if self._state == CircuitState.HALF_OPEN:
            # Successful call in half-open state - close circuit
            logger.info(f"Circuit '{self.name}': Service recovered, closing circuit")
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None

        elif self._state == CircuitState.CLOSED:
            # Normal successful call
            self._failure_count = 0
            self._success_count += 1

    def record_failure(self):
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        logger.warning(
            f"Circuit '{self.name}': recording failure "
            f"({self._failure_count}/{self.failure_threshold}, state={self._state})"
        )

        if self._state == CircuitState.HALF_OPEN:
            # Failure in half-open state - re-open circuit
            logger.warning(f"Circuit '{self.name}': Service still failing, re-opening circuit")
            self._open_circuit()

        elif self._state == CircuitState.CLOSED and self._failure_count >= self.failure_threshold:
            # Threshold exceeded - open circuit
            logger.error(
                f"Circuit '{self.name}': Failure threshold exceeded ({self._failure_count}/{self.failure_threshold}), "
                f"opening circuit for {self.recovery_timeout}s"
            )
            self._open_circuit()

    def _open_circuit(self):
        """Open the circuit."""
        self._state = CircuitState.OPEN
        self._opened_at = time.time()
        self._success_count = 0

    def try_call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Attempt to execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Returns:
            Function result if successful

        Raises:
            CircuitBreakerException: If circuit is open
            expected_exception: If function raises expected exception
        """
        # Check if circuit should transition to half-open
        if self._should_attempt_reset():
            logger.info(f"Circuit '{self.name}': Attempting recovery (half-open state)")
            self._state = CircuitState.HALF_OPEN
            self._failure_count = 0

        # Block if circuit is open
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerException(
                f"Circuit breaker '{self.name}' is OPEN. "
                f"Service unavailable, will retry in {self.recovery_timeout}s"
            )

        # Execute function with error handling
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except self.expected_exception as e:
            self.record_failure()
            raise

    async def try_call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Attempt to execute async function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Returns:
            Function result if successful

        Raises:
            CircuitBreakerException: If circuit is open
            expected_exception: If function raises expected exception
        """
        # Check if circuit should transition to half-open
        if self._should_attempt_reset():
            logger.info(f"Circuit '{self.name}': Attempting recovery (half-open state)")
            self._state = CircuitState.HALF_OPEN
            self._failure_count = 0

        # Block if circuit is open
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerException(
                f"Circuit breaker '{self.name}' is OPEN. "
                f"Service unavailable, will retry in {self.recovery_timeout}s"
            )

        # Execute async function with error handling
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except self.expected_exception as e:
            self.record_failure()
            raise

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator for protecting function calls.

        Usage:
            @circuit_breaker
            async def call_api():
                return await some_call()
        """
        # Detect if function is async
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self.try_call_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self.try_call(func, *args, **kwargs)
            return sync_wrapper

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CircuitBreaker(name='{self.name}', state={self._state.value}, "
            f"failures={self._failure_count}/{self.failure_threshold})"
        )


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    Useful when monitoring multiple external service calls.
    """

    def __init__(self):
        """Initialize registry."""
        self._breakers: dict[str, CircuitBreaker] = {}

    def register(self, name: str, breaker: CircuitBreaker) -> CircuitBreaker:
        """Register a circuit breaker."""
        self._breakers[name] = breaker
        logger.info(f"Registered circuit breaker: {name}")
        return breaker

    def create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ) -> CircuitBreaker:
        """Create and register a new circuit breaker."""
        breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            name=name
        )
        return self.register(name, breaker)

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self._breakers.get(name)

    def get_status(self) -> dict:
        """Get status of all registered circuit breakers."""
        return {
            name: {
                "state": breaker.state.value,
                "failures": breaker._failure_count,
                "threshold": breaker.failure_threshold
            }
            for name, breaker in self._breakers.items()
        }

    def __repr__(self) -> str:
        """String representation."""
        status = self.get_status()
        return f"CircuitBreakerRegistry({status})"


# Global registry instance
_registry = CircuitBreakerRegistry()


def get_registry() -> CircuitBreakerRegistry:
    """Get global circuit breaker registry."""
    return _registry


def create_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: Type[Exception] = Exception
) -> CircuitBreaker:
    """Create a circuit breaker in global registry."""
    return _registry.create(
        name=name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception
    )
