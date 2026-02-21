# Story BR-003: Implement Async Bulk Processing

**Story ID:** BR-003
**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** 1 (Critical)
**Priority:** CRITICAL (Performance)
**Status:** Ready
**Type:** Feature / Performance
**Complexity:** 8 points
**Estimated Effort:** 8-12 hours (2-3 dias)

---

## Description

### Problem
Bulk search endpoint processa números CNJ **sequencialmente**, resultando em:
- **Current:** 50 processos × 3s cada = **150 segundos** (2.5 minutos)
- **Impact:** Poor UX, user frustration, feature abandonment
- **Scalability:** Doesn't scale to larger batches
- **Resource Waste:** CPU idle enquanto aguarda I/O (network)

### Root Cause
Backend `process_service.py` usa loop sequencial:
```python
async def bulk_search(self, numbers):
    results = []
    for numero in numbers:  # ❌ Sequential
        result = await self.get_or_update_process(numero)  # 3-5s cada
        results.append(result)
    return results
```

### Solution
Refatorar para **parallel processing** usando `asyncio.gather()`:
```python
async def bulk_search(self, numbers):
    tasks = [self.get_or_update_process(numero) for numero in numbers]
    results = await asyncio.gather(*tasks, return_exceptions=True)  # ✅ Parallel
    return results
```

### Business Value
- **User Experience:** 150s → <30s (80% improvement)
- **Feature Viability:** Bulk search torna-se usável
- **Retention:** Reduz abandonment rate
- **Scalability:** Prepara sistema para crescimento

---

## Acceptance Criteria

### Given
- Backend está em `/api/v1/processes/bulk` endpoint
- Frontend tem componente `BulkSearch` que chama endpoint
- DataJud API é o bottleneck (3-5s por request)

### When
- User submete 50 processos válidos para bulk search
- User submete 50 processos com alguns inválidos
- User submete 100 processos (máximo)
- Performance é medida em staging

### Then
- ✅ 50 processos completam em <30 segundos (vs 150s current)
- ✅ 50 processos com 5 inválidos: 45 successes + 5 failures (graceful degradation)
- ✅ 100 processos processam sem crash, memory <500MB
- ✅ Falhas individuais não bloqueiam batch
- ✅ Progress tracking mostra X/N complete
- ✅ Performance baseline: 80%+ improvement confirmado
- ✅ Error rate <2% (com eventual retry logic)

---

## Scope

### In Scope ✅

1. **Backend Refactoring**
   - Connection pooling em DataJudClient (httpx AsyncClient)
   - Semaphore para concurrency control (max 10 concurrent)
   - `asyncio.gather()` para parallel execution
   - Graceful error handling (failures don't block batch)
   - Response structure: successes + failures separated

2. **Configuration**
   - `BULK_CONCURRENCY_LIMIT` (default: 10)
   - `BULK_MAX_BATCH_SIZE` (default: 100)

3. **Frontend Progress Tracking**
   - Basic progress state (X / N complete)
   - Progress bar UI
   - Percentage calculation
   - Status messages

4. **Testing & Validation**
   - Unit tests (parallel execution, error handling)
   - Integration tests (10, 50, 100 item batches)
   - Performance benchmarks (sequential vs parallel)
   - Memory profiling (baseline + peak usage)

5. **Documentation**
   - Update README with performance improvements
   - Tuning guide (`docs/operations/performance-tuning.md`)
   - Architecture diagram (parallel processing)

### Out of Scope ❌

- Server-Sent Events (SSE) for real-time progress - Future story
- Exponential backoff retry logic - Future story
- Queue-based processing (Celery, etc) - Future story
- Caching layer - Future story
- Advanced concurrency patterns (actor model, etc) - Future

---

## Dependencies

### Prerequisite Stories
- None (independent)

### Blocking This Story
- None

### This Story Blocks
- Performance optimization stories (will have new baseline)
- Monitoring/alerting on bulk operations

### External Dependencies
- ✅ DataJud API stability (external, assumed working)
- ✅ SQLite transactional support (already present)
- ✅ Python asyncio (built-in)

---

## Technical Notes

### Architecture: Parallel Processing

```
User submits [50 numbers]
    ↓
FastAPI /processes/bulk endpoint
    ↓
ProcessService.bulk_search(numbers)
    ├─ Create 50 tasks (concurrent)
    ├─ Semaphore limita a 10 concurrent
    │  (prevents overwhelming DataJud API)
    │  (prevents overwhelming SQLite single-writer)
    ├─ asyncio.gather(*tasks) aguarda todos
    │  (parallel execution, network bound ~5s total vs 150s sequential)
    └─ Return results + errors separated
        ↓
Response: {"total": 50, "successes": 48, "failures": 2, "results": [...], "errors": [...]}
    ↓
Frontend displays results
```

### Backend Implementation Pattern

```python
# backend/services/process_service.py
class ProcessService:
    def __init__(self, db: Session):
        self.db = db
        self.client = DataJudClient()
        self.semaphore = asyncio.Semaphore(10)  # Concurrency limit

    async def _get_process_with_limit(self, number: str):
        """Fetch with rate limiting via semaphore."""
        async with self.semaphore:
            try:
                return await self.get_or_update_process(number)
            except Exception as e:
                return {"number": number, "error": str(e)}

    async def bulk_search(self, numbers: list[str]):
        """Parallel bulk search."""
        if len(numbers) > 100:
            raise ValidationException("Max 100 processes")

        tasks = [self._get_process_with_limit(n) for n in numbers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successes = [r for r in results if isinstance(r, dict) and "error" not in r]
        failures = [r for r in results if isinstance(r, dict) and "error" in r]

        return {
            "total": len(numbers),
            "successes": len(successes),
            "failures": len(failures),
            "results": successes,
            "errors": failures
        }
```

### Performance Target

| Batch Size | Sequential (Current) | Parallel (Target) | Improvement |
|-----------|---------------------|-----------------|------------|
| 10 | 30s | 5s | 83% |
| 50 | 150s | 25s | 83% |
| 100 | 300s | 50s | 83% |

**Why 83%?** (not 90%+)
- Network latency baseline (RTT to DataJud) ~500-1000ms
- 10 concurrent requests = ~5-10s minimum (server RTT)
- Plus overhead (database writes, serialization)

### Error Handling Strategy

**Graceful Degradation:**
```python
# Individual failures don't block batch
results = await asyncio.gather(*tasks, return_exceptions=True)

# Separate successes from failures
successes = [r for r in results if not isinstance(r, Exception)]
failures = [{"number": numbers[i], "error": str(r)}
           for i, r in enumerate(results) if isinstance(r, Exception)]

# Return both
return {
    "successes": len(successes),
    "failures": len(failures),
    "results": successes,
    "errors": failures
}
```

---

## Files Affected

### Modified
- `backend/services/datajud.py` (add connection pooling - optional)
- `backend/services/process_service.py` (refactor bulk_search)
- `backend/config.py` (add BULK_* settings)
- `backend/schemas.py` (update BulkProcessResponse)
- `backend/main.py` (verify async endpoint)
- `frontend/src/components/BulkSearch.jsx` (add progress tracking)
- `README.md` (document performance improvement)

### Created
- `backend/tests/test_process_service_bulk.py` (NEW - bulk tests)
- `docs/operations/performance-tuning.md` (NEW - tuning guide)
- `docs/operations/parallel-processing-architecture.md` (NEW - architecture)

### Affected Indirectly
- Frontend API response handling (now includes "errors" field)
- Monitoring/alerting (will capture bulk operation metrics)

---

## Definition of Done

### Development Phase
- [ ] DataJudClient verified as fully async (no blocking calls)
- [ ] Connection pooling added (optional but recommended)
- [ ] Semaphore implemented (concurrency_limit = 10)
- [ ] `bulk_search()` refactored to use `asyncio.gather()`
- [ ] Error handling graceful (no cascading failures)
- [ ] Configuration added (`BULK_CONCURRENCY_LIMIT`, `BULK_MAX_BATCH_SIZE`)
- [ ] Response schema updated (successes + failures)

### Testing Phase
- [ ] Unit tests written (3+ test cases):
  - [ ] Parallel execution verified (timing)
  - [ ] Error handling (failures don't block)
  - [ ] Concurrency limit enforced
- [ ] Integration tests:
  - [ ] 10 item batch <5s
  - [ ] 50 item batch <30s
  - [ ] 100 item batch <60s
- [ ] Performance benchmarking:
  - [ ] Sequential vs parallel timing compared
  - [ ] 80%+ improvement confirmed
- [ ] Memory profiling:
  - [ ] Peak memory <500MB for 100 items
  - [ ] No memory leaks (baseline stable)
- [ ] Error scenarios:
  - [ ] Mixed valid/invalid handled gracefully
  - [ ] Rate limiting respected
  - [ ] Partial results returned

### Frontend Phase
- [ ] Progress state added to BulkSearch component
- [ ] Progress bar UI renders correctly
- [ ] Counter shows X / N complete
- [ ] API response handling updated (errors field)
- [ ] Error display shows failures separately

### Quality Assurance
- [ ] Code reviewed (parallel patterns, error handling)
- [ ] No obvious concurrency issues
- [ ] Connection management correct (no leaks)
- [ ] Database transaction safety verified
- [ ] Linting passes
- [ ] Type checking passes (if TypeScript frontend)

### Documentation
- [ ] README.md updated (performance improvement documented)
- [ ] Performance tuning guide written
- [ ] Architecture diagram created (parallel processing)
- [ ] Comments added to code (explain Semaphore, asyncio.gather)
- [ ] Configuration documented (BULK_* settings)

### Deployment
- [ ] Feature flag added (optional, but recommended)
- [ ] Can disable via `.env` if issues
- [ ] Rollback plan tested (<5 min via env var)
- [ ] Staging validated before production

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **DataJud rate limiting** | MEDIUM | HIGH | Semaphore (10 concurrent), monitor 429 responses |
| **SQLite single-writer bottleneck** | LOW | MEDIUM | Row-level locks already in place, monitor perf |
| **Memory exhaustion (100+ items)** | LOW | HIGH | Max batch = 100, memory profiling in testing |
| **Cascading failures** | LOW | MEDIUM | `return_exceptions=True`, graceful degradation |
| **Slower individual requests** | LOW | LOW | Connection pooling, httpx reuses sockets |

### Mitigation Details

**DataJud Rate Limiting:**
- Start conservative: 10 concurrent (Semaphore)
- Monitor 429 "Too Many Requests" responses
- Adjust `BULK_CONCURRENCY_LIMIT` if needed
- Future: Implement exponential backoff (separate story)

**SQLite Bottleneck:**
- Row-level locking (`.with_for_update()`) already prevents race conditions
- Monitor bulk operation performance over time
- If degrades, consider migration to PostgreSQL (future)

---

## Acceptance Testing Scenarios

### Scenario 1: 10 Item Batch (Quick Test)
```bash
curl -X POST http://localhost:8011/processes/bulk \
  -H "Content-Type: application/json" \
  -d '{"numbers": [
    "0000000009900000001",  # 10 valid CNJ numbers
    ...
  ]}'

# Expected: <5s, all successes
```

### Scenario 2: 50 Item Batch (Performance Test)
```bash
# 50 valid numbers
# Measure response time
time curl -X POST .../processes/bulk -d '{"numbers": [...]}'

# Expected: <30s (vs 150s sequential)
```

### Scenario 3: Mixed Valid/Invalid (Error Handling)
```bash
# 20 valid + 5 invalid
# Expected response:
{
  "total": 25,
  "successes": 20,
  "failures": 5,
  "results": [...20 items...],
  "errors": [
    {"number": "invalid1", "error": "..."},
    ...
  ]
}
```

### Scenario 4: 100 Item Batch (Max Capacity)
```bash
# 100 valid numbers
# Expected: <60s, no crash, memory stable
```

### Scenario 5: Progress Tracking (Frontend)
```javascript
// Start bulk search in BulkSearch component
// Observe progress bar updates
// Expected: Counter shows X/50, percentage increases
```

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Latency (50 items)** | <30s | `time curl ... /processes/bulk` |
| **Improvement** | ≥80% | (150s - result) / 150s × 100 |
| **Memory Usage** | <500MB | `psutil.Process().memory_info()` |
| **Error Rate** | <2% | failures / total in test batches |
| **Concurrency Limit** | ≤10 | Measure concurrent requests |

---

## Change Log

- **2026-02-21:** Story created by @architect (Aria) from PLAN-003
- Status: Ready for @dev implementation

---

## Related Documents

- **Implementation Plan:** `docs/brownfield/plans/PLAN-003-async-bulk-processing.md`
- **System Architecture:** `docs/brownfield/system-architecture.md` (Sections: Backend Layer, Performance)
- **Performance Tuning:** `docs/operations/performance-tuning.md` (to be created)

---

**Story Owner:** @dev
**Story Reviewer:** @qa
**Architect:** @architect (Aria)
**Created:** 2026-02-21
**Target Sprint:** 1 (Critical)
