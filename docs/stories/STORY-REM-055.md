# STORY-REM-055: Data Migration Script (Migration Phase 3)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-002 (Phase 3)
**Type:** Database Migration
**Complexity:** 13 pts (L - 1 week)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Create and execute data migration script to transfer all data from SQLite to PostgreSQL with validation.

## Acceptance Criteria

- [ ] Migration script created (Python or SQL)
- [ ] Batch processing implemented (avoid memory issues)
- [ ] Data transformation handled (JSON to JSONB)
- [ ] Progress logging implemented
- [ ] Dry-run mode available
- [ ] Rollback plan documented
- [ ] Data validation: row counts match
- [ ] Data validation: sample records match
- [ ] Performance acceptable (<2 hours for 100k records)

## Technical Notes

```python
# migration_script.py
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch

BATCH_SIZE = 1000

# Connect to both databases
sqlite_conn = sqlite3.connect('consulta_processual.db')
pg_conn = psycopg2.connect(DATABASE_URL)

# Migrate processes table
sqlite_cursor = sqlite_conn.cursor()
pg_cursor = pg_conn.cursor()

offset = 0
while True:
    # Fetch batch from SQLite
    sqlite_cursor.execute(
        "SELECT * FROM processes LIMIT ? OFFSET ?",
        (BATCH_SIZE, offset)
    )
    rows = sqlite_cursor.fetchall()

    if not rows:
        break

    # Insert into PostgreSQL
    execute_batch(
        pg_cursor,
        "INSERT INTO processes (id, number, phase, court, parties, metadata, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        rows
    )
    pg_conn.commit()

    offset += BATCH_SIZE
    print(f"Migrated {offset} processes...")

# Validation
sqlite_count = sqlite_cursor.execute("SELECT COUNT(*) FROM processes").fetchone()[0]
pg_count = pg_cursor.execute("SELECT COUNT(*) FROM processes").fetchone()[0]

assert sqlite_count == pg_count, f"Row count mismatch: SQLite {sqlite_count}, PostgreSQL {pg_count}"
print(f"✅ Migration complete: {pg_count} processes migrated")
```

## Dependencies

REM-054 (schema translation)

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
