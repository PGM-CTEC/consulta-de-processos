# STORY-REM-020: Implement Circuit Breaker for DataJud API

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** EXT-ARCH-001
**Type:** Reliability
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** HIGH
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 3

## Description

Add circuit breaker pattern (using pybreaker) to DataJud API calls to prevent cascading failures when DataJud is down.

## Acceptance Criteria

- [ ] pybreaker library installed (`pip install pybreaker`)
- [ ] CircuitBreaker configured: 5 failures → open, 60s timeout
- [ ] State transitions logged (closed → open → half-open → closed)
- [ ] Fast-fail when circuit open (don't wait for timeout)
- [ ] Test: 5 consecutive failures → circuit opens → 6th request fails immediately

## Technical Notes

```python
# Install: pip install pybreaker
from pybreaker import CircuitBreaker

# Configure circuit breaker
datajud_breaker = CircuitBreaker(
    fail_max=5,  # Open after 5 failures
    timeout_duration=60,  # Stay open for 60 seconds
    expected_exception=httpx.HTTPError
)

@datajud_breaker
async def fetch_datajud_with_breaker(numero: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DATAJUD_URL}/processos/{numero}")
        response.raise_for_status()
        return response.json()
```

**Circuit States:**
- **Closed:** Normal operation
- **Open:** Failures threshold reached, fail fast
- **Half-Open:** After timeout, test with 1 request

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
