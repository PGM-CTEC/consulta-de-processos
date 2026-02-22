# STORY-REM-011: Add Log Rotation

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** OPS-ARCH-001
**Type:** Operations
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 1

## Description

Configure Python logging with RotatingFileHandler (10 MB max, 5 backups) to prevent disk full from unbounded log growth.

## Acceptance Criteria

- [ ] RotatingFileHandler configured (10 MB max per file)
- [ ] 5 backup files retained (app.log, app.log.1, app.log.2, ..., app.log.5)
- [ ] Old logs deleted automatically when exceeding 5 backups
- [ ] Test: Generate 11 MB of logs → 2 files created (10 MB + 1 MB)

## Technical Notes

```python
# backend/main.py
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory
import os
os.makedirs('logs', exist_ok=True)

# Configure rotating handler
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5  # Keep 5 old files (app.log.1 to app.log.5)
)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger()
logger.addHandler(handler)
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
