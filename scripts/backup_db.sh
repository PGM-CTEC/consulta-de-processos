#!/bin/bash
#############################################
# Database Backup Script
# Story: REM-002 (DB-003)
# Description: Automated SQLite backup with integrity checks and 30-day retention
#############################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Use relative paths from project root
cd "$PROJECT_ROOT" || exit 1

DB_FILE="consulta_processual.db"
BACKUP_DIR="backups"
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/backup.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.db"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Create necessary directories
mkdir -p "$BACKUP_DIR" "$LOG_DIR"

log "========================================="
log "Starting database backup"
log "========================================="

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    log_error "Database file not found: $DB_FILE"
    exit 1
fi

log "Database file: $DB_FILE"
log "Backup destination: $BACKUP_FILE"

# Step 1: Integrity check
log "Step 1: Running integrity check..."
if command -v sqlite3 &> /dev/null; then
    # Use sqlite3 CLI if available
    INTEGRITY_RESULT=$(sqlite3 "$DB_FILE" "PRAGMA integrity_check;" 2>&1)
    if [ "$INTEGRITY_RESULT" != "ok" ]; then
        log_error "Database integrity check FAILED!"
        log_error "Result: $INTEGRITY_RESULT"
        exit 1
    fi
    log_success "Integrity check passed"
else
    # Fallback to Python if sqlite3 not available
    log_warning "sqlite3 command not found, using Python fallback..."
    python3 -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('$DB_FILE')
    cursor = conn.cursor()
    result = cursor.execute('PRAGMA integrity_check;').fetchone()[0]
    conn.close()
    if result != 'ok':
        print(f'FAIL: {result}')
        sys.exit(1)
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
    " || exit 1
    log_success "Integrity check passed (Python)"
fi

# Step 2: Create backup
log "Step 2: Creating backup..."
if command -v sqlite3 &> /dev/null; then
    # Use sqlite3 .backup command (transaction-safe)
    sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'" || {
        log_error "Backup failed!"
        exit 1
    }
else
    # Fallback to Python (also transaction-safe)
    python3 -c "
import sqlite3
import shutil
try:
    # SQLite backup API (transaction-safe)
    source = sqlite3.connect('$DB_FILE')
    dest = sqlite3.connect('$BACKUP_FILE')
    source.backup(dest)
    source.close()
    dest.close()
    print('Backup created successfully')
except Exception as e:
    print(f'Backup failed: {e}')
    import sys
    sys.exit(1)
    " || exit 1
fi

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log_success "Backup created: $BACKUP_SIZE"

# Step 3: Compress backup
log "Step 3: Compressing backup..."
gzip -f "$BACKUP_FILE" || {
    log_error "Compression failed!"
    exit 1
}
COMPRESSED_FILE="${BACKUP_FILE}.gz"
COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
log_success "Backup compressed: $COMPRESSED_SIZE"

# Step 4: Cleanup old backups (30-day retention)
log "Step 4: Cleaning up old backups (${RETENTION_DAYS}-day retention)..."
DELETED_COUNT=0
if command -v find &> /dev/null; then
    # Use find command
    DELETED_COUNT=$(find "$BACKUP_DIR" -name "backup_*.db.gz" -mtime +${RETENTION_DAYS} -type f 2>/dev/null | wc -l)
    find "$BACKUP_DIR" -name "backup_*.db.gz" -mtime +${RETENTION_DAYS} -type f -delete 2>/dev/null || true
else
    # Fallback to Python
    DELETED_COUNT=$(python3 -c "
import os
import time
from pathlib import Path

backup_dir = Path('$BACKUP_DIR')
cutoff = time.time() - (${RETENTION_DAYS} * 86400)
deleted = 0

for backup_file in backup_dir.glob('backup_*.db.gz'):
    if backup_file.stat().st_mtime < cutoff:
        backup_file.unlink()
        deleted += 1
print(deleted)
    ")
fi

if [ "$DELETED_COUNT" -gt 0 ]; then
    log_success "Deleted $DELETED_COUNT old backup(s)"
else
    log "No old backups to delete"
fi

# Step 5: Summary
log "========================================="
log_success "Backup completed successfully!"
log "========================================="
log "Backup file: $(basename "$COMPRESSED_FILE")"
log "Compressed size: $COMPRESSED_SIZE"
log "Total backups: $(ls -1 "$BACKUP_DIR"/backup_*.db.gz 2>/dev/null | wc -l)"
log "========================================="

exit 0
