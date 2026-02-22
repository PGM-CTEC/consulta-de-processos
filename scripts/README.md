# Database Backup Scripts

Automated backup and restore scripts for SQLite database.

**Story:** REM-002 (DB-003)
**Created:** 2026-02-22

---

## 📋 Scripts

| Script | Description | Duration |
|--------|-------------|----------|
| `backup_db.sh` | Automated backup with integrity check, compression, and retention | ~5-10 seconds |
| `restore_database.sh` | Interactive restore with safety checks | ~10-30 seconds |

---

## 🚀 Quick Start

### Manual Backup

```bash
# Linux/Mac
cd scripts
bash backup_db.sh

# Windows (Git Bash / WSL)
cd scripts
bash backup_db.sh
```

### Manual Restore

```bash
cd scripts
bash restore_database.sh
# Follow interactive prompts
```

---

## ⏰ Automated Backups (Cron)

### Linux/Mac Setup

1. **Make scripts executable:**
   ```bash
   chmod +x scripts/backup_db.sh scripts/restore_database.sh
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add daily backup at 2 AM:**
   ```cron
   # Database backup - Daily at 2 AM
   0 2 * * * /path/to/consulta-processo/scripts/backup_db.sh >> /path/to/consulta-processo/logs/backup.log 2>&1
   ```

4. **Verify cron job:**
   ```bash
   crontab -l
   ```

### Windows Task Scheduler Setup

1. Open **Task Scheduler** (Win + R → `taskschd.msc`)

2. **Create Basic Task:**
   - Name: `Database Backup - Consulta Processo`
   - Trigger: Daily at 2:00 AM
   - Action: Start a program
   - Program: `C:\Program Files\Git\bin\bash.exe`
   - Arguments: `C:\Projetos\Consulta processo\scripts\backup_db.sh`
   - Start in: `C:\Projetos\Consulta processo`

3. **Enable logging:**
   - Edit task → Actions → Add arguments:
   ```
   C:\Projetos\Consulta processo\scripts\backup_db.sh >> C:\Projetos\Consulta processo\logs\backup.log 2>&1
   ```

---

## 📂 File Structure

```
consulta-processo/
├── scripts/
│   ├── backup_db.sh           # Backup script
│   ├── restore_database.sh    # Restore script
│   └── README.md              # This file
├── backups/                   # Backup storage (auto-created)
│   ├── backup_20260222_020000.db.gz
│   ├── backup_20260223_020000.db.gz
│   └── ...
├── logs/                      # Log files (auto-created)
│   ├── backup.log
│   └── restore.log
└── consulta_processual.db     # Main database
```

---

## 🔍 Backup Features

### Integrity Check
- Runs `PRAGMA integrity_check` before backup
- Fails if database is corrupted
- Ensures only valid backups are created

### Transaction-Safe
- Uses SQLite `.backup` command (CLI) or `backup()` API (Python)
- Guarantees consistent backup even during writes
- No database locking required

### Compression
- Gzip compression reduces backup size by ~70-90%
- Example: 10MB database → 1-3MB compressed

### Retention Policy
- Automatically deletes backups older than 30 days
- Configurable via `RETENTION_DAYS` variable
- Prevents disk space exhaustion

### Cross-Platform
- Works on Linux, Mac, Windows (Git Bash/WSL)
- Automatic fallback to Python if `sqlite3` CLI not available
- Colored output for better readability

---

## 🔄 Restore Features

### Interactive Selection
- Lists all available backups with dates and sizes
- User selects backup by number
- Type 'q' to cancel

### Safety Backup
- Creates `.pre-restore-YYYYMMDD_HHMMSS` backup of current database before restore
- Allows rollback if restore goes wrong

### Integrity Verification
- Verifies backup integrity before restore
- Fails if backup is corrupted
- Prevents data loss

### Record Count Display
- Shows number of processes after restore
- Quick sanity check

---

## 📊 Monitoring

### Check Backup Logs

```bash
# View last backup
tail -20 logs/backup.log

# Watch live backup
tail -f logs/backup.log

# View all backups today
grep "$(date +%Y-%m-%d)" logs/backup.log
```

### List All Backups

```bash
ls -lh backups/

# Output example:
# -rw-r--r-- 1 user group 2.1M Feb 22 02:00 backup_20260222_020000.db.gz
# -rw-r--r-- 1 user group 2.1M Feb 23 02:00 backup_20260223_020000.db.gz
```

### Calculate Disk Usage

```bash
du -sh backups/
# Output: 63M    backups/
```

---

## ⚙️ Configuration

### Change Retention Period

Edit `backup_db.sh`:

```bash
# Line 19
RETENTION_DAYS=30  # Change to desired days (e.g., 7, 60, 90)
```

### Change Backup Time

Edit crontab:

```cron
# Daily at 3 AM instead of 2 AM
0 3 * * * /path/to/backup_db.sh >> /path/to/logs/backup.log 2>&1

# Twice daily (2 AM and 2 PM)
0 2,14 * * * /path/to/backup_db.sh >> /path/to/logs/backup.log 2>&1

# Weekly on Sundays at 2 AM
0 2 * * 0 /path/to/backup_db.sh >> /path/to/logs/backup.log 2>&1
```

---

## 🧪 Testing

### Test Backup Script

```bash
# Run backup manually
bash scripts/backup_db.sh

# Expected output:
# [2026-02-22 15:30:00] =========================================
# [2026-02-22 15:30:00] Starting database backup
# [2026-02-22 15:30:00] =========================================
# [2026-02-22 15:30:00] Database file: /path/to/consulta_processual.db
# [2026-02-22 15:30:00] Backup destination: /path/to/backups/backup_20260222_153000.db
# [2026-02-22 15:30:01] Step 1: Running integrity check...
# [SUCCESS] Integrity check passed
# [2026-02-22 15:30:02] Step 2: Creating backup...
# [SUCCESS] Backup created: 10M
# [2026-02-22 15:30:03] Step 3: Compressing backup...
# [SUCCESS] Backup compressed: 2.1M
# [2026-02-22 15:30:03] Step 4: Cleaning up old backups (30-day retention)...
# [2026-02-22 15:30:03] No old backups to delete
# [2026-02-22 15:30:03] =========================================
# [SUCCESS] Backup completed successfully!
# [2026-02-22 15:30:03] =========================================
# [2026-02-22 15:30:03] Backup file: backup_20260222_153000.db.gz
# [2026-02-22 15:30:03] Compressed size: 2.1M
# [2026-02-22 15:30:03] Total backups: 5
# [2026-02-22 15:30:03] =========================================
```

### Test Restore Script

```bash
# Run restore interactively
bash scripts/restore_database.sh

# Expected output:
# [2026-02-22 15:35:00] =========================================
# [2026-02-22 15:35:00] Database Restore Utility
# [2026-02-22 15:35:00] =========================================
# [INFO] Available backups:
# [0] backup_20260222_153000.db.gz (2.1M) - 2026-02-22 15:30:00
# [1] backup_20260221_020000.db.gz (2.0M) - 2026-02-21 02:00:00
# [2] backup_20260220_020000.db.gz (1.9M) - 2026-02-20 02:00:00
#
# Enter backup number to restore (or 'q' to quit): 0
# [INFO] Selected backup: backup_20260222_153000.db.gz
# [WARNING] WARNING: This will replace the current database!
# [INFO] Current database size: 10M
# Are you sure you want to continue? (type 'yes' to confirm): yes
# ...
# [SUCCESS] Database restored successfully!
```

---

## 🐛 Troubleshooting

### Error: "sqlite3: command not found"

**Solution:** Scripts automatically fall back to Python. Ensure Python 3 is installed:

```bash
python3 --version
# Python 3.x.x
```

### Error: "Permission denied"

**Solution:** Make scripts executable:

```bash
chmod +x scripts/*.sh
```

### Error: "No space left on device"

**Solution:** Delete old backups manually or reduce retention period:

```bash
# Delete backups older than 7 days manually
find backups/ -name "backup_*.db.gz" -mtime +7 -delete

# Or edit RETENTION_DAYS in backup_db.sh
```

### Cron job not running

**Solution:** Check cron service and logs:

```bash
# Check if cron is running
sudo systemctl status cron  # Linux
sudo launchctl list | grep cron  # Mac

# View cron logs
grep CRON /var/log/syslog  # Linux
tail -f /var/log/system.log | grep cron  # Mac
```

---

## 📝 Maintenance

### Monthly Health Check

```bash
# 1. Verify backups exist
ls -lh backups/ | tail -5

# 2. Check latest backup log
tail -50 logs/backup.log

# 3. Test restore (dry run)
bash scripts/restore_database.sh
# Type 'q' to quit without restoring
```

### Disaster Recovery Test

**Quarterly (every 3 months):**

1. Create test database copy
2. Restore from oldest backup
3. Verify data integrity
4. Document results

---

## 🔒 Security Notes

- Backup files contain **sensitive data** (process numbers, movements)
- Store backups in **secure location** (encrypted drive, private cloud)
- **DO NOT** commit backups to git (.gitignore already configured)
- Consider encrypting backups for production:
  ```bash
  # Encrypt backup
  gpg -c backup_20260222_020000.db.gz

  # Decrypt backup
  gpg backup_20260222_020000.db.gz.gpg
  ```

---

## 📚 References

- SQLite Backup API: https://www.sqlite.org/backup.html
- Cron Syntax: https://crontab.guru/
- **Story REM-002**: [docs/stories/epics/EPIC-BROWNFIELD-REMEDIATION.md](../docs/stories/epics/EPIC-BROWNFIELD-REMEDIATION.md#story-rem-002)

---

**Last Updated:** 2026-02-22
**Maintainer:** DevOps Team
