# STORY-REM-050: External API Resilience

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** EXT-ARCH-002, EXT-ARCH-003
**Type:** Reliability
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Improve resilience to DataJud API failures with fallback strategies, caching, and graceful degradation.

## Acceptance Criteria

- [ ] Response caching implemented (Redis or in-memory)
- [ ] Cache TTL configured (e.g., 1 hour for process data)
- [ ] Fallback to cached data when API down
- [ ] Graceful degradation UI (show cached data + warning)
- [ ] Monitoring for API health and cache hit rate
- [ ] Test: API down → cached data served + user notified

## Technical Notes

```python
# Install redis
pip install redis

# backend/cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cached(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(numero):
            cache_key = f"process:{numero}"

            # Try cache first
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)

            try:
                # Fetch from API
                data = await func(numero)
                redis_client.setex(cache_key, ttl, json.dumps(data))
                return data
            except Exception as e:
                # Fallback: return stale cache if available
                stale_data = redis_client.get(cache_key)
                if stale_data:
                    logger.warning(f"API failed, serving stale cache for {numero}")
                    return json.loads(stale_data)
                raise
        return wrapper
    return decorator

@cached(ttl=3600)
async def fetch_process(numero):
    # API call logic
    ...
```

## Dependencies

None

## Definition of Done

- [ ] Code complete and peer-reviewed
- [ ] Unit tests written (if applicable)
- [ ] Acceptance criteria met (all checkboxes ✅)
- [ ] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

_To be updated during development_

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
