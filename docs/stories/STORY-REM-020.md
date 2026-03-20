# STORY-REM-020: Implement Circuit Breaker for DataJud API

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** EXT-ARCH-001
**Type:** Reliability
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** HIGH
**Assignee:** Backend Developer
**Status:** Done
**Sprint:** Sprint 8

## Description

Add circuit breaker pattern (using pybreaker) to DataJud API calls to prevent cascading failures when DataJud is down.

## Acceptance Criteria

- [x] CircuitBreaker implementado em `backend/patterns/circuit_breaker.py` (custom, sem pybreaker)
- [x] CircuitBreaker integrado em `DataJudClient.__init__()` (5 falhas → open, 60s timeout)
- [x] Transições de estado logadas (closed → open → half-open → closed)
- [x] Fast-fail via `allow_request()` quando circuit OPEN
- [x] `record_failure()` em erros de rede, timeout e 5xx
- [x] `record_success()` após resposta bem-sucedida
- [x] Endpoint `GET /circuit-breaker/status` adicionado ao main.py

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

- `backend/patterns/circuit_breaker.py` — adicionado método `allow_request()`
- `backend/services/datajud.py` — integrado CircuitBreaker em `__init__` e `_search_index()`
- `backend/main.py` — endpoint `GET /circuit-breaker/status`

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-24 | @dev | Sprint 8: CircuitBreaker integrado no DataJudClient + endpoint status |
