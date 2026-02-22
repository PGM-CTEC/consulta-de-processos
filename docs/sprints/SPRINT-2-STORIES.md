# Sprint 2 Stories (Performance & Observability)

## Overview
5 stories, 12-14 days total effort
Focus: Remove performance blockers + enable production monitoring

---

## Story 1: PERF-ARCH-001 - Async Bulk Processing
**Type:** Feature | **Complexity:** 8 pts | **Severity:** CRITICAL
**Effort:** 3-5 days | **Impact:** 80% latency reduction

### Current Problem
Bulk searches process CNJ numbers sequentially:
- 50 items × 100-150ms per API call = 5-7.5 seconds minimum
- User experience: 2-5 minutes for 50+ items (user abandonment)

### Solution
Implement async/await with ClientSession connection pooling:
```python
async def bulk_search_async(numeros: list[str], max_concurrent: int = 10):
    async with ClientSession() as session:
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = [fetch_datajud_async(session, n, semaphore) for n in numeros]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

### Acceptance Criteria
- [ ] ProcessService.bulk_search() converted to async
- [ ] DataJud API calls run in parallel (10 concurrent max)
- [ ] 50-item bulk completes in <30s
- [ ] Individual failures don't block batch (return_exceptions=True)
- [ ] Configurable concurrency limit in .env
- [ ] No regression in single-process endpoint

### Files to Modify
- backend/services/process_service.py (lines 170-200)
- backend/services/datajud.py (add async variants)
- backend/main.py (make endpoint async)
- backend/config.py (add BULK_MAX_CONCURRENT)

### Dependencies
None (but enables TEST-ARCH-001 async tests)

---

## Story 2: ERROR-ARCH-002 - Sentry Integration
**Type:** Feature | **Complexity:** 5 pts | **Severity:** CRITICAL
**Effort:** 3-5 days | **Impact:** Real-time error monitoring

### Current Problem
- Errors logged locally only
- No alerting mechanism
- Production blind spots (silent failures)

### Solution
Integrate Sentry.io for error aggregation + Slack alerts:
```python
import sentry_sdk
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=0.1,
    environment=os.getenv('ENVIRONMENT', 'development')
)
```

### Acceptance Criteria
- [ ] Sentry SDK initialized in FastAPI app
- [ ] All unhandled exceptions captured
- [ ] DataJud API errors logged with context (CNJ number, status code)
- [ ] Database connection errors captured
- [ ] Sentry account created + DSN configured in .env
- [ ] Slack integration setup (test alert sent)
- [ ] Alert rules configured (threshold: 5 errors/hour)

### Files to Modify
- backend/main.py (add sentry_sdk import + init)
- backend/config.py (add SENTRY_DSN to Settings)
- .env.example (add SENTRY_DSN)
- backend/README.md (document setup)

### Setup Steps
1. Create free account at sentry.io
2. Generate DSN for project
3. Configure Slack integration in Sentry dashboard
4. Add SENTRY_DSN to .env
5. Deploy and verify alerts

### Dependencies
None

---

## Story 3: DEPLOY-ARCH-004 - Health Checks
**Type:** Feature | **Complexity:** 5 pts | **Severity:** CRITICAL
**Effort:** 3-5 days | **Impact:** Uptime monitoring enabled

### Current Problem
- No /health endpoint
- Monitoring tools cannot detect downtime
- Silent deployment failures

### Solution
Implement /health and /ready endpoints for deployment readiness:
```python
@app.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503

@app.get("/ready", tags=["health"])
async def readiness_check(db: Session = Depends(get_db)):
    return {"ready": True}
```

### Acceptance Criteria
- [ ] /health endpoint returns 200 (healthy state)
- [ ] /ready endpoint for Kubernetes probes
- [ ] Database connectivity verified
- [ ] Response time <200ms
- [ ] Monitoring tools can scrape endpoint
- [ ] Documented in backend/README.md

### Files to Modify
- backend/main.py (add endpoints)
- backend/config.py (optional: timeout config)
- backend/README.md (document)

### Dependencies
None

---

## Story 4: BE-ARCH-002 - Retry Logic & Resilience
**Type:** Feature | **Complexity:** 3 pts | **Severity:** MEDIUM
**Effort:** 1 day | **Impact:** Resilience to transient failures

### Current Problem
- No retry on transient DataJud failures
- Single timeout = failure (no retry mechanism)

### Solution
Implement exponential backoff retry logic using tenacity:
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

### Acceptance Criteria
- [ ] Retry logic for transient failures (timeout, connection error)
- [ ] Exponential backoff (2s, 4s, 8s)
- [ ] Max 3 attempts before failure
- [ ] Separate handling for permanent failures (404, 400)
- [ ] Metrics logged (retry count, final status)
- [ ] Unit tests for retry behavior

### Files to Modify
- backend/services/datajud.py (add retry decorator)
- backend/requirements.txt (add tenacity)
- backend/tests/ (add retry tests)

### Dependencies
None

---

## Story 5: LOG-ARCH-002 - Centralized Logging
**Type:** Feature | **Complexity:** 8 pts | **Severity:** HIGH
**Effort:** 3-5 days | **Impact:** Searchable production logs

### Current Problem
- Logs written to local files only
- No centralized searchable log storage
- Debugging in production is difficult

### Solution
Ship logs to CloudWatch (AWS) or ELK stack:
```python
from watchtower import CloudWatchLogHandler
import logging

handler = CloudWatchLogHandler(
    log_group='consulta-processo-prod',
    stream_name='backend'
)
logging.getLogger().addHandler(handler)
```

### Acceptance Criteria
- [ ] CloudWatch Logs integration (OR local ELK)
- [ ] Structured JSON format (timestamp, level, message, context)
- [ ] Full request context (user IP, CNJ number, endpoint)
- [ ] Full error context (stack trace, response code)
- [ ] Searchable dashboard in CloudWatch/ELK
- [ ] Log retention policy configured (30 days)
- [ ] Performance impact <100ms per request

### Files to Modify
- backend/utils/logger.py (add CloudWatch handler)
- backend/config.py (add CLOUDWATCH_* config)
- backend/main.py (integrate logger)
- .env.example (add logging vars)
- backend/README.md (document setup)

### Implementation Options
**Option A (Recommended):** CloudWatch Logs (AWS free tier)
**Option B:** ELK Stack (self-hosted, requires infra)
**Option C:** Datadog/New Relic (paid SaaS)

### Dependencies
None

---

## Implementation Order

**Days 1-2:** PERF-ARCH-001 start (async bulk)
**Days 1-3:** ERROR-ARCH-002 start (Sentry setup)
**Days 2-4:** DEPLOY-ARCH-004 start (health checks)
**Days 4-5:** BE-ARCH-002 (retry logic)
**Days 5-8:** LOG-ARCH-002 start (centralized logging)
**Days 8-12:** Parallel: finish async, complete logging
**Days 12-14:** Testing & bug fixes

---

## Success Metrics

**Performance:**
- Bulk 50 items: 2-5 min → <30s (80% improvement)
- Single search latency: <500ms
- No performance regression

**Observability:**
- Sentry capturing >95% of errors
- Alert latency <5 minutes
- Centralized logs searchable <2s

**Quality:**
- All tests passing
- CodeRabbit clean (0 CRITICAL)
- All AC met

---

**Sprint 2 Stories Created:** 2026-02-22
**Ready for:** @dev implementation
