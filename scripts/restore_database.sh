#!/bin/bash

# Restore Script for Consulta Processo Database
# Purpose: Restore database from backup
# Usage: ./restore_database.sh <backup_file.db.gz>
# Example: ./restore_database.sh backups/backup_20260224_020000.db.gz

set -e

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.db.gz>"
    echo "Example: $0 backups/backup_20260224_020000.db.gz"
    echo ""
    echo "Available backups:"
    ls -lh backups/backup_*.db.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
DB_FILE="consulta_processual.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Check if backup exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Verify it's a gzip file
if ! gzip -t "$BACKUP_FILE" 2>/dev/null; then
    echo "ERROR: File is not a valid gzip archive"
    exit 1
fi

# Create backup of current database
if [ -f "$DB_FILE" ]; then
    echo "Backing up current database to ${DB_FILE}.backup-${TIMESTAMP}"
    cp "$DB_FILE" "${DB_FILE}.backup-${TIMESTAMP}"
fi

# Decompress and restore
echo "Extracting backup..."
TEMP_DB=$(mktemp)
gunzip -c "$BACKUP_FILE" > "$TEMP_DB"

# Verify integrity
echo "Verifying backup integrity..."
INTEGRITY=$(sqlite3 "$TEMP_DB" "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
    echo "ERROR: Backup integrity check failed: $INTEGRITY"
    rm "$TEMP_DB"
    exit 1
fi

# Restore
echo "Restoring database..."
cp "$TEMP_DB" "$DB_FILE"
rm "$TEMP_DB"

echo "SUCCESS: Database restored from $BACKUP_FILE"
echo "Previous database backed up to: ${DB_FILE}.backup-${TIMESTAMP}"
