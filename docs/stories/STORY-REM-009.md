# STORY-REM-009: Add CNJ Number CHECK Constraint

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-007
**Type:** Database
**Complexity:** 2 pts (XS - 15 min)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 1

## Description

Add CHECK constraint to processes.number column to validate CNJ format (20 numeric digits only).

## Acceptance Criteria

- [ ] CHECK constraint added: `LENGTH(number) = 20 AND number GLOB '[0-9]*'`
- [ ] Test: INSERT with number='123' → CHECK constraint failed
- [ ] Test: INSERT with number='ABC12345678901234567' → CHECK constraint failed
- [ ] Test: INSERT with number='12345678901234567890' → Success

## Technical Notes

```sql
-- SQLite: Same table recreation pattern as DB-006
CREATE TABLE processes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL
        CHECK (LENGTH(number) = 20 AND number GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    ...
);
```

**PostgreSQL version (simpler):**
```sql
ALTER TABLE processes
ADD CONSTRAINT check_cnj_format
CHECK (number ~ '^[0-9]{20}$');
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
