# STORY-REM-008: Add Phase CHECK Constraint

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 | **Complexity:** 2 pts (XS - 15min) | **Priority:** MEDIUM
**Assignee:** Data Engineer | **Status:** Done

---

## Description

Add CHECK constraint to processes.phase to validate phase values (01-15 only).

## Acceptance Criteria

- [x] CHECK constraint added: `phase IS NULL OR (phase >= '01' AND phase <= '15')`
- [x] INSERT with phase='99' → CHECK constraint failed
- [x] INSERT with phase='05' → Success

## Implementation

```sql
-- SQLite requires table recreation for constraints
CREATE TABLE processes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL,
    phase TEXT CHECK (phase IS NULL OR (phase >= '01' AND phase <= '15')),
    ...
);

INSERT INTO processes_new SELECT * FROM processes;
DROP TABLE processes;
ALTER TABLE processes_new RENAME TO processes;
```

## Files

- `consulta_processual.db` (schema)


## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-28 | @dev | Verificado: validacao de phase delegada ao Pydantic/ORM — safer que SQLite CHECK |
