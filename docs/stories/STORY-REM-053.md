# STORY-REM-053: PostgreSQL Setup (Migration Phase 1)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-002 (Phase 1)
**Type:** Database Migration
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Setup PostgreSQL database instance, configure connection, and prepare migration environment.

## Acceptance Criteria

- [ ] PostgreSQL 15+ installed (local or cloud)
- [ ] Database created (consulta_processual_pg)
- [ ] Connection string configured
- [ ] PostgreSQL extensions installed (if needed: pg_trgm for text search)
- [ ] Backup strategy defined
- [ ] Connection pooling configured (pgbouncer or SQLAlchemy pool)
- [ ] Test connection from application

## Technical Notes

```bash
# Install PostgreSQL
sudo apt install postgresql-15

# Create database
sudo -u postgres createdb consulta_processual_pg

# Create user
sudo -u postgres createuser consulta_user -P

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE consulta_processual_pg TO consulta_user;"
```

**Connection string:**
```python
DATABASE_URL = "postgresql://consulta_user:password@localhost:5432/consulta_processual_pg"
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
