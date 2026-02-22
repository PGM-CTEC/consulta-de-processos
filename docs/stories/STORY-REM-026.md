# STORY-REM-026: Audit Trail for LGPD Compliance

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** DB-005
**Type:** Compliance
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Data Engineer
**Status:** Ready
**Sprint:** Sprint 4

## Description

Create audit_log table with SQLAlchemy event listeners to track INSERT/UPDATE/DELETE for LGPD compliance.

## Acceptance Criteria

- [ ] audit_log table created (table_name, record_id, action, old_values, new_values, timestamp)
- [ ] SQLAlchemy event listeners for Process and Movement tables
- [ ] Test: INSERT process → audit_log entry created
- [ ] Test: UPDATE process → audit_log with old/new values
- [ ] Test: DELETE process → audit_log with old values
- [ ] Admin endpoint to view audit log (optional)

## Technical Notes

```python
# backend/models.py
from sqlalchemy import event
from datetime import datetime

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50))
    record_id = Column(Integer)
    action = Column(String(10))  # INSERT, UPDATE, DELETE
    old_values = Column(JSON)
    new_values = Column(JSON)
    user_id = Column(String)  # Future: from auth system
    timestamp = Column(DateTime, default=datetime.utcnow)

# Event listeners
@event.listens_for(Process, 'after_insert')
def log_process_insert(mapper, connection, target):
    connection.execute(
        AuditLog.__table__.insert(),
        {"table_name": "processes", "record_id": target.id, "action": "INSERT", "new_values": target.to_dict()}
    )

@event.listens_for(Process, 'after_update')
def log_process_update(mapper, connection, target):
    # Use SQLAlchemy history to get old values
    old_values = {k: v[0] for k, v in inspect(target).attrs.items() if v.history.has_changes()}
    connection.execute(
        AuditLog.__table__.insert(),
        {"table_name": "processes", "record_id": target.id, "action": "UPDATE", "old_values": old_values, "new_values": target.to_dict()}
    )
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
