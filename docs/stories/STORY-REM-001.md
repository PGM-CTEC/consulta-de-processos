# STORY-REM-001: Add Missing Database Indexes

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 (Remediation)
**Type:** Technical Debt / Performance
**Complexity:** 2 pts (XS - 30 min)
**Priority:** CRITICAL
**Assignee:** Data Engineer
**Status:** Ready

---

## Description

Create 3 missing indexes on Movement table to achieve **20-100x query speedup** (100-500ms → <5ms).

---

## Acceptance Criteria

- [ ] CREATE INDEX idx_movement_process_date ON movements(process_id, date DESC)
- [ ] CREATE INDEX idx_movement_code ON movements(code)
- [ ] CREATE INDEX idx_movement_date ON movements(date DESC)
- [ ] EXPLAIN QUERY PLAN shows "SEARCH TABLE movements USING INDEX"
- [ ] Performance test: latency <5ms

---

## SQL

```sql
CREATE INDEX IF NOT EXISTS idx_movement_process_date ON movements(process_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_movement_code ON movements(code);
CREATE INDEX IF NOT EXISTS idx_movement_date ON movements(date DESC);

EXPLAIN QUERY PLAN SELECT * FROM movements WHERE process_id = 123 ORDER BY date DESC;
```

---

## Implementation

1. Backup: `cp consulta_processual.db consulta_processual.db.backup`
2. Execute CREATE INDEX statements
3. Verify with EXPLAIN QUERY PLAN
4. Performance test

---

## Files

- `consulta_processual.db` (schema only)

---

## Dev Tasks

- [ ] Create indexes
- [ ] Verify query plans
- [ ] Performance test
