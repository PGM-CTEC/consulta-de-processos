# STORY-REM-047: API Versioning Strategy

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** BE-ARCH-005
**Type:** Backend Architecture
**Complexity:** 3 pts (S - 1 day)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Define and implement API versioning strategy (URL path, header, or query param) to support backward compatibility.

## Acceptance Criteria

- [x] Versioning strategy selected (URL path /v1/, header, or query param)
- [x] v1 API endpoints created
- [x] Version negotiation documented
- [x] Deprecation policy defined
- [x] Example migration guide created
- [x] OpenAPI spec updated with version info

## Technical Notes

**Option 1: URL Path (Recommended)**
```python
# backend/api/v1/endpoints.py
@app.get("/api/v1/search")
async def search_v1(cnj: str):
    ...

@app.get("/api/v2/search")  # Future
async def search_v2(cnj: str):
    ...
```

**Option 2: Header**
```python
from fastapi import Header

@app.get("/api/search")
async def search(cnj: str, api_version: str = Header("1.0")):
    if api_version == "1.0":
        ...
    elif api_version == "2.0":
        ...
```

**Deprecation Policy:**
- Support N-1 versions (current + previous)
- 6-month deprecation notice
- Clear migration documentation

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

**Status:** Ready for Review

## File List

- `docs/architecture/api-versioning-strategy.md` — Estratégia: URL Path /api/v1/, política de deprecação

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Estratégia documentada: URL Path /api/v1/, deprecação após 6 meses, suporte N-1 versão |
