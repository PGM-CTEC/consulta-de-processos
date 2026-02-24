# STORY-REM-009: Add CNJ Number CHECK Constraint

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 | **Complexity:** 2 pts (XS - 15min) | **Priority:** MEDIUM
**Assignee:** Data Engineer | **Status:** Ready

---

## Description

Add CHECK constraint to processes.number to validate CNJ format (20 digits only).

## Acceptance Criteria

- [ ] CHECK constraint: `LENGTH(number) = 20 AND number GLOB '[0-9]*'`
- [ ] INSERT with number='123' → FAIL
- [ ] INSERT with 20-digit number → SUCCESS

## Implementation

```sql
CREATE TABLE processes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL
        CHECK (LENGTH(number) = 20 AND number GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    ...
);
```

## Files

- `consulta_processual.db` (schema)
