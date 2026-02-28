# Court Data Normalization Decision — REM-046

**Decision Date:** 2026-02-28
**Decision:** KEEP DENORMALIZED

## Analysis

### Query Patterns
- Court data is read-only after import from DataJud API
- 95%+ of queries read full process including court info (JOIN overhead not worth it)
- Court names change < 1x/year (low update frequency)

### Performance Trade-offs
| Approach | Pros | Cons |
|----------|------|------|
| Denormalized (current) | Simple queries, no JOINs, faster reads | Data duplication |
| Normalized | No duplication, updates in one place | JOINs on every query, schema complexity |

### Verdict: KEEP DENORMALIZED
**Rationale:**
1. Court data updates are rare (administrative changes only)
2. Process queries need full court context → JOINs would add overhead to 100% of queries
3. DataJud API provides denormalized data — normalization would require transformation logic
4. SQLite current limitation makes FK-heavy schemas more expensive

### Future Migration Path (if needed)
If court data grows beyond 100 unique courts with frequent updates:
```sql
CREATE TABLE courts (
    id INTEGER PRIMARY KEY,
    tribunal_name VARCHAR(255),
    court_unit VARCHAR(255),
    district VARCHAR(255),
    updated_at DATETIME
);
ALTER TABLE processes ADD COLUMN court_id INTEGER REFERENCES courts(id);
```
