"""
retry_utils.py - Improved retry logic with exponential backoff and jitter.

Prevents thundering herd problem by adding randomized jitter to backoff delays.
"""

import random
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def exponential_backoff_with_jitter(
    base_delay: float, attempt: int, max_delay: float = 60.0, jitter: bool = True
) -> float:
    """
    Calculate delay with exponential backoff and optional jitter.

    Args:
        base_delay: Base delay in seconds (e.g., 2.0)
        attempt: Current attempt number (0-indexed)
        max_delay: Maximum delay cap in seconds
        jitter: Whether to add randomized jitter

    Returns:
        Delay in seconds with exponential backoff and jitter

    Example:
        attempt 0: 2s (+ jitter)
        attempt 1: 4s (+ jitter)
        attempt 2: 8s (+ jitter)
        attempt 3: 16s (+ jitter)
    """
    # Calculate exponential delay
    delay = min(base_delay * (2**attempt), max_delay)

    if jitter:
        # Add full jitter: random value between 0 and delay
        # This prevents thundering herd when many requests fail simultaneously
        delay = random.uniform(0, delay)

    return delay


def decorrelated_jitter_backoff(
    base_delay: float, attempt: int, max_delay: float = 60.0, previous_delay: float = 0.0
) -> float:
    """
    Decorrelated jitter backoff strategy (AWS recommendation).

    More aggressive than full jitter, better for high-load scenarios.

    Args:
        base_delay: Base delay in seconds
        attempt: Current attempt number
        max_delay: Maximum delay cap
        previous_delay: Delay from previous attempt

    Returns:
        Delay in seconds with decorrelated jitter
    """
    if attempt == 0:
        return random.uniform(0, base_delay)

    # Decorrelated jitter: random between base_delay and 3x previous delay
    temp = random.uniform(base_delay, previous_delay * 3)
    return min(temp, max_delay)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    backoff_strategy: str = "exponential",
    expected_exceptions: tuple[type[Exception], ...] = (Exception,),
):
    """
    Decorator to retry function with exponential backoff and jitter.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for backoff
        max_delay: Maximum delay cap in seconds
        jitter: Whether to add randomized jitter
        backoff_strategy: "exponential" or "decorrelated"
        expected_exceptions: Exception types to catch and retry

    Example:
        @retry_with_backoff(max_retries=5, base_delay=1.0, jitter=True)
        def flaky_api_call():
            # Might fail with transient errors
            pass
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None
            previous_delay = 0.0

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except expected_exceptions as e:
                    last_exception = e

                    if attempt >= max_retries - 1:
                        # Last attempt, re-raise
                        raise

                    # Calculate delay based on strategy
                    if backoff_strategy == "decorrelated":
                        delay = decorrelated_jitter_backoff(
                            base_delay, attempt, max_delay, previous_delay
                        )
                        previous_delay = delay
                    else:  # exponential
                        delay = exponential_backoff_with_jitter(
                            base_delay, attempt, max_delay, jitter
                        )

                    time.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic failed unexpectedly")

        return wrapper

    return decorator


class RetryableError(Exception):
    """Base exception for errors that should trigger retry."""

    pass


class NonRetryableError(Exception):
    """Exception for errors that should NOT trigger retry."""

    pass
