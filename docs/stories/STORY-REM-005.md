# STORY-REM-005: Add CORS Whitelist Configuration

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** SEC-ARCH-004
**Type:** Security
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 1

## Description

Audit and restrict CORS configuration to whitelist only trusted origins (prevent XSS from malicious domains).

## Acceptance Criteria

- [x] CORS middleware configured with explicit allow_origins list
- [x] Localhost allowed for development (http://localhost:5173)
- [x] allow_origins=["*"] removed (security risk) - VERIFIED
- [x] CORS middleware uses settings.allowed_origins_list (whitelist pattern)
- [x] Configuration: backend/config.py ALLOWED_ORIGINS property

## Technical Notes

```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://consulta-processo.example.com",  # Production
    "http://localhost:5173",  # Dev frontend
    "http://localhost:3000",  # Alternative dev port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
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
