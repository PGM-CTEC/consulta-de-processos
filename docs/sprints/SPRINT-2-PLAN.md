# Sprint 2 Planning: Performance & Observability
**Weeks 2-3** | **Duration:** 10-12 days | **Team Effort:** 12 days (Backend Dev: 10d, DevOps: 2d)

---

## Sprint Goal
Remove user-facing performance blockers and enable production monitoring for real-time issue detection.

---

## Sprint Scope (5 Tasks)

### 1️⃣ PERF-ARCH-001: Async Bulk Processing (3-5 days)
**Type:** Performance | **Severity:** CRITICAL
**Impact:** Bulk search 2-5 min → <30s (80% improvement)
**Files:** `backend/services/process_service.py`, `backend/services/datajud.py`

**Current State:**
```python
# Sequential processing (blocking)
for numero in numeros:
    resultado = fetch_datajud(numero)  # 50-150ms per call
    results.append(resultado)
# Total: 50 items × 100ms = ~5000ms (5 seconds)
```

**Target Implementation:**
```python
async def bulk_search_async(numeros: list[str]):
    async with ClientSession() as session:
        tasks = [fetch_datajud_async(session, n) for n in numeros]
        return await asyncio.gather(*tasks, return_exceptions=True)
# Target: 50 items in <30 seconds (parallel: 30 items in parallel = 2 requests)
```

**Acceptance Criteria:**
- [ ] Async implementation in ProcessService
- [ ] ClientSession connection pooling
- [ ] Graceful error handling (individual failures don't block batch)
- [ ] Concurrency limit configurable (default: 10)
- [ ] 50-item bulk completes in <30s
- [ ] No regression in single-process endpoint

**Files to Modify:**
- `backend/services/process_service.py` (lines 170-200)
- `backend/services/datajud.py` (add async variants)
- `backend/models.py` (response models if needed)
- `backend/main.py` (async endpoint definition)

**Dependencies:** None (but unlocks TEST-ARCH-001 async tests in Sprint 3)

---

### 2️⃣ ERROR-ARCH-002: Sentry Integration (3-5 days)
**Type:** Operations | **Severity:** CRITICAL
**Impact:** Production blind spots → real-time error monitoring
**Files:** `backend/main.py`, `backend/config.py`

**Current State:**
- Errors logged locally only
- No alerting or aggregation
- Silent failures in production

**Target Implementation:**
```python
import sentry_sdk
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=0.1,
    environment=os.getenv('ENVIRONMENT', 'development')
)
```

**Setup Steps:**
1. Create free Sentry account (sentry.io)
2. Generate DSN for project
3. Add SENTRY_DSN to .env
4. Integrate with Slack for alert routing
5. Configure alert rules (>5 errors/hour = Slack notification)

**Acceptance Criteria:**
- [ ] Sentry SDK initialized in FastAPI app
- [ ] Error middleware capturing exceptions
- [ ] SENTRY_DSN configured in production
- [ ] Slack integration working (test alert sent)
- [ ] Alert rules configured (threshold: 5 errors/hour)
- [ ] DataJud API errors logged with context (CNJ number, status code)
- [ ] Database connection errors captured

**Files to Modify:**
- `backend/main.py` (add sentry_sdk import + init)
- `backend/config.py` (add SENTRY_DSN to Settings)
- `.env.example` (add SENTRY_DSN placeholder)
- `backend/middleware.py` (add error context capture)

**Dependencies:** None

---

### 3️⃣ DEPLOY-ARCH-004: Health Checks (3-5 days)
**Type:** Operations | **Severity:** CRITICAL
**Impact:** Cannot detect downtime → uptime monitoring enabled
**Files:** `backend/main.py`

**Current State:**
- No /health endpoint
- Monitoring tools cannot verify uptime
- Silent deployment failures

**Target Implementation:**
```python
@app.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        # Database connectivity
        db.execute("SELECT 1")

        # DataJud connectivity check (optional, cached)
        datajud_status = "ok"  # or "degraded" if timeout

        return {
            "status": "healthy",
            "database": "connected",
            "datajud": datajud_status,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503

@app.get("/ready", tags=["health"])
async def readiness_check(db: Session = Depends(get_db)):
    # More detailed readiness probe for Kubernetes
    return {"ready": True}
```

**Kubernetes/Docker Deployment Integration:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

**Acceptance Criteria:**
- [ ] /health endpoint returning 200 (healthy state)
- [ ] /ready endpoint for deployment readiness
- [ ] Database connectivity verified
- [ ] Response time <200ms
- [ ] Monitoring tools (New Relic, DataDog, etc.) can scrape endpoint
- [ ] Documentation in backend/README.md

**Files to Modify:**
- `backend/main.py` (add endpoints)
- `backend/config.py` (optional: health check timeout config)
- `backend/README.md` (document endpoints)

**Dependencies:** None (but integrates with DEPLOY-ARCH-002 CI/CD)

---

### 4️⃣ BE-ARCH-002: Retry Logic & Circuit Breaker (1 day)
**Type:** Code Quality | **Severity:** MEDIUM
**Impact:** Resilience to transient DataJud failures
**Files:** `backend/services/datajud.py`

**Current State:**
```python
# No retry on transient failures
response = requests.get(url, timeout=5)
if response.status_code != 200:
    raise Exception(f"DataJud error: {response.status_code}")
```

**Target Implementation:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_datajud_with_retry(numero: str):
    try:
        return await fetch_datajud_api(numero)
    except (TimeoutError, ConnectionError) as e:
        raise  # Let tenacity retry
```

**Acceptance Criteria:**
- [ ] Retry logic for transient failures (timeout, connection error)
- [ ] Exponential backoff (2s, 4s, 8s)
- [ ] Max 3 attempts before failure
- [ ] Separate handling for permanent failures (404, 400)
- [ ] Metrics logged (retry count, final status)

**Files to Modify:**
- `backend/services/datajud.py`
- `backend/requirements.txt` (add tenacity)

**Dependencies:** None

---

### 5️⃣ LOG-ARCH-002: Centralized Logging (3-5 days)
**Type:** Operations | **Severity:** HIGH
**Impact:** Debugging difficulty → searchable, structured logs
**Files:** `backend/utils/logger.py`, `backend/main.py`

**Current State:**
```python
# Local file logging only (see backend/utils/logger.py)
formatter = jsonlogger.JsonFormatter(...)
# Logs written to logs/backend.log (local disk)
```

**Target Implementation:**
```python
# Option 1: CloudWatch Logs (AWS)
from watchtower import CloudWatchLogHandler
log_handler = CloudWatchLogHandler(
    log_group='consulta-processo-prod',
    stream_name='backend'
)

# Option 2: ELK Stack (self-hosted)
from pythonjsonlogger import jsonlogger
# Configure to send to Logstash/Elasticsearch

# Option 3: Sentry with cron job integration
# Already included in ERROR-ARCH-002
```

**Acceptance Criteria:**
- [ ] Logs shipped to centralized system (CloudWatch OR local ELK)
- [ ] Structured JSON format (timestamp, level, message, context)
- [ ] Full request context (user IP, CNJ number, endpoint)
- [ ] Full error context (stack trace, response code)
- [ ] Searchable dashboard in logging system
- [ ] Log retention policy configured (30 days)
- [ ] Performance impact <100ms per request

**Files to Modify:**
- `backend/utils/logger.py` (add centralized handler)
- `backend/config.py` (add CLOUDWATCH_* or LOGSTASH_* config)
- `backend/main.py` (integrate logger)
- `.env.example` (add logging config vars)
- `backend/README.md` (document setup)

**Dependencies:** None

---

## Effort Breakdown

| Task | Dev | QA | DevOps | Total |
|------|-----|----|----|-------|
| PERF-ARCH-001 (async) | 3-5d | 1d | — | 4-6d |
| ERROR-ARCH-002 (Sentry) | 2d | 1d | 1d | 4d |
| DEPLOY-ARCH-004 (health) | 1-2d | 1d | — | 2-3d |
| BE-ARCH-002 (retry) | 1d | — | — | 1d |
| LOG-ARCH-002 (logging) | 2-3d | 1d | — | 3-4d |
| **TOTAL** | **9-13d** | **4d** | **1d** | **14-18d** |

---

## Sprint Acceptance Criteria

- [ ] Bulk search 50 items in <30s (4x improvement from 2-5 min)
- [ ] Sentry operational with Slack alerts working
- [ ] /health endpoint returning 200 (verified with monitoring tool)
- [ ] Zero DataJud API failures due to transient issues (retry logic working)
- [ ] Centralized logging operational (CloudWatch or ELK)
- [ ] All tasks passing CodeRabbit review (CRITICAL/HIGH auto-fixed)
- [ ] No performance regression in single-process endpoint

---

## Dependencies & Order

```
DAY 1-2:    PERF-ARCH-001 start (async bulk)
DAY 1-3:    ERROR-ARCH-002 start (Sentry setup)
DAY 2-4:    DEPLOY-ARCH-004 start (health checks)
DAY 4-5:    BE-ARCH-002 (retry logic)
DAY 5-8:    LOG-ARCH-002 start (centralized logging)
DAY 8-12:   Parallel: finish async, complete logging
DAY 12-14:  Testing & CodeRabbit reviews
```

---

## Sprint 2 vs Sprint 1 Comparison

| Aspect | Sprint 1 | Sprint 2 |
|--------|----------|----------|
| Focus | Stabilization (Quick Wins) | Performance & Observability |
| Duration | 6-8 days | 10-12 days |
| # Stories | 10 (9 completed) | 5 (new focus) |
| Effort | 6-8 days | 12-14 days |
| Severity | 7 CRITICAL + 3 MEDIUM | 3 CRITICAL + 2 HIGH |
| Type | Infrastructure/Config | Feature + Infrastructure |
| Risk Level | LOW | MEDIUM |
| Testing Impact | Minimal | HIGH (async tests added) |

---

## Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Async implementation has subtle bugs | MEDIUM | Add comprehensive async tests in Sprint 3 |
| Sentry quota exceeded | LOW | Monitor error rate, configure sampling |
| DataJud API timeout during bulk | HIGH | Implement timeouts per item (5s), retry with backoff |
| Health check endpoint becomes bottleneck | LOW | Cache database check (5s TTL) |
| Centralized logging performance impact | MEDIUM | Batch log writes, use async handler |

---

## Success Metrics (Post-Sprint)

**Performance:**
- [ ] Bulk 50 items: 2-5 min → <30s (80% improvement)
- [ ] Single search latency: <500ms (verify with monitoring)

**Observability:**
- [ ] Sentry capturing >95% of errors
- [ ] Alert latency <5 minutes (error → Slack notification)
- [ ] Centralized logs searchable with <2s query time

**Quality:**
- [ ] No performance regressions vs Sprint 1 baseline
- [ ] CodeRabbit clean (zero CRITICAL issues)
- [ ] All acceptance criteria met

---

## Next Steps (Post-Sprint 2)

1. **Sprint 3 (Weeks 4-5):** Testing Foundation (backend tests 70%, frontend tests, E2E)
2. **Sprint 4 (Weeks 6-7):** Deployment Readiness (Docker, CI/CD)
3. **Sprint 5+ (Weeks 8+):** Polish & Migration Planning (accessibility, design system, PostgreSQL decision)

---

**Sprint 2 Plan Created:** 2026-02-22
**Based on:** technical-debt-assessment.md (Phase 8)
**Approval Gate:** Ready for @dev implementation
