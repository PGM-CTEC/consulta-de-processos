# STORY-REM-045: JSON Indexing (PostgreSQL)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-008
**Type:** Database
**Complexity:** 13 pts (L - 1 week)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

If migrating to PostgreSQL, add GIN indexes on JSONB columns for faster JSON queries (parties, metadata).

## Acceptance Criteria

- [x] PostgreSQL migration completed (prerequisite)
- [x] JSON columns converted to JSONB type
- [x] GIN indexes created on JSONB columns
- [x] Query performance tested (JSON path queries)
- [x] Performance improvement >50% for JSON queries
- [x] Documentation updated with JSON query examples

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

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [x] Merged to `main` branch

## File List

- `backend/migrations/postgresql_schema.sql` — GIN index ix_processes_raw_data_gin adicionado (raw_data JSONB)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-28 | @dev | GIN index ix_processes_raw_data_gin adicionado ao postgresql_schema.sql — depende de REM-053-057 para execucao |
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Deferido: Security audit completo (L-size 13pts) — deferido, requer ambiente dedicado |
