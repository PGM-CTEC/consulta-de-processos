# Sprint 7: Performance & Observability

**Sprint Number:** Sprint 7 (Sprint 2 of Brownfield Remediation)
**Duration:** 10-12 days (2-3 weeks)
**Status:** Planning
**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Date Range:** Post-Sprint-6 (2026-03-03 onwards)

---

## Sprint Overview

**Objetivo Principal:** Remove performance bottlenecks and enable production monitoring — making the system visible and fast for end users.

**Business Value:**
- 🚀 **Performance:** Bulk search 2-5min → <30s (80% improvement)
- 📊 **Observability:** Zero visibility → Full error tracking + health checks
- 🔄 **Resilience:** Single points of failure → Retry logic + circuit breakers
- 🎯 **Monitoring:** Silent failures → Proactive alerts

**Effort Distribution:**
- Backend Developer: 10 days
- DevOps Engineer: 2 days

---

## Stories Sprint 7 (5 Total)

| ID | Story | Effort | Developer | Status |
|----|-------|--------|-----------|--------|
| REM-012 | Implement Async Bulk Processing | 13 pts (L) | Backend | [ ] TODO |
| REM-013 | Integrate Sentry Error Monitoring | 8 pts (M) | Backend | [ ] TODO |
| REM-014 | Add Health Check Endpoints | 8 pts (M) | Backend | [ ] TODO |
| REM-015 | Implement Retry Logic for DataJud | 3 pts (S) | Backend | [ ] TODO |
| REM-016 | Centralized Logging with CloudWatch | 8 pts (M) | Backend | [ ] TODO |

---

## Acceptance Criteria (Sprint Level)

- [ ] Async bulk processing completes 50 CNJ in <30s (80% faster)
- [ ] Sentry operational with alerts configured (Slack)
- [ ] /health endpoint returning 200 with DB connectivity check
- [ ] Health checks integrated with monitoring
- [ ] Retry logic working for transient DataJud failures
- [ ] CloudWatch logs streaming successfully
- [ ] All tests passing (unit + E2E)
- [ ] Performance benchmarks documented
- [ ] No regressions in existing functionality
- [ ] PR ready for review

---

## Story Details

### REM-012: Implement Async Bulk Processing
**Debit ID:** PERF-ARCH-001 | **Priority:** CRITICAL
**Complexity:** 13 pts (L - 3-5 days)

**Problem:** Sequential processing of 50 CNJ numbers takes 2-5 minutes. Users abandon searches.

**Solution:** Use `asyncio.gather()` for parallel DataJud API calls with configurable concurrency limit.

**Acceptance Criteria:**
- [ ] `bulk_search_async()` function created using async/await
- [ ] ClientSession from aiohttp used for parallel requests
- [ ] Concurrency limit = 10 (avoid overwhelming DataJud)
- [ ] Error handling: return_exceptions=True (partial failures ok)
- [ ] Performance test: 50 CNJ in <30s
- [ ] Unit tests for async function
- [ ] E2E test for bulk workflow

**Technical Notes:**
```python
async def bulk_search_async(self, numeros: list[str]):
    async with ClientSession() as session:
        tasks = [
            self._fetch_datajud_async(session, numero)
            for numero in numeros
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

**Key Metrics:**
- Baseline: 150s for 50 items
- Target: <30s
- Expected: 80% latency reduction

---

### REM-013: Integrate Sentry Error Monitoring
**Debit ID:** ERROR-ARCH-002 | **Priority:** CRITICAL
**Complexity:** 8 pts (M - 3-5 days)

**Problem:** Production errors go unnoticed. No alerts or dashboards.

**Solution:** Sentry SDK integration with Slack alerts and performance tracing.

**Acceptance Criteria:**
- [ ] Sentry project created (sentry.io account)
- [ ] SENTRY_DSN environment variable configured
- [ ] sentry_sdk.init() in backend/main.py
- [ ] FastAPI integration enabled
- [ ] Test error triggered → appears in dashboard
- [ ] Slack alerts configured for CRITICAL errors
- [ ] Tracing enabled (traces_sample_rate=0.1)
- [ ] User context captured (optional auth)

**Technical Notes:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv('ENVIRONMENT', 'development')
)
```

**Slack Integration:**
- Settings → Integrations → Slack
- Alert rule: "CRITICAL level → Send Slack notification"

---

### REM-014: Add Health Check Endpoints
**Debit ID:** DEPLOY-ARCH-004 | **Priority:** CRITICAL
**Complexity:** 8 pts (M - 3-5 days)

**Problem:** No way to detect downtime. Load balancers can't health check.

**Solution:** Implement /health (liveness) and /ready (readiness) endpoints.

**Acceptance Criteria:**
- [ ] GET /health returns 200 + JSON status
- [ ] Database connectivity check included
- [ ] Response time <100ms
- [ ] 503 Service Unavailable if DB down
- [ ] Uptime monitoring configured (UptimeRobot)
- [ ] Kubernetes probes documented

**Technical Notes:**
```python
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

**Kubernetes Config:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

### REM-015: Implement Retry Logic for DataJud
**Debit ID:** BE-ARCH-002 | **Priority:** HIGH
**Complexity:** 3 pts (S - 1 day)

**Problem:** Transient DataJud API failures cause bulk searches to fail.

**Solution:** Exponential backoff retry (3 attempts, 1s/2s/4s delays).

**Acceptance Criteria:**
- [ ] Retry decorator or library used (tenacity)
- [ ] Max 3 retry attempts
- [ ] Exponential backoff: 1s, 2s, 4s
- [ ] Retry only on transient errors (503, 429, timeout)
- [ ] Skip retry on client errors (4xx)
- [ ] Unit tests

**Technical Notes:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4)
)
async def fetch_datajud_with_retry(numero: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DATAJUD_URL}/processos/{numero}")
        response.raise_for_status()
        return response.json()
```

---

### REM-016: Centralized Logging with CloudWatch
**Debit ID:** LOG-ARCH-002 | **Priority:** HIGH
**Complexity:** 8 pts (M - 3-5 days)

**Problem:** Logs only on disk. Can't search production logs.

**Solution:** AWS CloudWatch Logs integration with CloudWatch Insights queries.

**Acceptance Criteria:**
- [ ] watchtower library installed
- [ ] CloudWatch log group created: `/app/consulta-processo`
- [ ] Backend logs streaming to CloudWatch
- [ ] 30-day retention configured
- [ ] CloudWatch Insights query tested
- [ ] IAM permissions configured

**Technical Notes:**
```python
import watchtower

cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group_name='/app/consulta-processo',
    stream_name='backend',
    use_queues=True
)

logger.addHandler(cloudwatch_handler)
```

**CloudWatch Insights Query:**
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

---

## Dependencies

**Sprint 6 → Sprint 7 Blockers:**
- ✅ SEC-ARCH-001 (Secrets) — Optional (needed for production deploy)
- ✅ DB-001 (Indexes) — Recommended (improves async perf)

**Within Sprint 7:**
- REM-012 (Async) → Blocks TEST-ARCH-001 (async tests)
- REM-014 (Health) → Integrates with REM-013 (monitoring)

---

## Implementation Order

**Phase 1: Core Async (Days 1-5)**
1. REM-012: Async bulk processing
2. REM-015: Retry logic (complements async)

**Phase 2: Monitoring (Days 3-8)**
3. REM-013: Sentry integration
4. REM-014: Health checks (integrates with Sentry)

**Phase 3: Logging (Days 6-10)**
5. REM-016: CloudWatch logging

---

## Success Metrics

### Performance
- **Before:** 150s for 50 CNJ items
- **After:** <30s for 50 CNJ items
- **Target:** ✅ 80% latency reduction

### Reliability
- **Before:** No retry logic, single failures block operations
- **After:** 3 retries with exponential backoff
- **Target:** ✅ 99% success rate for transient failures

### Observability
- **Before:** No error tracking, no uptime monitoring
- **After:** Sentry + health checks + centralized logs
- **Target:** ✅ MTTR <1 hour

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Async introduces deadlocks | MEDIUM | HIGH | Test with concurrent load, monitor DB locks |
| Sentry DSN leaked | LOW | CRITICAL | Use secrets vault, rotate keys |
| CloudWatch costs spike | MEDIUM | MEDIUM | Set retention to 30 days, monitor usage |
| DataJud rate limiting triggered | MEDIUM | MEDIUM | Test retry logic, implement circuit breaker (Sprint 8) |

---

## Definition of Done

For each story:
- [ ] Code written and tested locally
- [ ] All acceptance criteria met
- [ ] Unit tests added (>90% coverage)
- [ ] Integration tests added
- [ ] Performance benchmarks documented
- [ ] No regressions in existing tests
- [ ] CodeRabbit review passed
- [ ] Manual code review approved
- [ ] Merged to sprint-7 branch
- [ ] Verified in staging environment

---

## Testing Strategy

### Unit Tests
- Async function tests (with pytest-asyncio)
- Retry logic tests (mock DataJud failures)
- Health check tests

### Integration Tests
- Bulk search end-to-end
- Sentry error capture
- CloudWatch log delivery

### Performance Tests
- Load test: 50 concurrent bulk searches
- Measure: latency p50/p95/p99
- Target: <30s for 50 items

### Monitoring Tests
- Trigger error → Verify Sentry
- Stop DB → Verify /health 503
- Generate logs → Verify CloudWatch

---

## Timeline

| Phase | Duration | Tasks | Owner |
|-------|----------|-------|-------|
| Async Core | 3-5 days | REM-012, REM-015 | @dev |
| Monitoring | 3-5 days | REM-013, REM-014 | @dev |
| Logging | 3-5 days | REM-016 | @dev |
| **Total** | **10-12 days** | **5 stories** | **@dev** |

---

## Communication

**Daily Sync:** Slack #sprint-7-updates
**Issues:** GitHub tagged `sprint-7`
**Code Review:** PR comments
**Blockers:** Escalate to @pm (Morgan)

---

## Next Steps After Sprint 7

**Sprint 8 Planning (in parallel):**
- Circuit breaker pattern (EXT-ARCH-001)
- Backend test coverage improvements
- E2E test suite setup

**Decisions Needed:**
1. CloudWatch or ELK for centralized logging?
2. Circuit breaker library (pybreaker vs others)?
3. Performance targets (p95 <500ms?)

---

**Sprint 7 Planning Complete**
**Status:** Ready for Development
**Next:** Wait for Sprint 6 PR merge, then kick off Sprint 7

