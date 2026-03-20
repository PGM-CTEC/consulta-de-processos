# STORY-REM-013: Integrate Sentry Error Monitoring

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** ERROR-ARCH-002
**Type:** Observability
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** CRITICAL
**Assignee:** Backend Developer
**Status:** DECLINED - Not Required for This Project
**Sprint:** Sprint 2

## Description

Integrate Sentry SDK for error tracking, alerts (Slack), and performance monitoring (traces).

**STATUS UPDATE (2026-02-23):** Story DECLINED - Not required for this project. Local logging with Python's logging module is sufficient. Sentry code infrastructure can be removed if desired.

## Acceptance Criteria

- [ ] Sentry project created (sentry.io account)
- [ ] SENTRY_DSN environment variable configured
- [ ] sentry_sdk.init() in backend/main.py
- [ ] Frontend Sentry integration (optional but recommended)
- [ ] Test error triggered → appears in Sentry dashboard
- [ ] Slack alerts configured for CRITICAL errors
- [ ] Tracing enabled (traces_sample_rate=0.1)
- [ ] User context captured (user_id if auth exists)

## Technical Notes

```python
# backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of requests traced
    environment=os.getenv('ENVIRONMENT', 'development')
)

# Test error
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
```

**Slack Integration:**
- Sentry Settings → Integrations → Slack
- Alert rule: "When event level is CRITICAL → Send Slack notification"

## Dependencies

None (but integrates with DEPLOY-ARCH-004 health checks)

## Definition of Done

- [ ] Code complete and peer-reviewed
- [ ] Unit tests written (if applicable)
- [ ] Acceptance criteria met (all checkboxes ✅)
- [ ] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## Implementation Status

### Already Implemented (90%)
- [x] sentry_sdk imported in backend/main.py (lines 27-33)
- [x] Conditional initialization with SENTRY_AVAILABLE check
- [x] FastApiIntegration configured (lines 48-55)
- [x] SENTRY_DSN setting in backend/config.py (line 41)
- [x] traces_sample_rate=0.1 (10% tracing)
- [x] Environment variable support
- [x] Global exception handler in main.py (lines 78-94)

### Still Required (10%)
- [ ] Create Sentry project at sentry.io
- [ ] Obtain DSN and add to .env
- [ ] Test with error triggering
- [ ] (Optional) Configure Slack alerts

## Documentation & Testing

### Created
- docs/SENTRY_SETUP.md (comprehensive setup guide)
- backend/tests/test_sentry_integration.py (automated tests)
- scripts/test_sentry.py (manual test script)

### Setup Instructions
Follow docs/SENTRY_SETUP.md for step-by-step:
1. Create Sentry project at https://sentry.io
2. Copy DSN from project settings
3. Add SENTRY_DSN to .env file
4. Restart backend
5. Test error triggering: curl http://localhost:8000/sentry-debug

## File List

- backend/main.py (Sentry init + exception handler)
- backend/config.py (SENTRY_DSN setting)
- docs/SENTRY_SETUP.md (NEW - comprehensive setup guide)
- backend/tests/test_sentry_integration.py (NEW - test suite)
- scripts/test_sentry.py (NEW - manual test script)

## Change Log

| Date      | Author | Change                                                      |
| --------- | ------ | ----------------------------------------------------------- |
| 2026-02-23 | @dev   | Created setup docs + test scripts for REM-013             |
| 2026-02-23 | @dev   | Verified: Code already 90% implemented, awaiting DSN       |
| 2026-02-23 | @pm    | Story created from Brownfield Discovery Phase 10           |
