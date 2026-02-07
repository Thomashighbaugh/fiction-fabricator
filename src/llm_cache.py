"""
llm_cache.py - LRU cache implementation for LLM responses.

Caches LLM responses to avoid repeated API calls with identical prompts.
"""
import hashlib
import json
import time
from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


class LRUCache:
    """
    Least Recently Used (LRU) cache with time-based expiration.

    Args:
        max_size: Maximum number of items to cache (default: 100)
        ttl: Time-to-live in seconds, None for no expiration (default: 3600)
    """

    def __init__(self, max_size: int = 100, ttl: int | None = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate cache key from function arguments."""
        # Convert args and kwargs to JSON string, then hash
        key_data = {"args": args, "kwargs": kwargs}
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry has expired."""
        if self.ttl is None:
            return False
        return (time.time() - timestamp) > self.ttl

    def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key not in self.cache:
            self.misses += 1
            return None

        value, timestamp = self.cache[key]

        if self._is_expired(timestamp):
            del self.cache[key]
            self.misses += 1
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1
        return value

    def set(self, key: str, value: Any) -> None:
        """Add or update cache entry."""
        if key in self.cache:
            # Update existing entry
            self.cache[key] = (value, time.time())
            self.cache.move_to_end(key)
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Remove least recently used item
                self.cache.popitem(last=False)
            self.cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> dict[str, int | float]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate_percent": hit_rate,
            "size": len(self.cache),
            "max_size": self.max_size,
        }


def lru_cache(max_size: int = 100, ttl: int | None = 3600):
    """
    Decorator to add LRU caching to a function.

    Example:
        @lru_cache(max_size=50, ttl=1800)
        def expensive_llm_call(prompt: str) -> str:
            return llm.get_response(prompt)

    Args:
        max_size: Maximum number of cached responses
        ttl: Cache expiration time in seconds (None for no expiration)
    """
    cache = LRUCache(max_size=max_size, ttl=ttl)

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Generate cache key
            cache_key = cache._generate_key(*args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        # Attach cache instance for manual control
        wrapper.cache = cache  # type: ignore
        return wrapper

    return decorator


def cache_key_from_prompt(prompt: str, task_description: str = "") -> str:
    """
    Generate a consistent cache key from prompt and task description.

    Useful for manual cache management.
    """
    key_data = f"{prompt}::{task_description}"
    return hashlib.sha256(key_data.encode()).hexdigest()
