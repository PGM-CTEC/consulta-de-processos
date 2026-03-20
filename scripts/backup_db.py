#!/usr/bin/env python3

"""
Backup Script for Consulta Processo Database
Purpose: Daily automated SQLite backup with integrity checks and retention policy
Usage: python backup_db.py
"""

import sqlite3
import shutil
import gzip
import os
import sys
from datetime import datetime
from pathlib import Path
import glob

# Configuration
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
DB_FILE = 'consulta_processual.db'
BACKUP_DIR = 'backups'
LOG_FILE = 'logs/backup.log'
RETENTION_DAYS = 30

# Create directories
Path(BACKUP_DIR).mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)

def log(message):
    """Log message to file and stdout"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{timestamp}] {message}'
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def error_exit(message):
    """Log error and exit"""
    log(f'ERROR: {message}')
    sys.exit(1)

def main():
    log('Starting database backup...')
    
    # Check database exists
    if not os.path.exists(DB_FILE):
        error_exit(f'Database file not found: {DB_FILE}')
    
    try:
        # Step 1: Integrity check
        log('Running integrity check...')
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('PRAGMA integrity_check')
        result = cursor.fetchone()[0]
        conn.close()
        
        if result != 'ok':
            error_exit(f'Database integrity check failed: {result}')
        log('Integrity check passed')
        
        # Step 2: Create backup
        backup_file = os.path.join(BACKUP_DIR, f'backup_{TIMESTAMP}.db')
        log(f'Creating backup: {backup_file}')
        shutil.copy2(DB_FILE, backup_file)
        log('Backup created successfully')
        
        # Step 3: Compress backup
        log('Compressing backup...')
        backup_file_gz = f'{backup_file}.gz'
        with open(backup_file, 'rb') as f_in:
            with gzip.open(backup_file_gz, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(backup_file)  # Remove uncompressed file
        log(f'Backup compressed: {backup_file_gz}')
        
        # Step 4: Cleanup old backups
        log(f'Cleaning up backups older than {RETENTION_DAYS} days...')
        now = datetime.now()
        deleted_count = 0
        for backup in glob.glob(os.path.join(BACKUP_DIR, 'backup_*.db.gz')):
            file_time = datetime.fromtimestamp(os.path.getmtime(backup))
            if (now - file_time).days > RETENTION_DAYS:
                os.remove(backup)
                deleted_count += 1
        log(f'Deleted {deleted_count} old backup(s)')
        
        # Step 5: Verify backup integrity
        log('Verifying backup integrity...')
        try:
            with gzip.open(backup_file_gz, 'rb') as f:
                f.read(1)
            log('Backup integrity verified')
        except Exception as e:
            error_exit(f'Backup integrity verification failed: {e}')
        
        # Summary
        backup_size = os.path.getsize(backup_file_gz) / (1024 * 1024)
        log(f'Backup completed successfully. Size: {backup_size:.2f} MB')
        log('---')
        
    except Exception as e:
        error_exit(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()
