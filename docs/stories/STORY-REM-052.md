# STORY-REM-052: Input Sanitization

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Related to SEC-ARCH-005
**Type:** Security
**Complexity:** 5 pts (M - 1 day)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Implement comprehensive input sanitization for all user inputs to prevent injection attacks (SQL injection, XSS, command injection).

## Acceptance Criteria

- [x] Input validation library integrated (Pydantic for backend)
- [x] All API endpoints validate input schemas
- [x] SQL injection prevention verified (parameterized queries)
- [x] File upload sanitization (type check, size limit)
- [x] Error messages don't leak sensitive info
- [x] Security test suite passes

## Technical Notes

Use Pydantic BaseModel for input validation with regex patterns for CNJ numbers. Ensure all database queries use parameterized queries via SQLAlchemy ORM. Validate file uploads for allowed extensions and size limits.

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

- `backend/schemas.py` — Pydantic models com field_validator para todos os inputs
- `backend/validators.py` — ProcessNumberValidator com regex CNJ e sanitização
- `backend/utils/redact.py` — Redação de dados sensíveis

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Verificado: Pydantic + validators.py já implementam sanitização completa, SQL injection prevenido por SQLAlchemy ORM |
