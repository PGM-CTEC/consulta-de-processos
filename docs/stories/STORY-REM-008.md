# STORY-REM-008: Add Phase CHECK Constraint

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-006
**Type:** Database
**Complexity:** 2 pts (XS - 15 min)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 1

## Description

Add CHECK constraint to processes.phase column to validate phase values (01-15 only).

## Acceptance Criteria

- [ ] CHECK constraint added: `phase IS NULL OR (phase >= '01' AND phase <= '15')`
- [ ] Test: INSERT with phase='99' → CHECK constraint failed
- [ ] Test: INSERT with phase='05' → Success
- [ ] Test: INSERT with phase=NULL → Success (allowed)

## Technical Notes

```sql
-- SQLite: Recreate table with constraint
CREATE TABLE processes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL,
    phase TEXT CHECK (phase IS NULL OR (phase >= '01' AND phase <= '15')),
    ...
);

-- Copy data
INSERT INTO processes_new SELECT * FROM processes;

-- Drop old, rename new
DROP TABLE processes;
ALTER TABLE processes_new RENAME TO processes;

-- Recreate indexes
CREATE UNIQUE INDEX idx_process_number ON processes(number);
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
