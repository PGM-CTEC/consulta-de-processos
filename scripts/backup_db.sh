#!/bin/bash

################################################################################
# Database Backup Script for SQLite
#
# Automated daily backup with:
# - Integrity check before backup
# - Gzip compression
# - 30-day retention policy
# - Transaction-safe backup
#
# Usage: ./backup_db.sh
# 
# Cron setup (daily 2 AM):
# 0 2 * * * /path/to/consulta-processo/scripts/backup_db.sh >> /path/to/logs/backup.log 2>&1
#
################################################################################

set -e

# Configuration
DB_FILE="consulta_processual.db"
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/backup.log"
RETENTION_DAYS=30

# Create directories if needed
mkdir -p "$BACKUP_DIR" "logs"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Database Backup Started ==="

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    log "ERROR: Database file not found: $DB_FILE"
    exit 1
fi

# Integrity check before backup
log "Running integrity check..."
INTEGRITY=$(sqlite3 "$DB_FILE" "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
    log "ERROR: Database integrity check failed: $INTEGRITY"
    exit 1
fi
log "Database integrity: OK"

# Perform backup (transaction-safe)
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.db"
log "Creating backup: $BACKUP_FILE"

sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"

if [ ! -f "$BACKUP_FILE" ]; then
    log "ERROR: Backup file was not created"
    exit 1
fi

# Compress backup
log "Compressing backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

if [ ! -f "$BACKUP_FILE_GZ" ]; then
    log "ERROR: Compressed backup not created"
    exit 1
fi

# Get file size
SIZE=$(du -h "$BACKUP_FILE_GZ" | cut -f1)
log "Backup created successfully: $BACKUP_FILE_GZ ($SIZE)"

# Cleanup old backups (retention policy)
log "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
DELETED=$(find "$BACKUP_DIR" -name "backup_*.db.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
log "Deleted $DELETED old backup(s)"

# Summary
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "backup_*.db.gz" | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Current backups: $BACKUP_COUNT files ($TOTAL_SIZE total)"

log "=== Database Backup Completed Successfully ==="

exit 0
