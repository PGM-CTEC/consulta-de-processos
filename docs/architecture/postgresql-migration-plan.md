# Plano de Migração SQLite → PostgreSQL

**Stories:** REM-053 (Setup), REM-054 (Schema), REM-055 (Data), REM-056 (App Code), REM-057 (Cutover)
**Data de criação:** 2026-02-28

## Visão Geral

Migração em 5 fases do banco SQLite atual para PostgreSQL 15+ para suportar:
- Múltiplos usuários simultâneos
- Full-text search (pg_trgm)
- JSONB queries eficientes
- Connection pooling (pgBouncer)

---

## Fase 1: Setup PostgreSQL (REM-053)

```bash
# Ubuntu/Debian
sudo apt install postgresql-15
sudo -u postgres createuser consulta_user --pwprompt
sudo -u postgres createdb consulta_processual_pg --owner consulta_user

# Variável de ambiente
DATABASE_URL=postgresql://consulta_user:senha@localhost:5432/consulta_processual_pg
```

**Extensions:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## Fase 2: Schema Translation (REM-054)

Script: `backend/migrations/postgresql_schema.sql`

**Mapeamento de tipos:**

| SQLite | PostgreSQL |
|--------|-----------|
| INTEGER | SERIAL (auto-increment) |
| TEXT | TEXT ou VARCHAR(N) |
| DATETIME | TIMESTAMPTZ |
| JSON | JSONB |
| String | VARCHAR(N) |

---

## Fase 3: Data Migration (REM-055)

```python
# Script de migração de dados
# backend/migrations/migrate_data.py
import sqlite3
import psycopg2

def migrate():
    sqlite_conn = sqlite3.connect('consulta_processual.db')
    pg_conn = psycopg2.connect(DATABASE_URL)

    # Migrar processos em lotes de 1000
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    sqlite_cursor.execute("SELECT COUNT(*) FROM processes")
    total = sqlite_cursor.fetchone()[0]

    batch_size = 1000
    for offset in range(0, total, batch_size):
        sqlite_cursor.execute(
            "SELECT * FROM processes LIMIT ? OFFSET ?",
            (batch_size, offset)
        )
        rows = sqlite_cursor.fetchall()
        # INSERT batch into PostgreSQL
        pg_cursor.executemany(
            "INSERT INTO processes (...) VALUES (...)",
            rows
        )
        pg_conn.commit()
        print(f"Migrated {min(offset + batch_size, total)}/{total} processes")
```

---

## Fase 4: Application Code (REM-056)

Mudanças mínimas em `backend/database.py`:

```python
# Antes (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./consulta_processual.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Depois (PostgreSQL)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```

---

## Fase 5: Cutover (REM-057)

### Checklist de Cutover

- [ ] Backup completo do SQLite (`cp consulta_processual.db backup_$(date +%Y%m%d).db`)
- [ ] Executar migração de dados em ambiente de staging
- [ ] Validar contagem de registros (SQLite == PostgreSQL)
- [ ] Ativar modo manutenção (< 30 min)
- [ ] Executar script de migração
- [ ] Validar integridade: SELECTs de amostragem
- [ ] Atualizar DATABASE_URL em produção
- [ ] Smoke tests (busca de processo, bulk search, dashboard)
- [ ] Monitorar erros por 24h
- [ ] Rollback: `DATABASE_URL=sqlite:///...` se necessário

### Rollback Plan

```bash
# Reverter em < 5 minutos
export DATABASE_URL="sqlite:///./consulta_processual.db"
systemctl restart app
```

---

## Estimativa de Tempo

| Fase | Estimativa |
|------|-----------|
| Setup | 2 horas |
| Schema | 1 hora |
| Data migration | 1-4 horas (depende do volume) |
| App code | 2 horas |
| Cutover | 30 min de downtime |
