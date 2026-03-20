#!/bin/bash
# backup_db.sh — Automated SQLite backup with integrity check and retention policy
# Story: REM-002 — Implement Automated Database Backup
#
# Usage:
#   ./scripts/backup_db.sh
#   DB_FILE=/path/to/db.sqlite BACKUP_DIR=/mnt/backups ./scripts/backup_db.sh
#
# Cron (daily at 2 AM):
#   0 2 * * * /opt/consulta-processo/scripts/backup_db.sh >> /opt/consulta-processo/logs/backup.log 2>&1

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

DB_FILE="${DB_FILE:-$PROJECT_ROOT/consulta_processual.db}"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"
LOG_DIR="${LOG_DIR:-$PROJECT_ROOT/logs}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

BACKUP_NAME="backup_${TIMESTAMP}.db"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

mkdir -p "$BACKUP_DIR" "$LOG_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "=== Backup iniciado: $DB_FILE ==="

if [[ ! -f "$DB_FILE" ]]; then
    log "ERRO: Banco nao encontrado: $DB_FILE"
    exit 1
fi

log "Verificando integridade..."
INTEGRITY=$(sqlite3 "$DB_FILE" "PRAGMA integrity_check;" 2>&1)
if [[ "$INTEGRITY" != "ok" ]]; then
    log "ERRO: Falha na integridade: $INTEGRITY"
    exit 1
fi
log "Integridade OK"

log "Criando backup: $BACKUP_PATH"
sqlite3 "$DB_FILE" ".backup '$BACKUP_PATH'"

gzip "$BACKUP_PATH"
COMPRESSED_PATH="${BACKUP_PATH}.gz"
SIZE=$(du -sh "$COMPRESSED_PATH" | cut -f1)
log "Backup comprimido: ${COMPRESSED_PATH} (${SIZE})"

log "Limpando backups com mais de ${RETENTION_DAYS} dias..."
DELETED=$(find "$BACKUP_DIR" -name "backup_*.db.gz" -mtime "+${RETENTION_DAYS}" -print -delete | wc -l)
log "Removidos: $DELETED arquivo(s)"

TOTAL=$(find "$BACKUP_DIR" -name "backup_*.db.gz" | wc -l)
log "=== Backup concluido. Total: $TOTAL backups ==="
