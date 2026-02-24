# STORY-REM-010: Configure Database Connection Pooling

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 | **Complexity:** 2 pts (XS - 30min) | **Priority:** MEDIUM
**Assignee:** Backend Developer | **Status:** Ready

---

## Description

Configure SQLAlchemy connection pool (StaticPool for SQLite) to prevent connection exhaustion.

## Acceptance Criteria

- [ ] Engine configured with `poolclass=StaticPool`
- [ ] `connect_args={'check_same_thread': False}` set
- [ ] Load test: 50 concurrent requests → No errors
- [ ] Documentation updated with future PostgreSQL config

## Implementation

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    'sqlite:///consulta_processual.db',
    poolclass=StaticPool,
    connect_args={'check_same_thread': False}
)

# Future PostgreSQL config
# engine = create_engine(
#     DATABASE_URL,
#     pool_size=10,
#     max_overflow=20,
#     pool_pre_ping=True,
#     pool_recycle=3600
# )
```

## Files

- `backend/database.py` (modified)
