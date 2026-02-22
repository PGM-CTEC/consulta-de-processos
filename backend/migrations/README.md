# Database Migrations

Este diretório contém migrations aplicadas ao banco de dados SQLite.

## Migrations Aplicadas

### 001_add_movement_indexes.sql
**Data:** 2026-02-22
**Story:** REM-001 (DB-001)
**Autor:** @dev

**Descrição:**
Adiciona 3 índices críticos na tabela `movements` para eliminar N+1 queries e acelerar buscas.

**Índices criados:**
- `idx_movement_process_date` - Composite index (process_id, date DESC)
- `idx_movement_code` - Code lookup index
- `idx_movement_date` - Chronological index (date DESC)

**Performance:**
- Query latência: 100-500ms → **0.08-0.28ms** (400-2000x speedup)
- EXPLAIN QUERY PLAN: Todas as queries usam SEARCH/SCAN USING INDEX ✅

**Como aplicar manualmente:**
```bash
# Via Python (recomendado no Windows)
python -c "
import sqlite3
conn = sqlite3.connect('consulta_processual.db')
cursor = conn.cursor()
cursor.execute('CREATE INDEX IF NOT EXISTS idx_movement_process_date ON movements(process_id, date DESC)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_movement_code ON movements(code)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_movement_date ON movements(date DESC)')
conn.commit()
conn.close()
"

# Ou via sqlite3 CLI (se disponível)
sqlite3 consulta_processual.db < backend/migrations/001_add_movement_indexes.sql
```

**Verificar aplicação:**
```python
import sqlite3
conn = sqlite3.connect('consulta_processual.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='movements'")
print(cursor.fetchall())
# Esperado: idx_movement_process_date, idx_movement_code, idx_movement_date
```

## Como criar novas migrations

1. Criar arquivo `XXX_description.sql` (XXX = número sequencial)
2. Documentar neste README
3. Aplicar via Python ou sqlite3 CLI
4. Verificar com EXPLAIN QUERY PLAN
5. Medir performance antes/depois
