# STORY-REM-025: Database Migrations with Alembic

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-013
**Type:** Database
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Done
**Sprint:** Sprint 9

## Description

Setup Alembic for database schema versioning and automated migrations, preventing manual SQL errors.

## Acceptance Criteria

- [x] Alembic installed (`pip install alembic==1.13.1`)
- [x] `alembic init alembic` executed
- [x] alembic.ini configured (sqlalchemy.url = sqlite:///./consulta_processual.db)
- [x] Initial migration created: `alembic revision --autogenerate -m "initial schema"`
- [x] Migration applied: `alembic upgrade head`
- [x] Rollback tested: `alembic downgrade -1` && `alembic upgrade head`
- [x] README.md created with migration commands

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

- `alembic.ini` — Config Alembic (sqlite URL)
- `alembic/env.py` — env configurado com Base, render_as_batch=True
- `alembic/script.py.mako` — template de migration
- `alembic/versions/2f1ecee8db76_initial_schema.py` — migration inicial
- `backend/requirements.txt` — adicionado alembic==1.13.1
- `backend/models.py` — adicionado Index import + __table_args__ em Movement

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-27 | @dev | Implemented Alembic setup with render_as_batch for SQLite [Sprint 9] |
