# STORY-REM-061: Error Messages Improvement

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Various LOW priority debits
**Type:** UX
**Complexity:** 3 pts (S - 1 day)
**Priority:** LOW
**Assignee:** Frontend Developer / Backend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Improve error messages throughout the application to be more user-friendly and actionable.

## Acceptance Criteria

- [x] All error messages reviewed
- [x] Technical errors translated to user-friendly messages
- [x] Error messages suggest next steps
- [x] Error codes standardized
- [x] i18n support for error messages (future-ready)
- [x] No stack traces shown to end users

## Technical Notes

**Error message guidelines:**
- ❌ "Database error: Foreign key constraint failed"
- ✅ "Unable to delete this item because it's being used elsewhere. Please remove dependencies first."

- ❌ "HTTP 500 Internal Server Error"
- ✅ "We're experiencing technical difficulties. Please try again in a few minutes."

- ❌ "ValidationError: cnj must match regex"
- ✅ "CNJ number must be exactly 20 digits. Example: 12345678901234567890"

**Implementation:**
```python
# backend/exceptions.py
class UserFriendlyException(Exception):
    def __init__(self, user_message: str, technical_details: str = None):
        self.user_message = user_message
        self.technical_details = technical_details
        super().__init__(user_message)

# Usage
raise UserFriendlyException(
    user_message="Unable to find process. Please check the CNJ number and try again.",
    technical_details="ProcessNotFoundError: No process with number 12345678901234567890"
)
```

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

- `frontend/src/lib/errorMessages.js` — Constantes ERROR_MESSAGES + getFriendlyErrorMessage(error)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Implementado: errorMessages.js com mensagens amigáveis para todos os erros HTTP comuns |
