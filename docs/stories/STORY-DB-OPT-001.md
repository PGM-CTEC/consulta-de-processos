# STORY-DB-OPT-001: Database Query Optimization

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-OPTIMIZATION-001
**Type:** Database
**Complexity:** 7 pts (L - 2-3 days)
**Priority:** HIGH
**Assignee:** Data Engineer / Backend Developer
**Status:** Ready
**Sprint:** Sprint 4

## Description

Implement database query optimization, analyze query performance, provide index recommendations, optimize connection pooling, and establish query caching strategy to improve overall database efficiency.

## Acceptance Criteria

- [ ] Query performance analysis (EXPLAIN plans)
- [ ] Index recommendations (7+ indexes)
- [ ] Connection pool optimization
- [ ] N+1 query detection and fixes
- [ ] Batch operation optimization (100 items/batch)
- [ ] Query caching with TTL (5min default)
- [ ] Cache hit/miss tracking
- [ ] Automatic cache expiration
- [ ] Database optimizer module
- [ ] Performance comparison before/after

## Technical Notes

### DatabaseOptimizer

```python
# backend/database_optimizations.py

class DatabaseOptimizer:
    @staticmethod
    def analyze_query_performance(query: str, db) -> dict:
        """Use EXPLAIN to analyze query performance"""
        # Returns: full_table_scan, rows_scanned, execution_time

    @staticmethod
    def get_index_recommendations(db) -> List[str]:
        """Recommend indexes for common query patterns"""
        # Returns: List of CREATE INDEX statements

    @staticmethod
    def optimize_connection_pool() -> dict:
        """Recommended pool settings"""
        return {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "pool_pre_ping": True
        }
```

### QueryCache

```python
class QueryCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str):
        """Get cached result"""

    def set(self, key: str, value: Any):
        """Cache result with TTL"""

    def invalidate(self, key: str):
        """Remove cached entry"""

    def get_stats(self) -> dict:
        """Returns hit/miss statistics"""

# Global instance
_query_cache = QueryCache()
def get_query_cache() -> QueryCache:
    return _query_cache
```

### Recommended Indexes

```sql
-- Primary lookup
CREATE UNIQUE INDEX idx_processes_number ON processes(numero_cnj);

-- Filtering
CREATE INDEX idx_processes_tribunal ON processes(tribunal_name);
CREATE INDEX idx_processes_phase ON processes(fase_processual);

-- Relationships
CREATE INDEX idx_movements_process ON movimentacoes(processo_id);
CREATE INDEX idx_movements_date ON movimentacoes(data_movimentacao);

-- Analytics
CREATE INDEX idx_search_history_number ON historico_busca(numero_cnj);
CREATE INDEX idx_search_history_searched_at ON historico_busca(data_busca);
```

### Batch Optimization

```python
class BatchQueryOptimizer:
    @staticmethod
    def batch_insert(items: List[dict], batch_size: int = 100) -> dict:
        """Insert items in batches (100 items per batch)"""
        # Returns: inserted_count, failed_count, timing

    @staticmethod
    def batch_update(items: List[dict], batch_size: int = 100) -> dict:
        """Update items in batches"""
```

## Dependencies

None (can run independently)

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
| 2026-02-23 | @pm | Story created for Sprint 4 |
