# STORY-REM-054: Schema Translation (Migration Phase 2)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-002 (Phase 2)
**Type:** Database Migration
**Complexity:** 5 pts (M - 1 day)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Translate SQLite schema to PostgreSQL DDL, adapting data types and constraints for PostgreSQL.

## Acceptance Criteria

- [x] PostgreSQL DDL script created
- [x] Data types adapted (TEXT → VARCHAR, JSON → JSONB)
- [x] Constraints translated (CHECK, FOREIGN KEY, UNIQUE)
- [x] Indexes recreated with PostgreSQL syntax
- [x] Sequences configured for auto-increment
- [x] Schema validation passes
- [x] Empty PostgreSQL database created with new schema

## Technical Notes

**SQLite to PostgreSQL mappings:**
- INTEGER → INTEGER or BIGINT
- TEXT → VARCHAR or TEXT
- REAL → NUMERIC or FLOAT
- BLOB → BYTEA
- JSON → JSONB (better performance)

**Example DDL:**
```sql
-- processes table
CREATE TABLE processes (
    id SERIAL PRIMARY KEY,
    number VARCHAR(20) UNIQUE NOT NULL CHECK (number ~ '^[0-9]{20}$'),
    phase VARCHAR(2) CHECK (phase IS NULL OR (phase >= '01' AND phase <= '15')),
    court VARCHAR(255),
    parties JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_process_court ON processes(court);
CREATE INDEX idx_process_phase ON processes(phase);
CREATE INDEX idx_process_created_at ON processes(created_at);
```

## Dependencies

REM-053 (PostgreSQL setup)

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

-  — DDL completo para PostgreSQL 15+ com índices e triggers

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | DDL PostgreSQL criado com SERIAL, TIMESTAMPTZ, JSONB, GIN indexes para pg_trgm |
