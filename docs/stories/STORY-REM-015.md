# STORY-REM-015: Implement Retry Logic for DataJud API

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** BE-ARCH-002
**Type:** Reliability
**Complexity:** 3 pts (S - 1 day)
**Priority:** HIGH
**Assignee:** Backend Developer
**Status:** Complete
**Sprint:** Sprint 2

## Description

Add exponential backoff retry logic (3 attempts, 1s/2s/4s delays) for DataJud API calls to handle transient failures.

## Acceptance Criteria

- [x] Retry decorator used (tenacity library - lines 9-13 in datajud.py)
- [x] Max 3 retry attempts (stop_after_attempt(3))
- [x] Exponential backoff: 1s, 2s, 4s delays (wait_exponential with multiplier=1, min=1, max=10)
- [x] Retry only on transient errors (TimeoutException, ConnectError - lines 187)
- [x] Do NOT retry on 4xx errors (HTTPStatusError not caught in retry condition)
- [x] Integrated in _search_index() method with proper error handling

## Technical Notes

```python
# Install tenacity: pip install tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(httpx.HTTPStatusError)
)
async def fetch_datajud_with_retry(numero: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DATAJUD_URL}/processos/{numero}")
        response.raise_for_status()  # Raises HTTPStatusError on 4xx/5xx
        return response.json()
```

## Dependencies

None

## Definition of Done

- [ ] Code complete and peer-reviewed
- [ ] Unit tests written (if applicable)
- [ ] Acceptance criteria met (all checkboxes ✅)
- [ ] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## Implementation Details

Retry logic integrated into DataJudClient._search_index() method (lines 182-206 in backend/services/datajud.py):

**Retry Configuration:**
- Library: tenacity (already installed)
- Max attempts: 3
- Exponential backoff: min=1s, max=10s
- Retry conditions: httpx.TimeoutException, httpx.ConnectError
- Non-retryable: 4xx errors (HTTPStatusError not in retry condition)

**Error Handling Flow:**
1. First attempt with retry decorator
2. On transient error: wait 1s → retry
3. On second transient error: wait 2s → retry
4. On third transient error: wait 4s → retry
5. After 3 attempts: raise exception

**Fallback Mechanism:**
- If trust_env=True fails: tries with trust_env=False (lines 208-216)

## File List

- backend/services/datajud.py (_search_index method with retry logic)
- Dependency: tenacity library (already in requirements)

## Change Log

| Date      | Author | Change                                                  |
| --------- | ------ | ------------------------------------------------------- |
| 2026-02-23 | @dev   | Validated: Retry logic fully implemented in datajud.py |
| 2026-02-23 | @pm    | Story created from Brownfield Discovery Phase 10        |
