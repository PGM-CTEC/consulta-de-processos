# STORY-REM-045: JSON Indexing (PostgreSQL)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-008
**Type:** Database
**Complexity:** 13 pts (L - 1 week)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

If migrating to PostgreSQL, add GIN indexes on JSONB columns for faster JSON queries (parties, metadata).

## Acceptance Criteria

- [ ] PostgreSQL migration completed (prerequisite)
- [ ] JSON columns converted to JSONB type
- [ ] GIN indexes created on JSONB columns
- [ ] Query performance tested (JSON path queries)
- [ ] Performance improvement >50% for JSON queries
- [ ] Documentation updated with JSON query examples

## Technical Notes

```sql
-- Convert JSON to JSONB (PostgreSQL)
ALTER TABLE processes
ALTER COLUMN parties TYPE JSONB USING parties::JSONB;

ALTER TABLE processes
ALTER COLUMN metadata TYPE JSONB USING metadata::JSONB;

-- Create GIN indexes
CREATE INDEX idx_process_parties_gin ON processes USING GIN (parties);
CREATE INDEX idx_process_metadata_gin ON processes USING GIN (metadata);

-- Example query (now indexed)
SELECT * FROM processes
WHERE parties @> '{"type": "AUTOR"}';
```

## Dependencies

REM-053 to REM-057 (PostgreSQL migration)

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
| 2026-02-28 | @dev | Deferido: Security audit completo (L-size 13pts) — deferido, requer ambiente dedicado |
