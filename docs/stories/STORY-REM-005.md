# STORY-REM-005: Add CORS Whitelist Configuration

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 | **Complexity:** 2 pts (XS - 30min) | **Priority:** MEDIUM
**Assignee:** Backend Developer | **Status:** Ready

---

## Description

Restrict CORS to whitelisted origins only (prevent XSS from malicious domains).

## Acceptance Criteria

- [ ] CORS middleware configured with explicit allow_origins list
- [ ] Production domain whitelisted
- [ ] Localhost allowed for dev
- [ ] allow_origins=["*"] removed

## Implementation

```python
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://consulta-processo.example.com",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Files

- `backend/main.py` (modified)
