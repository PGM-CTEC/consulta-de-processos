# STORY-REM-025: Database Migrations with Alembic

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-013
**Type:** Database
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 4

## Description

Setup Alembic for database schema versioning and automated migrations, preventing manual SQL errors.

## Acceptance Criteria

- [ ] Alembic installed (`pip install alembic`)
- [ ] `alembic init alembic` executed
- [ ] alembic.ini configured (sqlalchemy.url)
- [ ] Initial migration created: `alembic revision --autogenerate -m "initial schema"`
- [ ] Migration applied: `alembic upgrade head`
- [ ] Rollback tested: `alembic downgrade -1`
- [ ] README.md updated with migration commands

## Technical Notes

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Edit alembic.ini
# sqlalchemy.url = sqlite:///consulta_processual.db

# Auto-generate migration from models
alembic revision --autogenerate -m "initial schema"

# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View history
alembic history
```

**alembic/env.py:**
```python
from backend.models import Base  # Import SQLAlchemy Base
target_metadata = Base.metadata
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
