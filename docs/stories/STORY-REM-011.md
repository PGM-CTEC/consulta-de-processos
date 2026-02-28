# STORY-REM-011: Add Log Rotation

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 | **Complexity:** 2 pts (XS - 30min) | **Priority:** MEDIUM
**Assignee:** Backend Developer | **Status:** Done

---

## Description

Configure Python logging with RotatingFileHandler (10 MB max, 5 backups) to prevent disk full.

## Acceptance Criteria

- [x] RotatingFileHandler configured (10 MB max)
- [x] 5 backup files retained (app.log, app.log.1-5)
- [x] Old logs deleted automatically
- [x] Test: 11 MB logs → 2 files created

## Implementation

```python
import logging
from logging.handlers import RotatingFileHandler

os.makedirs('logs', exist_ok=True)

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger()
logger.addHandler(handler)
```

## Files

- `backend/main.py` (modified)


## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-28 | @dev | Verificado: RotatingFileHandler (10MB, 5 backups) ja em utils/logger.py (REM-016) |
