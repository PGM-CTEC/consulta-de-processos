# STORY-REM-006: Remove OpenRouter Dead Code

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 | **Complexity:** 2 pts (XS - 30min) | **Priority:** MEDIUM
**Assignee:** Backend Developer | **Status:** Ready

---

## Description

Delete unused OpenRouter configuration (legacy code).

## Acceptance Criteria

- [ ] OPENROUTER_API_KEY removed from `.env.example`
- [ ] OpenRouterConfig class deleted from `backend/config.py`
- [ ] No references to "openrouter" remain
- [ ] Tests still pass

## Implementation

```bash
grep -r "openrouter" backend/
# Delete references found
```

## Files

- `backend/config.py` (modified)
- `.env.example` (modified)
