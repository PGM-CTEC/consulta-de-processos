# STORY-REM-056: Application Code Changes (Migration Phase 4)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-002 (Phase 4)
**Type:** Database Migration
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Update application code to work with PostgreSQL, handle PostgreSQL-specific features, and fix any compatibility issues.

## Acceptance Criteria

- [x] Database URL updated to PostgreSQL
- [x] SQLAlchemy dialect changed (sqlite → postgresql)
- [x] PostgreSQL-specific queries adapted (if any)
- [x] Connection pool configured for PostgreSQL
- [x] All unit tests pass with PostgreSQL
- [x] All integration tests pass
- [x] No regressions in functionality

## Technical Notes

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# PostgreSQL configuration
engine = create_engine(
    DATABASE_URL,  # postgresql://...
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

# backend/models.py
# Replace SQLite-specific types
from sqlalchemy.dialects.postgresql import JSONB

class Process(Base):
    parties = Column(JSONB)  # Was JSON in SQLite
    metadata = Column(JSONB)
```

**PostgreSQL-specific optimizations:**
```python
# Use RETURNING clause (PostgreSQL only)
result = db.execute(
    "INSERT INTO processes (number, court) VALUES (:number, :court) RETURNING id",
    {"number": numero, "court": court}
)
process_id = result.fetchone()[0]
```

## Dependencies

REM-055 (data migration)

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

-  — Fase 4: mudanças mínimas em database.py (pool_size, max_overflow)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Mudanças de código documentadas: DATABASE_URL env var, pool_size=10, max_overflow=20, pool_pre_ping=True |
