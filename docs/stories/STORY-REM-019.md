# STORY-REM-019: Refactor ProcessService (Decouple DataJud Adapter)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** BE-ARCH-001
**Type:** Architecture
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** HIGH
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 3

## Description

Extract DataJud API logic from ProcessService into separate adapter class using dependency injection for better testability.

## Acceptance Criteria

- [ ] DataJudAdapter class created (`backend/adapters/datajud_adapter.py`)
- [ ] ProcessService receives adapter via dependency injection
- [ ] Mock adapter created for unit tests
- [ ] All existing tests still pass
- [ ] No direct httpx calls in ProcessService (delegated to adapter)
- [ ] Code complexity reduced (Cyclomatic complexity <10)

## Technical Notes

```python
# backend/adapters/datajud_adapter.py
class DataJudAdapter:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    async def fetch_process(self, numero: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/processos/{numero}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return response.json()

# backend/services/process_service.py
class ProcessService:
    def __init__(self, datajud_adapter: DataJudAdapter):
        self.datajud = datajud_adapter

    async def get_or_update_process(self, numero: str):
        # Delegate to adapter
        data = await self.datajud.fetch_process(numero)
        # Process data
        return self._save_to_db(data)
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
