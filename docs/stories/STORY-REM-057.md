# STORY-REM-057: Cutover & Monitoring (Migration Phase 5)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-002 (Phase 5)
**Type:** Database Migration
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** DevOps Engineer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Execute production cutover from SQLite to PostgreSQL with monitoring, rollback plan, and post-migration validation.

## Acceptance Criteria

- [ ] Cutover plan documented (step-by-step)
- [ ] Maintenance window scheduled
- [ ] Application downtime minimized (<30 min)
- [ ] PostgreSQL monitoring configured (pg_stat_statements)
- [ ] Performance metrics baseline captured
- [ ] Rollback plan tested
- [ ] Post-cutover smoke tests pass
- [ ] No data loss verified

## Technical Notes

**Cutover Checklist:**
1. Enable maintenance mode (UI shows "Under maintenance")
2. Stop all background jobs
3. Take final SQLite backup
4. Run final incremental migration (catch any new data)
5. Validate data integrity
6. Switch DATABASE_URL to PostgreSQL
7. Restart application
8. Run smoke tests
9. Monitor for errors (30 min)
10. Disable maintenance mode

**Rollback Plan:**
1. Stop application
2. Restore SQLite backup
3. Switch DATABASE_URL back to SQLite
4. Restart application
5. Investigate issues before retry

**Monitoring:**
```sql
-- Enable query stats
CREATE EXTENSION pg_stat_statements;

-- Monitor slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Dependencies

REM-056 (application code changes)

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
