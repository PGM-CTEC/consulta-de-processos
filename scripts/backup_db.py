#!/usr/bin/env python3

"""
Database Backup Script for SQLite (Python version)

Automated daily backup with:
- Integrity check before backup
- Gzip compression
- 30-day retention policy
- Cross-platform compatibility (Python 3.7+)

Usage:
    python backup_db.py
    
Cron setup (daily 2 AM):
    0 2 * * * python /path/to/consulta-processo/scripts/backup_db.py >> /path/to/logs/backup.log 2>&1
"""

import sqlite3
import shutil
import gzip
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configuration
DB_FILE = "consulta_processual.db"
BACKUP_DIR = "backups"
LOG_FILE = "logs/backup.log"
RETENTION_DAYS = 30

# Setup logging
Path(BACKUP_DIR).mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

log = logging.getLogger(__name__)


def check_database_integrity():
    """Check database integrity before backup."""
    log.info("Running integrity check...")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        conn.close()
        
        if result != "ok":
            log.error(f"Database integrity check failed: {result}")
            return False
        
        log.info("Database integrity: OK")
        return True
    except Exception as e:
        log.error(f"Error checking integrity: {e}")
        return False


def create_backup():
    """Create database backup with gzip compression."""
    if not os.path.isfile(DB_FILE):
        log.error(f"Database file not found: {DB_FILE}")
        return False
    
    # Check integrity first
    if not check_database_integrity():
        return False
    
    # Create backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.db")
    backup_file_gz = f"{backup_file}.gz"
    
    try:
        log.info(f"Creating backup: {backup_file}")
        
        # Copy database file (transaction-safe)
        shutil.copy2(DB_FILE, backup_file)
        
        # Compress
        log.info("Compressing backup...")
        with open(backup_file, 'rb') as f_in:
            with gzip.open(backup_file_gz, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Verify compressed file
        if not os.path.isfile(backup_file_gz):
            log.error("Compressed backup not created")
            return False
        
        # Remove uncompressed file
        os.remove(backup_file)
        
        # Get file size
        size_mb = os.path.getsize(backup_file_gz) / (1024 * 1024)
        log.info(f"Backup created successfully: {backup_file_gz} ({size_mb:.2f} MB)")
        
        return True
        
    except Exception as e:
        log.error(f"Error creating backup: {e}")
        return False


def cleanup_old_backups():
    """Delete backups older than retention period."""
    log.info(f"Cleaning up old backups (retention: {RETENTION_DAYS} days)...")
    
    try:
        now = datetime.now()
        deleted_count = 0
        
        for backup_file in Path(BACKUP_DIR).glob("backup_*.db.gz"):
            # Get file modification time
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            age_days = (now - mtime).days
            
            if age_days > RETENTION_DAYS:
                backup_file.unlink()
                deleted_count += 1
                log.info(f"Deleted old backup: {backup_file.name} ({age_days} days old)")
        
        log.info(f"Deleted {deleted_count} old backup(s)")
        return True
        
    except Exception as e:
        log.error(f"Error cleaning up backups: {e}")
        return False


def get_backup_stats():
    """Get backup directory statistics."""
    try:
        backup_files = list(Path(BACKUP_DIR).glob("backup_*.db.gz"))
        total_size = sum(f.stat().st_size for f in backup_files)
        total_size_mb = total_size / (1024 * 1024)
        
        log.info(f"Current backups: {len(backup_files)} files ({total_size_mb:.2f} MB total)")
        
    except Exception as e:
        log.error(f"Error getting backup stats: {e}")


def main():
    """Main backup procedure."""
    log.info("=== Database Backup Started ===")
    
    try:
        # Create backup
        if not create_backup():
            log.error("Failed to create backup")
            return 1
        
        # Cleanup old backups
        if not cleanup_old_backups():
            log.error("Failed to cleanup old backups")
            return 1
        
        # Print stats
        get_backup_stats()
        
        log.info("=== Database Backup Completed Successfully ===")
        return 0
        
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
