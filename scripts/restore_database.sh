#!/bin/bash
#############################################
# Database Restore Script
# Story: REM-002 (DB-003)
# Description: Restore SQLite database from backup with safety checks
#############################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_FILE="$PROJECT_ROOT/consulta_processual.db"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/restore.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
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

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Create log directory
mkdir -p "$LOG_DIR"

log "========================================="
log "Database Restore Utility"
log "========================================="

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    log_error "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# List available backups
log_info "Available backups:"
BACKUPS=($(ls -1t "$BACKUP_DIR"/backup_*.db.gz 2>/dev/null || true))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    log_error "No backup files found in $BACKUP_DIR"
    exit 1
fi

# Display backups with index
for i in "${!BACKUPS[@]}"; do
    BACKUP_FILE="${BACKUPS[$i]}"
    BACKUP_NAME=$(basename "$BACKUP_FILE")
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    BACKUP_DATE=$(stat -c %y "$BACKUP_FILE" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$BACKUP_FILE" 2>/dev/null || echo "Unknown")
    echo -e "${CYAN}[$i]${NC} $BACKUP_NAME ($BACKUP_SIZE) - $BACKUP_DATE"
done

# Prompt user to select backup
echo ""
read -p "Enter backup number to restore (or 'q' to quit): " SELECTION

if [ "$SELECTION" = "q" ] || [ "$SELECTION" = "Q" ]; then
    log "Restore cancelled by user"
    exit 0
fi

# Validate selection
if ! [[ "$SELECTION" =~ ^[0-9]+$ ]] || [ "$SELECTION" -ge ${#BACKUPS[@]} ]; then
    log_error "Invalid selection: $SELECTION"
    exit 1
fi

SELECTED_BACKUP="${BACKUPS[$SELECTION]}"
log_info "Selected backup: $(basename "$SELECTED_BACKUP")"

# Safety confirmation
log_warning "WARNING: This will replace the current database!"
if [ -f "$DB_FILE" ]; then
    CURRENT_SIZE=$(du -h "$DB_FILE" | cut -f1)
    log_info "Current database size: $CURRENT_SIZE"
fi

read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log "Restore cancelled by user"
    exit 0
fi

log "========================================="
log "Starting database restore..."
log "========================================="

# Step 1: Backup current database (if exists)
if [ -f "$DB_FILE" ]; then
    SAFETY_BACKUP="${DB_FILE}.pre-restore-$(date +%Y%m%d_%H%M%S)"
    log "Step 1: Creating safety backup of current database..."
    cp "$DB_FILE" "$SAFETY_BACKUP" || {
        log_error "Failed to create safety backup!"
        exit 1
    }
    log_success "Safety backup created: $(basename "$SAFETY_BACKUP")"
else
    log_info "No existing database to backup"
fi

# Step 2: Decompress backup
log "Step 2: Decompressing backup..."
TEMP_BACKUP="${SELECTED_BACKUP%.gz}"
gunzip -c "$SELECTED_BACKUP" > "$TEMP_BACKUP" || {
    log_error "Failed to decompress backup!"
    exit 1
}
log_success "Backup decompressed"

# Step 3: Verify integrity of backup
log "Step 3: Verifying backup integrity..."
if command -v sqlite3 &> /dev/null; then
    INTEGRITY_RESULT=$(sqlite3 "$TEMP_BACKUP" "PRAGMA integrity_check;" 2>&1)
    if [ "$INTEGRITY_RESULT" != "ok" ]; then
        log_error "Backup integrity check FAILED!"
        log_error "Result: $INTEGRITY_RESULT"
        rm -f "$TEMP_BACKUP"
        exit 1
    fi
    log_success "Backup integrity verified"
else
    python3 -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('$TEMP_BACKUP')
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
    " || {
        log_error "Backup integrity check FAILED!"
        rm -f "$TEMP_BACKUP"
        exit 1
    }
    log_success "Backup integrity verified (Python)"
fi

# Step 4: Replace database
log "Step 4: Replacing database..."
mv "$TEMP_BACKUP" "$DB_FILE" || {
    log_error "Failed to replace database!"
    rm -f "$TEMP_BACKUP"
    exit 1
}
log_success "Database replaced"

# Step 5: Verify restored database
log "Step 5: Verifying restored database..."
if command -v sqlite3 &> /dev/null; then
    RECORD_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM processes;" 2>&1)
    log_info "Restored database contains $RECORD_COUNT processes"
else
    python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_FILE')
count = conn.execute('SELECT COUNT(*) FROM processes').fetchone()[0]
conn.close()
print(f'Restored database contains {count} processes')
    "
fi

# Summary
log "========================================="
log_success "Database restored successfully!"
log "========================================="
log "Restored from: $(basename "$SELECTED_BACKUP")"
if [ -n "${SAFETY_BACKUP:-}" ]; then
    log "Safety backup: $(basename "$SAFETY_BACKUP")"
    log_info "You can delete the safety backup if restore is confirmed working"
fi
log "========================================="

exit 0
