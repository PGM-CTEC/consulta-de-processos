#!/bin/bash

################################################################################
# Database Restore Script for SQLite
#
# Restores database from a gzipped backup file
#
# Usage: ./restore_database.sh [backup_file]
# 
# Example:
# ./restore_database.sh backups/backup_20260223_143500.db.gz
#
# Or interactive:
# ./restore_database.sh  (will list available backups)
#
################################################################################

set -e

BACKUP_DIR="backups"
RESTORE_DB="consulta_processual_restored.db"

# Function to display usage
usage() {
    echo "Usage: $0 [backup_file]"
    echo ""
    echo "Examples:"
    echo "  $0                                           # Interactive mode (list backups)"
    echo "  $0 backups/backup_20260223_143500.db.gz    # Restore specific backup"
    exit 1
}

# Function to restore from backup
restore_backup() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        echo "ERROR: Backup file not found: $backup_file"
        exit 1
    fi
    
    echo "=== Database Restore Started ==="
    echo "Backup file: $backup_file"
    echo "Restore file: $RESTORE_DB"
    echo ""
    
    # Ask for confirmation
    read -p "Proceed with restore? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Restore cancelled."
        exit 0
    fi
    
    echo "Decompressing and restoring..."
    gunzip -c "$backup_file" > "$RESTORE_DB"
    
    echo "Verifying restored database..."
    INTEGRITY=$(sqlite3 "$RESTORE_DB" "PRAGMA integrity_check;")
    if [ "$INTEGRITY" != "ok" ]; then
        echo "ERROR: Restored database failed integrity check!"
        echo "Integrity check result: $INTEGRITY"
        rm -f "$RESTORE_DB"
        exit 1
    fi
    
    echo ""
    echo "SUCCESS! Database restored to: $RESTORE_DB"
    echo ""
    echo "To use the restored database:"
    echo "  1. Stop the application"
    echo "  2. Backup current: mv consulta_processual.db consulta_processual_old.db"
    echo "  3. Use restored: mv $RESTORE_DB consulta_processual.db"
    echo "  4. Restart application"
    echo ""
    echo "=== Database Restore Completed ==="
}

# Main logic
if [ -z "$1" ]; then
    # Interactive mode - list available backups
    echo "=== Available Database Backups ==="
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ]; then
        echo "No backups directory found"
        usage
    fi
    
    BACKUPS=$(find "$BACKUP_DIR" -name "backup_*.db.gz" -type f | sort -r)
    
    if [ -z "$BACKUPS" ]; then
        echo "No backups found in $BACKUP_DIR"
        usage
    fi
    
    # Display backups with numbers
    i=1
    declare -a backup_array
    while IFS= read -r backup; do
        size=$(du -h "$backup" | cut -f1)
        mtime=$(date -r "$backup" '+%Y-%m-%d %H:%M:%S')
        echo "[$i] $backup ($size) - $mtime"
        backup_array[$i]="$backup"
        i=$((i+1))
    done <<< "$BACKUPS"
    
    echo ""
    read -p "Select backup number to restore (or q to quit): " choice
    
    if [ "$choice" = "q" ] || [ "$choice" = "Q" ]; then
        echo "Cancelled."
        exit 0
    fi
    
    if [ -z "${backup_array[$choice]}" ]; then
        echo "Invalid selection"
        exit 1
    fi
    
    restore_backup "${backup_array[$choice]}"
else
    # Restore from provided backup file
    restore_backup "$1"
fi

exit 0
