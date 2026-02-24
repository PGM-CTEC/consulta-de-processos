#!/bin/bash

# Backup Script for Consulta Processo Database
# Purpose: Daily automated SQLite backup with integrity checks and retention policy
# Usage: ./backup_db.sh
# Cron: 0 2 * * * /path/to/backup_db.sh >> /path/to/logs/backup.log 2>&1

set -e  # Exit on error

# Configuration
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_FILE="consulta_processual.db"
BACKUP_DIR="backups"
LOG_FILE="logs/backup.log"
RETENTION_DAYS=30

# Create directories if they don't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Function: Log message
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function: Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Start backup
log "Starting database backup..."

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    error_exit "Database file not found: $DB_FILE"
fi

# Step 1: Integrity check
log "Running integrity check..."
INTEGRITY_RESULT=$(sqlite3 "$DB_FILE" "PRAGMA integrity_check;" 2>&1)
if [ "$INTEGRITY_RESULT" != "ok" ]; then
    error_exit "Database integrity check failed: $INTEGRITY_RESULT"
fi
log "Integrity check passed"

# Step 2: Create backup
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.db"
log "Creating backup: $BACKUP_FILE"

sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"
if [ ! -f "$BACKUP_FILE" ]; then
    error_exit "Backup creation failed"
fi
log "Backup created successfully"

# Step 3: Compress backup
log "Compressing backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"
if [ ! -f "$BACKUP_FILE_GZ" ]; then
    error_exit "Compression failed"
fi
log "Backup compressed: $BACKUP_FILE_GZ"

# Step 4: Cleanup old backups (retention: 30 days)
log "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "backup_*.db.gz" -mtime +$RETENTION_DAYS -delete
log "Cleanup completed"

# Step 5: Verify backup integrity
log "Verifying backup integrity..."
if gzip -t "$BACKUP_FILE_GZ" 2>/dev/null; then
    log "Backup integrity verified"
else
    error_exit "Backup integrity verification failed"
fi

# Summary
BACKUP_SIZE=$(du -h "$BACKUP_FILE_GZ" | cut -f1)
log "Backup completed successfully. Size: $BACKUP_SIZE"
log "---"
