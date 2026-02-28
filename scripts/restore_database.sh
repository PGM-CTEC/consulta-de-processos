#!/bin/bash
# restore_database.sh — Restore SQLite database from a compressed backup
# Story: REM-002 — Implement Automated Database Backup
#
# Usage:
#   ./scripts/restore_database.sh backups/backup_20260228_020000.db.gz
#   ./scripts/restore_database.sh  # lists available backups

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_FILE="${DB_FILE:-$PROJECT_ROOT/consulta_processual.db}"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

if [[ $# -eq 0 ]]; then
    echo "Backups disponiveis:"
    echo "----------------------------------------------------"
    if compgen -G "$BACKUP_DIR/backup_*.db.gz" > /dev/null 2>&1; then
        ls -lh "$BACKUP_DIR"/backup_*.db.gz | awk '{print NR".", $NF, $5, $6, $7, $8}'
    else
        echo "  Nenhum backup encontrado em: $BACKUP_DIR"
    fi
    echo ""
    echo "Uso: $0 <arquivo-backup.db.gz>"
    exit 0
fi

BACKUP_FILE="$1"
if [[ ! "$BACKUP_FILE" = /* ]]; then
    BACKUP_FILE="$PROJECT_ROOT/$BACKUP_FILE"
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
    log "ERRO: Backup nao encontrado: $BACKUP_FILE"
    exit 1
fi

log "=== Restauracao: $BACKUP_FILE => $DB_FILE ==="
echo ""
echo "  ATENCAO: O banco atual sera substituido."
read -r -p "  Continuar? [s/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
    log "Restauracao cancelada."
    exit 0
fi

if [[ -f "$DB_FILE" ]]; then
    SAFETY_BACKUP="${DB_FILE}.before-restore-$(date +%Y%m%d_%H%M%S).bak"
    cp "$DB_FILE" "$SAFETY_BACKUP"
    log "Banco atual salvo em: $SAFETY_BACKUP"
fi

TEMP_DB=$(mktemp /tmp/consulta_restore_XXXXXX.db)
log "Descomprimindo..."
gunzip -c "$BACKUP_FILE" > "$TEMP_DB"

log "Verificando integridade do backup..."
INTEGRITY=$(sqlite3 "$TEMP_DB" "PRAGMA integrity_check;" 2>&1)
if [[ "$INTEGRITY" != "ok" ]]; then
    rm -f "$TEMP_DB"
    log "ERRO: Backup corrompido: $INTEGRITY"
    exit 1
fi

cp "$TEMP_DB" "$DB_FILE"
rm -f "$TEMP_DB"

RECORDS=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM processes;" 2>/dev/null || echo "N/A")
log "=== Restauracao concluida. Processos: $RECORDS ==="
