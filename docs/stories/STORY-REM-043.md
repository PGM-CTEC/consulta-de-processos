# STORY-REM-043: Soft Deletes

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-010
**Type:** Database
**Complexity:** 3 pts (S - 1 day)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Implement soft delete pattern with deleted_at timestamp instead of hard deletes for data recovery and audit trail.

## Acceptance Criteria

- [ ] deleted_at column added to processes and movements tables
- [ ] DELETE operations replaced with UPDATE deleted_at = NOW()
- [ ] Queries exclude soft-deleted records by default
- [ ] Admin endpoint to view deleted records
- [ ] Restore functionality implemented
- [ ] Migration script created

## Technical Notes

```python
# backend/models.py
from sqlalchemy import Column, DateTime

class Process(Base):
    deleted_at = Column(DateTime, nullable=True)

    @classmethod
    def active(cls):
        return cls.query.filter(cls.deleted_at.is_(None))

# Soft delete
process.deleted_at = datetime.utcnow()
session.commit()

# Restore
process.deleted_at = None
session.commit()
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
