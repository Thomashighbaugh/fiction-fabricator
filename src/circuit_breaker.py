"""
circuit_breaker.py - Circuit breaker pattern implementation for API reliability.

Prevents cascading failures by opening the circuit after a threshold of failures.
"""
import time
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, reject requests immediately
    - HALF_OPEN: After timeout, allow one test request

    Args:
        failure_threshold: Number of failures before opening circuit (default: 5)
        timeout: Seconds to wait before attempting half-open (default: 60)
        expected_exception: Exception type to catch (default: Exception)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute function with circuit breaker protection.

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Expected exceptions: If function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.timeout

    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


def circuit_breaker(
    failure_threshold: int = 5, timeout: int = 60, expected_exception: type[Exception] = Exception
):
    """
    Decorator to apply circuit breaker pattern to a function.

    Example:
        @circuit_breaker(failure_threshold=3, timeout=30)
        def call_external_api():
            # API call that might fail
            pass
    """
    breaker = CircuitBreaker(failure_threshold, timeout, expected_exception)

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return breaker.call(func, *args, **kwargs)

        # Attach breaker to function for manual control if needed
        wrapper.breaker = breaker  # type: ignore
        return wrapper

    return decorator
