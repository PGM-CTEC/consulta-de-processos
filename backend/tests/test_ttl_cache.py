"""Tests for in-memory TTL cache — REM-050: External API Resilience."""

import time
from backend.utils.ttl_cache import TTLCache


def test_set_and_get():
    """Basic set/get returns stored value."""
    cache = TTLCache(ttl=60)
    cache.set("key1", {"data": "value"})
    result = cache.get("key1")
    assert result == {"data": "value"}


def test_get_nonexistent_returns_none():
    """Missing key returns None."""
    cache = TTLCache(ttl=60)
    assert cache.get("missing") is None


def test_expired_entry_returns_none():
    """Entry with past TTL is treated as missing."""
    cache = TTLCache(ttl=1)
    cache.set("key1", "value")
    # Manually expire it
    cache._store["key1"] = ("value", time.time() - 1)
    assert cache.get("key1") is None


def test_delete_removes_entry():
    """Delete removes a specific key."""
    cache = TTLCache(ttl=60)
    cache.set("key1", "value")
    cache.delete("key1")
    assert cache.get("key1") is None


def test_clear_empties_cache():
    """Clear removes all entries."""
    cache = TTLCache(ttl=60)
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    cache.clear()
    assert cache.size == 0


def test_max_size_evicts_oldest():
    """When at capacity, oldest entry is evicted."""
    cache = TTLCache(ttl=60, max_size=2)
    cache.set("first", "v1")
    time.sleep(0.01)  # ensure different timestamps
    cache.set("second", "v2")
    cache.set("third", "v3")  # should evict "first"
    assert cache.get("first") is None
    assert cache.get("second") == "v2"
    assert cache.get("third") == "v3"


def test_size_counts_non_expired():
    """Size returns count of non-expired entries."""
    cache = TTLCache(ttl=60)
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    assert cache.size == 2
    # Expire one entry manually
    cache._store["k1"] = ("v1", time.time() - 1)
    assert cache.size == 1
