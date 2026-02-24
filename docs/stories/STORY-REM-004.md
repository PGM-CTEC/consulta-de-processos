# STORY-REM-004: Add API Rate Limiting

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 | **Complexity:** 3 pts (S - 2h) | **Priority:** HIGH
**Assignee:** Backend Developer | **Status:** Ready

---

## Description

Implement SlowAPI rate limiter (100 requests/minute per IP) to prevent DoS attacks.

## Acceptance Criteria

- [ ] SlowAPI installed (`pip install slowapi`)
- [ ] Limiter configured (100/minute per IP)
- [ ] Applied to /api/search endpoint
- [ ] Applied to /api/bulk endpoint
- [ ] 429 response on rate limit exceeded
- [ ] Test: 101st request returns 429

## Implementation

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/search")
@limiter.limit("100/minute")
async def search_process(cnj: str):
    ...
```

## Files

- `backend/main.py` (modified)
