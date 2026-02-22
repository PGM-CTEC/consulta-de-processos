# STORY-REM-010: Configure Database Connection Pooling

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-011
**Type:** Performance
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 1

## Description

Configure SQLAlchemy connection pool (StaticPool for SQLite) to prevent connection exhaustion under load.

## Acceptance Criteria

- [ ] Engine configured with `poolclass=StaticPool` (for SQLite)
- [ ] `connect_args={'check_same_thread': False}` set (for FastAPI async)
- [ ] Documentation updated with future PostgreSQL pool config
- [ ] Load test: 50 concurrent requests → No connection errors

## Technical Notes

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool  # For SQLite

# SQLite configuration
engine = create_engine(
    'sqlite:///consulta_processual.db',
    poolclass=StaticPool,  # Required for SQLite (single connection)
    connect_args={'check_same_thread': False}  # Required for FastAPI async
)

# PostgreSQL configuration (future - document only)
# engine = create_engine(
#     DATABASE_URL,
#     pool_size=10,  # 10 permanent connections
#     max_overflow=20,  # +20 temporary connections
#     pool_pre_ping=True,  # Health check before using connection
#     pool_recycle=3600  # Recycle connections after 1 hour
# )
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
