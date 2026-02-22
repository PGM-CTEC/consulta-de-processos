# STORY-REM-044: SearchHistory Foreign Key

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-004
**Type:** Database
**Complexity:** 3 pts (S - 1 day)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Add foreign key constraint from search_history to processes table to maintain referential integrity.

## Acceptance Criteria

- [ ] Foreign key constraint added (search_history.process_id → processes.id)
- [ ] ON DELETE CASCADE configured
- [ ] Test: Delete process → search_history records deleted
- [ ] Test: Insert search_history with invalid process_id → constraint violation
- [ ] Migration script created and tested

## Technical Notes

```sql
-- SQLite migration
ALTER TABLE search_history
ADD CONSTRAINT fk_search_history_process
FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE;

-- Verify constraint
INSERT INTO search_history (process_id, searched_at)
VALUES (99999, NOW());  -- Should fail if process 99999 doesn't exist
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
