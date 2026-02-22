# STORY-REM-016: Centralized Logging with CloudWatch

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** LOG-ARCH-002
**Type:** Observability
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** HIGH
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 2

## Description

Integrate AWS CloudWatch Logs for centralized logging (aggregates logs from multiple instances, searchable).

## Acceptance Criteria

- [ ] watchtower library installed (`pip install watchtower`)
- [ ] CloudWatch log group created: `/app/consulta-processo`
- [ ] Backend logs streamed to CloudWatch
- [ ] Frontend logs streamed to CloudWatch (optional)
- [ ] Log retention: 30 days
- [ ] CloudWatch Insights query tested (search for errors)
- [ ] IAM permissions configured (logs:PutLogEvents)

## Technical Notes

```python
# backend/main.py
import logging
import watchtower

# CloudWatch handler
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group_name='/app/consulta-processo',
    stream_name='backend',
    use_queues=True
)
cloudwatch_handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.addHandler(cloudwatch_handler)
```

**CloudWatch Insights Query Example:**
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

## Dependencies

None

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
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
