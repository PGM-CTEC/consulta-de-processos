# STORY-REM-016: Centralized Logging with Local Observability Stack

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** LOG-ARCH-002
**Type:** Observability
**Complexity:** 8 pts (M - 1 day)
**Priority:** HIGH
**Assignee:** Backend Developer
**Status:** Complete
**Sprint:** Sprint 7

## Description

Implement a centralized local logging solution (adapted from CloudWatch plan) with structured JSON logs,
per-request correlation IDs, HTTP access logs, and an enhanced CLI viewer for log querying.

**ADAPTATION (2026-02-24):** Original story called for AWS CloudWatch. Since this project runs locally,
CloudWatch was replaced with an equivalent local stack:
- Correlation ID middleware (replaces CloudWatch trace IDs)
- HTTP access log middleware (replaces CloudWatch access log group)
- Enhanced `logs-view.py` CLI (replaces CloudWatch Insights)

## Acceptance Criteria

- [x] Correlation ID middleware: each request gets a unique `X-Request-ID` (UUID4)
- [x] Correlation ID echoed back in response headers
- [x] HTTP access log with method, path, status, duration_ms, client_ip, correlation_id
- [x] Access logs written to `logs/access.log` (separate from `logs/backend.log`)
- [x] Health probe paths (`/health`, `/ready`) excluded from access logs (noise reduction)
- [x] `logs-view.py` supports `--last Nh/Nm/Nd` (relative time filter)
- [x] `logs-view.py` supports `--search TEXT` (free-text search across all fields)
- [x] `logs-view.py` supports `--request-id UUID` (end-to-end request tracing)
- [x] `logs-view.py` supports `--tail` mode (real-time follow like tail -f)
- [x] `logs-view.py` summary mode shows error rate, top endpoints, top services
- [x] 7/7 middleware unit tests passing
- [x] Pre-existing logging tests fixed (Windows file-lock cleanup)

## Technical Implementation

### Correlation ID Middleware (`backend/middleware/correlation_id.py`)
```python
class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = correlation_id
        return response
```

### Request Logger Middleware (`backend/middleware/request_logger.py`)
```python
class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"{method} {path} → {status} ({duration_ms}ms)",
            extra={"method": ..., "path": ..., "status_code": ...,
                   "duration_ms": ..., "client_ip": ..., "correlation_id": ...})
        return response
```

### Log CLI Examples
```bash
# Last 1 hour of errors
python backend/scripts/logs-view.py --level ERROR --last 1h

# Trace a full request by ID
python backend/scripts/logs-view.py --request-id "abc-123..." --format table

# Search for a CNJ number
python backend/scripts/logs-view.py --search "0001234-56.2023"

# Real-time follow
python backend/scripts/logs-view.py --tail --level WARNING

# Access log summary
python backend/scripts/logs-view.py --log-file logs/access.log --format summary
```

## Middleware Registration Order in main.py

Starlette middleware wraps in reverse order of `add_middleware()` calls, so:
1. `app.add_middleware(RequestLoggerMiddleware)` — outer
2. `app.add_middleware(CorrelationIdMiddleware)` — inner

At runtime: CorrelationId runs first (sets `request.state.correlation_id`), then RequestLogger reads it.

## Files Created/Modified

### New Files
- `backend/middleware/__init__.py` — Package with exports
- `backend/middleware/correlation_id.py` — Correlation ID middleware
- `backend/middleware/request_logger.py` — HTTP access log middleware
- `backend/tests/test_middleware_logging.py` — 7 middleware unit tests

### Modified Files
- `backend/utils/logger.py` — Added `setup_access_logger()`, `console` param to `setup_logger()`
- `backend/main.py` — Registered both middlewares + access logger init
- `backend/scripts/logs-view.py` — Full rewrite with `--last`, `--search`, `--request-id`, `--tail`
- `backend/tests/test_logging.py` — Fixed Windows file-lock cleanup in 2 tests

## Test Results

```
14 passed, 0 failed
- TestCorrelationIdMiddleware::test_generates_id_when_not_provided  PASS
- TestCorrelationIdMiddleware::test_reuses_client_id                PASS
- TestCorrelationIdMiddleware::test_different_requests_get_different_ids PASS
- TestRequestLoggerMiddleware::test_logs_request_to_file            PASS
- TestRequestLoggerMiddleware::test_logs_status_code                PASS
- TestRequestLoggerMiddleware::test_logs_correlation_id             PASS
- TestRequestLoggerMiddleware::test_skips_health_paths              PASS
- test_logger_setup                                                 PASS
- test_logger_writes_json                                           PASS
- test_logger_rotation                                              PASS
- test_redact_cpf / test_redact_email / test_redact_dict            PASS
- test_get_logger                                                   PASS
```

## Comparison with CloudWatch (original story)

| Feature | CloudWatch (original) | Local Stack (implemented) |
|---------|----------------------|--------------------------|
| Centralized logs | Log groups in AWS | `logs/backend.log` + `logs/access.log` |
| Request tracing | X-Ray trace IDs | X-Request-ID (UUID4) |
| Access logs | CloudWatch access log group | RequestLoggerMiddleware → `logs/access.log` |
| Log search | CloudWatch Insights queries | `logs-view.py --search / --last / --request-id` |
| Real-time | CloudWatch Live Tail | `logs-view.py --tail` |
| Log retention | 30-day policy | RotatingFileHandler (10MB × 7 backups) |
| Cost | $0.50/GB ingested | Free (local disk) |

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-24 | @dev | Implemented local logging stack: correlation ID + access log middleware + enhanced CLI |
| 2026-02-24 | @dev | 14/14 tests passing, pre-existing test fixes applied |
| 2026-02-23 | @pm  | Story created from Brownfield Discovery Phase 10 |
