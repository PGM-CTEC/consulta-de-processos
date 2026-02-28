# STORY-REM-048: Log Structure Improvement

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** LOG-ARCH-001, LOG-ARCH-003
**Type:** Observability
**Complexity:** 5 pts (M - 1 day)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Done
**Sprint:** Sprint 5+

## Description

Migrate to structured JSON logging with standardized fields (timestamp, level, message, context) for better log parsing and analysis.

## Acceptance Criteria

- [x] JSON logging configured (python-json-logger or structlog)
- [x] Correlation IDs added to trace requests
- [x] Standardized log fields (timestamp, level, logger, message, context)
- [x] Sensitive data redacted from logs
- [x] Log levels properly used (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [x] CloudWatch Insights queries work with new format

## Technical Notes

```python
# Install structlog
pip install structlog

# backend/logging_config.py
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage
logger.info("process_searched", cnj=cnj, user_id=user_id, correlation_id=correlation_id)
```

**Output:**
```json
{
  "timestamp": "2026-02-23T10:30:00.123Z",
  "level": "info",
  "event": "process_searched",
  "cnj": "12345678901234567890",
  "user_id": "user_123",
  "correlation_id": "abc-123-def"
}
```

## Dependencies

None

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

**Status:** Ready for Review

## File List

- `backend/utils/logger.py` — JSON logger (pythonjsonlogger) com rotação, campos padrão, correlation_id (implementado em REM-016)
- `backend/utils/redact.py` — Redação de dados sensíveis nos logs
- `backend/middleware.py` — CorrelationIdMiddleware + RequestLoggerMiddleware

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Verificado: logging JSON estruturado já implementado em REM-016 — todos os critérios atendidos |
