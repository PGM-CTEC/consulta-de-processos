"""In-memory TTL cache for external API responses.

Story: REM-050 — External API Resilience
"""
import time
from threading import Lock
from typing import Any, Optional


class TTLCache:
    """Thread-safe in-memory cache with TTL expiration.

    Stores key→value pairs that automatically expire after `ttl` seconds.
    Useful as a fallback layer when the external DataJud API is unavailable.

    Example:
        cache = TTLCache(ttl=3600)
        cache.set("0001234-56.2020.8.19.0001", process_data)
        data = cache.get("0001234-56.2020.8.19.0001")  # None after TTL expires
    """

    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        """
        Args:
            ttl:      Time-to-live in seconds (default: 1 hour)
            max_size: Maximum number of items before evicting oldest
        """
        self.ttl = ttl
        self.max_size = max_size
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Return cached value if not expired, else None."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        """Store value with TTL expiration, evict oldest if at capacity."""
        with self._lock:
            if len(self._store) >= self.max_size and key not in self._store:
                # Evict the oldest entry
                oldest_key = min(self._store, key=lambda k: self._store[k][1])
                del self._store[oldest_key]
            self._store[key] = (value, time.time() + self.ttl)

    def delete(self, key: str) -> None:
        """Remove a specific key from cache."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from cache."""
        with self._lock:
            self._store.clear()

    @property
    def size(self) -> int:
        """Return current number of non-expired entries."""
        now = time.time()
        with self._lock:
            return sum(1 for _, (_, exp) in self._store.items() if exp > now)


# Module-level singleton for process data (1-hour TTL, max 500 entries)
process_cache = TTLCache(ttl=3600, max_size=500)
