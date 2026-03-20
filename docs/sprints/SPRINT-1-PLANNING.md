# Sprint 1 Planning — Critical Stabilization + Quick Wins

**Sprint:** Sprint 1 (Brownfield Remediation)
**Duration:** 1 semana (5 dias úteis)
**Start Date:** 2026-02-24 (Segunda-feira)
**End Date:** 2026-02-28 (Sexta-feira)
**Sprint Goal:** Eliminar riscos críticos de segurança, otimizar performance de queries (20-100x speedup), e habilitar backup automático — tudo com Quick Wins (<1 dia esforço cada)

---

## 🎯 Sprint Goal

**Objetivo Principal:**
Remover **40% dos débitos HIGH** e **3 débitos CRITICAL** através de 10 Quick Wins que custam apenas 6 horas de esforço total, mas entregam:
- 🔒 **Segurança:** Secrets vault (SEC-ARCH-001), rate limiting (SEC-ARCH-002), CORS whitelist (SEC-ARCH-004)
- ⚡ **Performance:** Database indexes (DB-001) → 20-100x query speedup
- 💾 **Confiabilidade:** Backup automation (DB-003), log rotation (OPS-ARCH-001)
- ✅ **Qualidade:** Data validation (DB-006/007), dead code cleanup (BE-ARCH-004), accessibility (FE-001)

**Success Criteria:**
- [ ] Todas 10 stories completas e deployadas em produção
- [ ] Query latency Movement table: 100-500ms → <5ms (20-100x faster)
- [ ] Secrets vault operacional (zero plaintext credentials)
- [ ] Backup diário automático funcionando (30-day retention)
- [ ] Rate limiting ativo (100 req/min)

---

## 📊 Sprint Capacity

### Team Allocation

| Role | Developer | Availability | Capacity (Story Points) |
|------|-----------|-------------|------------------------|
| **Backend Developer** | [Nome] | 5 dias (100%) | 15 pts |
| **Frontend Developer** | [Nome] | 5 dias (100%) | 10 pts |
| **Data Engineer** | [Nome] | 3 dias (60%) | 8 pts |
| **DevOps Engineer** | [Nome] | 2 dias (40%) | 5 pts |

**Total Sprint Capacity:** **38 story points**
**Committed Sprint Backlog:** **27 story points** (70% utilização — buffer saudável)

---

## 📋 Sprint Backlog (10 Stories)

### 🔴 CRITICAL Priority (1 story — 5 pts)

#### STORY-REM-003: Implement Secrets Vault ⭐
**Debit ID:** SEC-ARCH-001
**Complexity:** 5 pts (S - 1 day)
**Assignee:** Backend Developer
**Priority:** CRITICAL (Security breach prevention)

**User Story:**
> Como desenvolvedor, quero migrar secrets de plaintext (.env) para vault criptografado, para que credenciais não sejam expostas em caso de leak.

**Acceptance Criteria:**
- [ ] Vault solution selected (dotenv-vault OU AWS Secrets Manager)
- [ ] DATAJUD_APIKEY migrado para vault
- [ ] DATABASE_URL migrado para vault
- [ ] `.env` removido do repo (verificar .gitignore)
- [ ] `backend/config.py` atualizado para fetch from vault
- [ ] API keys rotated (novas chaves geradas após migração)
- [ ] README.md atualizado com instruções de vault

**Technical Tasks:**
1. [ ] Decidir vault provider (dotenv-vault vs AWS Secrets Manager)
2. [ ] Instalar dependencies (`npm install -g dotenv-vault` OU `pip install boto3`)
3. [ ] Criar vault project/secret store
4. [ ] Migrar 3 secrets (DATAJUD_APIKEY, DATABASE_URL, SENTRY_DSN)
5. [ ] Update backend/config.py para fetch secrets
6. [ ] Rotar API keys no DataJud dashboard
7. [ ] Testar aplicação com secrets do vault
8. [ ] Documentar processo em README.md

**Definition of Done:**
- ✅ Code merged to `main`
- ✅ Secrets vault operational (production)
- ✅ Zero plaintext secrets in codebase
- ✅ Documentation updated
- ✅ Team trained on vault usage

**Dependencies:** None (but blocks DEPLOY-ARCH-001/002)

---

### 🟠 HIGH Priority (3 stories — 8 pts)

#### STORY-REM-001: Add Missing Database Indexes ⚡
**Debit ID:** DB-001
**Complexity:** 2 pts (XS - 30 min)
**Assignee:** Data Engineer
**Priority:** HIGH (20-100x performance improvement)

**User Story:**
> Como usuário, quero que queries de movimentações sejam 20-100x mais rápidas, para que eu possa visualizar detalhes de processos instantaneamente (sem esperar 100-500ms).

**Acceptance Criteria:**
- [ ] CREATE INDEX idx_movement_process_date ON movements(process_id, date DESC)
- [ ] CREATE INDEX idx_movement_code ON movements(code)
- [ ] CREATE INDEX idx_movement_date ON movements(date DESC)
- [ ] EXPLAIN QUERY PLAN mostra "SEARCH TABLE movements USING INDEX" (não SCAN)
- [ ] Performance test: Movement query <5ms (atualmente 100-500ms)

**SQL Script:**
```sql
-- Execute in production database
CREATE INDEX IF NOT EXISTS idx_movement_process_date ON movements(process_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_movement_code ON movements(code);
CREATE INDEX IF NOT EXISTS idx_movement_date ON movements(date DESC);

-- Verify indexes created
SELECT name, tbl_name, sql FROM sqlite_master WHERE type = 'index' AND tbl_name = 'movements';

-- Performance validation
EXPLAIN QUERY PLAN
SELECT * FROM movements WHERE process_id = 123 ORDER BY date DESC;
-- Expected: SEARCH TABLE movements USING INDEX idx_movement_process_date
```

**Testing:**
```bash
# Before: Measure baseline
time sqlite3 consulta_processual.db "SELECT * FROM movements WHERE process_id = 1 ORDER BY date DESC;"
# Expected: ~100-500ms

# After: Measure improvement
time sqlite3 consulta_processual.db "SELECT * FROM movements WHERE process_id = 1 ORDER BY date DESC;"
# Expected: <5ms (20-100x faster)
```

**Definition of Done:**
- ✅ 3 indexes created in production database
- ✅ EXPLAIN QUERY PLAN shows index usage
- ✅ Performance test passes (<5ms query time)
- ✅ No production errors (rollback plan tested)

---

#### STORY-REM-002: Implement Automated Database Backup 💾
**Debit ID:** DB-003
**Complexity:** 3 pts (S - 2 hours)
**Assignee:** DevOps Engineer
**Priority:** HIGH (Data loss prevention)

**User Story:**
> Como administrador de sistema, quero backups diários automatizados com 30-day retention, para que possamos recuperar dados em caso de disaster.

**Acceptance Criteria:**
- [ ] Script `scripts/backup_db.sh` criado
- [ ] Backup usa `.backup` command (transaction-safe)
- [ ] Gzip compression aplicada
- [ ] Integrity check (PRAGMA integrity_check) antes do backup
- [ ] 30-day retention (backups antigos deletados automaticamente)
- [ ] Cron job agendado (daily 2 AM)
- [ ] Restore script `scripts/restore_database.sh` testado

**Backup Script:**
```bash
#!/bin/bash
# scripts/backup_db.sh
set -e

DB_FILE="consulta_processual.db"
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/backup.log"

mkdir -p $BACKUP_DIR logs

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "=== Backup Started ==="

# Check database exists
if [ ! -f "$DB_FILE" ]; then
    log "ERROR: Database file not found!"
    exit 1
fi

# Integrity check
log "Running integrity check..."
INTEGRITY=$(sqlite3 $DB_FILE "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
    log "ERROR: Integrity check failed: $INTEGRITY"
    exit 1
fi
log "Integrity: OK"

# Backup
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.db"
log "Creating backup: $BACKUP_FILE"
sqlite3 $DB_FILE ".backup '$BACKUP_FILE'"

# Compress
log "Compressing..."
gzip $BACKUP_FILE
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

# Verify
if [ ! -f "$BACKUP_FILE_GZ" ]; then
    log "ERROR: Compressed backup not created!"
    exit 1
fi

SIZE=$(du -h $BACKUP_FILE_GZ | cut -f1)
log "Backup created: $BACKUP_FILE_GZ ($SIZE)"

# Cleanup old backups (30 days)
log "Cleaning up old backups (retention: 30 days)..."
DELETED=$(find $BACKUP_DIR -name "backup_*.db.gz" -mtime +30 -delete -print | wc -l)
log "Deleted $DELETED old backup(s)"

# Summary
BACKUP_COUNT=$(find $BACKUP_DIR -name "backup_*.db.gz" | wc -l)
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
log "Current backups: $BACKUP_COUNT files ($TOTAL_SIZE total)"

log "=== Backup Completed ==="
```

**Restore Script:**
```bash
#!/bin/bash
# scripts/restore_database.sh
BACKUP_DIR="backups"

echo "Available backups:"
ls -lh $BACKUP_DIR/backup_*.db.gz

read -p "Enter backup filename to restore: " BACKUP_FILE

# Decompress
gunzip -c "$BACKUP_DIR/$BACKUP_FILE" > consulta_processual_restored.db

# Verify
INTEGRITY=$(sqlite3 consulta_processual_restored.db "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
    echo "ERROR: Restored database failed integrity check!"
    exit 1
fi

echo "✅ Database restored to consulta_processual_restored.db"
echo "To use:"
echo "  1. Stop application"
echo "  2. Backup current: mv consulta_processual.db consulta_processual_old.db"
echo "  3. Use restored: mv consulta_processual_restored.db consulta_processual.db"
echo "  4. Restart application"
```

**Cron Setup:**
```bash
# Add to crontab
crontab -e

# Add this line:
0 2 * * * cd /path/to/consulta-processo && ./scripts/backup_db.sh >> logs/backup.log 2>&1
```

**Testing:**
1. Run `./scripts/backup_db.sh` manually
2. Verify backup file created in `backups/`
3. Test restore with `./scripts/restore_database.sh`
4. Verify cron job runs (check logs next day)

**Definition of Done:**
- ✅ Backup script executable and tested
- ✅ Cron job scheduled (daily 2 AM)
- ✅ Restore script tested successfully
- ✅ 30-day retention working
- ✅ Documentation in README.md

---

#### STORY-REM-004: Add API Rate Limiting 🛡️
**Debit ID:** SEC-ARCH-002
**Complexity:** 3 pts (S - 2 hours)
**Assignee:** Backend Developer
**Priority:** HIGH (DoS prevention)

**User Story:**
> Como administrador de sistema, quero limitar requests a 100/min por IP, para que o servidor não seja sobrecarregado por DoS attacks ou uso abusivo.

**Acceptance Criteria:**
- [ ] SlowAPI library installed (`pip install slowapi`)
- [ ] Limiter configured (100/minute per remote address)
- [ ] Applied to `/api/search` endpoint
- [ ] Applied to `/api/bulk` endpoint (50/minute — mais restritivo)
- [ ] 429 response quando rate excedido
- [ ] Rate limit headers included (X-RateLimit-Limit, X-RateLimit-Remaining)
- [ ] Test: 101 requests → 101st returns 429 Too Many Requests

**Implementation:**
```python
# backend/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@app.get("/api/search")
@limiter.limit("100/minute")
async def search_process(request: Request, cnj: str):
    # Existing code
    ...

@app.post("/api/bulk")
@limiter.limit("50/minute")  # More restrictive for bulk
async def bulk_search(request: Request, numeros: list):
    # Existing code
    ...
```

**Testing:**
```python
# tests/test_rate_limiting.py
import pytest
from fastapi.testclient import TestClient

def test_rate_limit_enforced():
    client = TestClient(app)

    # Send 101 requests
    for i in range(101):
        response = client.get("/api/search?cnj=12345678901234567890")

        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429  # 101st request blocked
            assert "X-RateLimit-Limit" in response.headers
```

**Definition of Done:**
- ✅ SlowAPI integrated
- ✅ Rate limits active on search + bulk endpoints
- ✅ 429 response working correctly
- ✅ Rate limit headers present
- ✅ Tests passing

---

### 🟡 MEDIUM Priority (7 stories — 14 pts)

#### STORY-REM-005: Add CORS Whitelist Configuration
**Debit ID:** SEC-ARCH-004 | **Complexity:** 2 pts | **Assignee:** Backend Dev

**Acceptance Criteria:**
- [ ] CORS middleware configured with explicit `allow_origins` list
- [ ] Production domain whitelisted
- [ ] Localhost allowed for dev
- [ ] `allow_origins=["*"]` removed
- [ ] Test: Non-whitelisted origin → CORS error

---

#### STORY-REM-006: Remove OpenRouter Dead Code
**Debit ID:** BE-ARCH-004 | **Complexity:** 2 pts | **Assignee:** Backend Dev

**Acceptance Criteria:**
- [ ] OPENROUTER_API_KEY removed from `.env.example`
- [ ] OpenRouterConfig class deleted
- [ ] Grep confirms no "openrouter" references
- [ ] Tests pass

---

#### STORY-REM-007: Add Label HTML Associations (Accessibility)
**Debit ID:** FE-001 | **Complexity:** 2 pts | **Assignee:** Frontend Dev

**Acceptance Criteria:**
- [ ] BulkSearch textarea has `htmlFor="bulk-numbers-textarea"`
- [ ] Settings: All 15+ fields have `htmlFor`
- [ ] Axe accessibility audit passes
- [ ] Screen reader test: Labels announced

---

#### STORY-REM-008: Add Phase CHECK Constraint
**Debit ID:** DB-006 | **Complexity:** 2 pts | **Assignee:** Data Engineer

**Acceptance Criteria:**
- [ ] CHECK constraint added: `phase IS NULL OR (phase >= '01' AND phase <= '15')`
- [ ] Test: phase='99' → fails
- [ ] Test: phase='05' → success

---

#### STORY-REM-009: Add CNJ Number CHECK Constraint
**Debit ID:** DB-007 | **Complexity:** 2 pts | **Assignee:** Data Engineer

**Acceptance Criteria:**
- [ ] CHECK constraint added: `LENGTH(number) = 20 AND number GLOB '[0-9]*'`
- [ ] Test: number='123' → fails
- [ ] Test: 20 digits → success

---

#### STORY-REM-010: Configure Database Connection Pooling
**Debit ID:** DB-011 | **Complexity:** 2 pts | **Assignee:** Backend Dev

**Acceptance Criteria:**
- [ ] Engine configured with `poolclass=StaticPool`
- [ ] `connect_args={'check_same_thread': False}` set
- [ ] Load test: 50 concurrent requests → no errors

---

#### STORY-REM-011: Add Log Rotation
**Debit ID:** OPS-ARCH-001 | **Complexity:** 2 pts | **Assignee:** Backend Dev

**Acceptance Criteria:**
- [ ] RotatingFileHandler configured (10 MB max, 5 backups)
- [ ] Old logs deleted automatically
- [ ] Test: 11 MB logs → 2 files created

---

## 📅 Sprint Timeline (5 dias)

### Dia 1 (Segunda) — Setup & Critical
**Focus:** Secrets vault (5 pts)
- [ ] **REM-003** (Secrets Vault) — Backend Dev (full day)

### Dia 2 (Terça) — Database & Security
**Focus:** Performance + Security (8 pts)
- [ ] **REM-001** (Indexes) — Data Engineer (30 min)
- [ ] **REM-002** (Backup) — DevOps (2 hours)
- [ ] **REM-004** (Rate Limiting) — Backend Dev (2 hours)
- [ ] **REM-005** (CORS) — Backend Dev (30 min)

### Dia 3 (Quarta) — Data Validation & Cleanup
**Focus:** Quality (8 pts)
- [ ] **REM-006** (Dead Code) — Backend Dev (30 min)
- [ ] **REM-008** (Phase CHECK) — Data Engineer (15 min)
- [ ] **REM-009** (CNJ CHECK) — Data Engineer (15 min)
- [ ] **REM-010** (Connection Pool) — Backend Dev (30 min)
- [ ] **REM-011** (Log Rotation) — Backend Dev (30 min)

### Dia 4 (Quinta) — Frontend & Testing
**Focus:** Accessibility + QA (2 pts)
- [ ] **REM-007** (Label Associations) — Frontend Dev (30 min)
- [ ] Integration testing (all stories)
- [ ] Performance validation (DB-001 speedup)

### Dia 5 (Sexta) — Deploy & Review
**Focus:** Production deployment + Retrospective
- [ ] Production deployment (all 10 stories)
- [ ] Smoke tests
- [ ] Sprint Review (demo to stakeholders)
- [ ] Sprint Retrospective

---

## ✅ Definition of Done

**Story-level:**
- [ ] Code complete and peer-reviewed
- [ ] Unit tests written (if applicable)
- [ ] Acceptance criteria met (all checkboxes ✅)
- [ ] Documentation updated (README, comments)
- [ ] Merged to `main` branch

**Sprint-level:**
- [ ] All 10 stories deployed to production
- [ ] No critical bugs in production
- [ ] Performance metrics validated:
  - Query latency <5ms (DB-001)
  - Secrets vault operational (SEC-ARCH-001)
  - Backup cron running (DB-003)
  - Rate limiting active (SEC-ARCH-002)
- [ ] Sprint Review completed (demo to stakeholders)
- [ ] Sprint Retrospective completed

---

## 🎯 Success Metrics

### Performance
- **Before:** Movement query = 100-500ms
- **After:** Movement query = **<5ms**
- **Target:** ✅ 20-100x speedup

### Security
- **Before:** Secrets in plaintext (.env)
- **After:** Secrets in vault (dotenv-vault/AWS)
- **Target:** ✅ Zero plaintext credentials

### Reliability
- **Before:** No backups
- **After:** Daily backups (30-day retention)
- **Target:** ✅ RPO (Recovery Point Objective) = 24h

### Quality
- **Before:** No rate limiting, no data validation
- **After:** 100 req/min limit, CHECK constraints
- **Target:** ✅ DoS protection + data integrity

---

## 🚨 Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Secrets vault setup delays | MEDIUM | HIGH | Start Day 1, have fallback (dotenv-vault simpler than AWS) |
| Production index creation locks table | LOW | MEDIUM | Run during off-peak hours (2 AM), test in staging first |
| Cron job permission issues | MEDIUM | LOW | Test manually first, document setup steps |
| Team availability | LOW | HIGH | Buffer capacity (27 pts vs 38 pts capacity) |

---

## 📝 Sprint Planning Notes

**Meeting Date:** 2026-02-22
**Participants:** Backend Dev, Frontend Dev, Data Engineer, DevOps
**Duration:** 1 hora

**Decisions:**
1. ✅ Sprint Goal approved unanimously
2. ✅ 10 stories committed (27 pts)
3. ✅ Team capacity confirmed (38 pts available, 70% utilization)
4. ✅ DevOps will support Data Engineer on Day 2 (backup + indexes)
5. ✅ Backend Dev owns secrets vault (most complex story)

**Action Items:**
- [ ] Backend Dev: Research dotenv-vault vs AWS Secrets Manager (before Day 1)
- [ ] Data Engineer: Identify off-peak window for index creation
- [ ] DevOps: Setup cron environment (test user permissions)
- [ ] Frontend Dev: Audit all form fields needing htmlFor (prep for REM-007)

---

## 🔄 Daily Standup Format

**3 Questions (15 min daily):**
1. What did you complete yesterday?
2. What will you work on today?
3. Any blockers?

**Slack Channel:** `#sprint-1-brownfield`
**Time:** 9:00 AM daily

---

## 📊 Sprint Burndown

| Day | Stories Remaining | Points Remaining | Velocity |
|-----|------------------|------------------|----------|
| Day 0 (Mon start) | 10 | 27 | — |
| Day 1 (Mon end) | 9 | 22 | 5 pts/day |
| Day 2 (Tue end) | 6 | 14 | 8 pts/day |
| Day 3 (Wed end) | 2 | 6 | 8 pts/day |
| Day 4 (Thu end) | 0 | 0 | 6 pts/day |
| Day 5 (Fri) | 0 | 0 | Deploy + Review |

**Target:** Zero points remaining by Day 4 EOD (Day 5 reserved for deploy + review)

---

## 🎉 Sprint Review Agenda (Sexta 16h)

**Duration:** 30 min
**Attendees:** Team + Stakeholders

**Demo:**
1. **Performance:** Show before/after query latency (100-500ms → <5ms)
2. **Security:** Demo secrets vault (no plaintext in .env)
3. **Reliability:** Show backup files (30-day retention)
4. **Quality:** Demo rate limiting (101st request → 429)
5. **Accessibility:** Show label associations (screen reader demo)

**Metrics Review:**
- 10/10 stories completed ✅
- 27/27 points delivered ✅
- Query speedup: 20-100x ✅
- Zero production incidents ✅

---

## 🔍 Sprint Retrospective Agenda (Sexta 16:30)

**Duration:** 30 min
**Format:** Start/Stop/Continue

**Discussion Points:**
1. What went well? (celebrate wins)
2. What didn't go well? (identify problems)
3. What should we start/stop/continue?
4. Action items for Sprint 2

**Output:** Action items documented → Sprint 2 Planning input

---

**Sprint 1 Planning** ✅ COMPLETE
**Ready to Start:** Segunda-feira, 2026-02-24
**Next Step:** Kick-off meeting (9 AM Monday) → Daily standups begin

---

**Quer ajustar alguma prioridade ou story do Sprint 1?** 🚀
