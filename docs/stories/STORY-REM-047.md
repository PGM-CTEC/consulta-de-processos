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

- [ ] Versioning strategy selected (URL path /v1/, header, or query param)
- [ ] v1 API endpoints created
- [ ] Version negotiation documented
- [ ] Deprecation policy defined
- [ ] Example migration guide created
- [ ] OpenAPI spec updated with version info

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
