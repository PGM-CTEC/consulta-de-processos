# STORY-REM-002: Implement Automated Database Backup

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Sprint:** Sprint 6 (Remediation)
**Type:** Operations / Reliability
**Complexity:** 3 pts (S - 2 hours)
**Priority:** HIGH
**Assignee:** DevOps Engineer
**Status:** Ready

---

## Description

Create bash script for daily automated SQLite backup with integrity checks, 30-day retention, and cron scheduling.

---

## Acceptance Criteria

- [ ] Script `scripts/backup_db.sh` created
- [ ] Backup uses `.backup` command (transaction-safe)
- [ ] Gzip compression applied
- [ ] Integrity check (PRAGMA integrity_check) runs before backup
- [ ] 30-day retention policy (old backups auto-deleted)
- [ ] Cron job configured (daily 2 AM)
- [ ] Manual restore script `scripts/restore_database.sh` tested

---

## Implementation

### backup_db.sh

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_FILE="consulta_processual.db"
BACKUP_DIR="backups"

mkdir -p $BACKUP_DIR
mkdir -p logs

# Integrity check
sqlite3 $DB_FILE "PRAGMA integrity_check;" || exit 1

# Backup + compress
sqlite3 $DB_FILE ".backup '$BACKUP_DIR/backup_${TIMESTAMP}.db'"
gzip $BACKUP_DIR/backup_${TIMESTAMP}.db

# Cleanup old backups (30 days)
find $BACKUP_DIR -name "backup_*.db.gz" -mtime +30 -delete
```

### Cron Setup

```
0 2 * * * /path/to/backup_db.sh >> /path/to/logs/backup.log 2>&1
```

---

## Files

- `scripts/backup_db.sh` (new)
- `scripts/restore_database.sh` (new)

---

## Dev Tasks

- [ ] Create backup script
- [ ] Create restore script
- [ ] Test backup/restore cycle
- [ ] Configure cron job
