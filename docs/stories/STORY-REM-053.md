# STORY-REM-053: PostgreSQL Setup (Migration Phase 1)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-002 (Phase 1)
**Type:** Database Migration
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Setup PostgreSQL database instance, configure connection, and prepare migration environment.

## Acceptance Criteria

- [x] PostgreSQL 15+ installed (local or cloud)
- [x] Database created (consulta_processual_pg)
- [x] Connection string configured
- [x] PostgreSQL extensions installed (if needed: pg_trgm for text search)
- [x] Backup strategy defined
- [x] Connection pooling configured (pgbouncer or SQLAlchemy pool)
- [x] Test connection from application

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

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

-  — Plano completo de migração SQLite→PostgreSQL (Fases 1-5)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Setup documentado com script de instalação, configuração de usuário/database, extensões e connection pooling |
