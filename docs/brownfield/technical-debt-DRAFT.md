# Technical Debt Assessment (DRAFT)

**Projeto:** Consulta Processo
**Data:** 2026-02-21
**Fase:** Brownfield Discovery - Fase 4 (Draft)
**Consolidação:** @architect (Aria)
**Fonte:** system-architecture.md (Fase 1) + DB-AUDIT.md (Fase 2) + frontend-spec.md (Fase 3)

---

## Executive Summary

Consolidação de **49 débitos técnicos** identificados nas Fases 1-3 do Brownfield Discovery.

### Estatísticas Gerais

| Categoria | Contagem | % Total |
|-----------|----------|---------|
| **CRITICAL** | 7 | 14% |
| **HIGH** | 14 | 29% |
| **MEDIUM** | 21 | 43% |
| **LOW** | 7 | 14% |
| **TOTAL** | **49** | 100% |

### Distribuição por Dimensão

| Dimensão | Count | Effort Total | Prioridade |
|----------|-------|--------------|-----------|
| **Performance** | 5 | 12 dias | 🔴 CRITICAL |
| **Security** | 5 | 4 dias | 🔴 CRITICAL |
| **Testing** | 4 | 20 dias | 🔴 CRITICAL |
| **Operations** | 8 | 15 dias | 🟠 HIGH |
| **Code Quality** | 10 | 18 dias | 🟠 HIGH |
| **Scalability** | 3 | 25 dias | 🟡 MEDIUM |
| **Compliance** | 2 | 5 dias | 🟡 MEDIUM |
| **Deployment** | 7 | 12 dias | 🟠 HIGH |

### Business Impact

- 🔴 **1 BLOCKING ISSUE**: Bulk processing sequencial (2-5min delays) → user churn
- 🔴 **2 SECURITY RISKS**: Secrets em plaintext + sem monitoring → breach exposure
- 🔴 **1 PRODUCTION BLOCKER**: Sem health checks/monitoring → blind to failures

### Quick Wins (High Impact, Low Effort)

**< 1 dia esforço, removes 30% of HIGH debits:**
1. ✅ DB-001: Add missing indexes (XS, HIGH) → 30 min
2. ✅ DB-003: Backup script (S, HIGH) → 2 hours
3. ✅ SEC-ARCH-002: Rate limiting setup (S, HIGH) → 2 hours
4. ✅ BE-ARCH-004: Remove OpenRouter dead code (S, MEDIUM) → 30 min

---

## Debit Inventory (Completo)

### 🔴 CRITICAL SEVERITY (7 débitos - Ação Imediata)

#### SEC-ARCH-001: Secrets Management
**Category**: Security
**Status**: OPEN
**Severity**: CRITICAL (Security Breach Risk)
**Affected**: `backend/config.py`, `.env`
**Description**: Secrets (API keys, database URL) armazenados em plaintext no .env sem encryption
**Impact**: If `.env` leaked → complete API compromise, DataJud API hijacking
**Effort**: S (1 day)
**Recommendation**: Audit .gitignore → implement dotenv-vault or AWS Secrets Manager → rotate keys
**Depends On**: None

---

#### PERF-ARCH-001: Sequential Bulk Processing
**Category**: Performance
**Status**: OPEN
**Severity**: CRITICAL (Poor UX, User Abandonment)
**Affected**: `backend/services/process_service.py:178` (`bulk_search()`)
**Description**: Bulk searches process 50+ CNJ numbers sequentially → 2-5min delays
**Impact**: Users abandon large batch requests; frontend timeout errors
**Current**: 50 items × 100ms = 5s, with queuing → 15-30s
**Target**: 50 items, parallel → <30s
**Effort**: L (3-5 days)
**Recommendation**: Replace sequential loop with `asyncio.gather()`, concurrency limit = 10
**Code Fix**:
```python
# ❌ Current (sequential)
for numero in numeros:
    result = self.get_or_update_process(numero)  # Blocks for 100ms

# ✅ Proposed (async)
async def bulk_search_async(self, numeros):
    tasks = [self.get_or_update_process(n) for n in numeros]
    return await asyncio.gather(*tasks, return_exceptions=True)
```
**Depends On**: None (but unblocks PERF-002)

---

#### ERROR-ARCH-002: Error Monitoring
**Category**: Operations
**Status**: OPEN
**Severity**: CRITICAL (Blind to Production Issues)
**Affected**: Backend + Frontend (all layers)
**Description**: Sem centralized error tracking → erros em produção não detectados
**Impact**: Silent failures → users experience timeouts, we're unaware
**Current**: Local logging only, no alerting
**Effort**: M (3-5 days)
**Recommendation**: Implement Sentry (backend + frontend) + Slack/email alerts
**User Story**: STORY-BR-002 (already refactored to local JSON logging)
**Depends On**: None

---

#### TEST-ARCH-001: Test Coverage Inadequate
**Category**: Testing
**Status**: OPEN
**Severity**: CRITICAL (Regression Risk)
**Affected**: Backend (~15%), Frontend (~2%)
**Description**: Cobertura de testes <20% → regressions não detectadas before deploy
**Impact**: Bug escapes to production; confidence low for refactoring
**Target**: 70% backend, 60% frontend
**Effort**: XL (2-3 weeks)
**Recommendation**: Priorize ProcessService, DataJudClient, PhaseAnalyzer tests; add React Testing Library
**Dependencies**: None (but blocks production readiness)

---

#### DEPLOY-ARCH-004: No Health Checks/Monitoring
**Category**: Deployment/Operations
**Status**: OPEN
**Severity**: CRITICAL (Downtime Not Detected)
**Affected**: Deployment infrastructure, launcher.py
**Description**: Sem health checks, alerting, or monitoring → downtime invisible to ops
**Impact**: Service down, users affected, we don't know until complaints
**Effort**: M (3-5 days)
**Recommendation**: Add `/health` endpoint; implement Prometheus metrics; setup monitoring dashboard
**Depends On**: Error monitoring (ERROR-ARCH-002)

---

#### DB-002: SQLite Single-Writer Limitation
**Category**: Scalability
**Status**: OPEN
**Severity**: CRITICAL (Production Bottleneck for Scale)
**Affected**: `database.py`, SQLite choice
**Description**: SQLite serializes writes (single writer) → concurrent bulk requests lock table
**Impact**: Blocks production scale beyond 50-100 concurrent users
**Current**: OK for dev (1-5 users), breaks at 100+ users
**Effort**: XL (3-4 weeks migration)
**Recommendation**: Monitor; plan PostgreSQL migration if production scale expected
**Depends On**: None (future-only unless scale hits)

---

#### FE-006: Testing Coverage (Frontend)
**Category**: Testing
**Status**: OPEN
**Severity**: CRITICAL (Accessibility + Regression Risk)
**Affected**: 9 components (only `phases.test.js` exists)
**Description**: 1 test file for 9 components → 2% coverage, regressions invisible
**Impact**: UI changes break subtly; accessibility gaps go unnoticed
**Effort**: 13 pts (2-3 days)
**Recommendation**: Add Vitest + React Testing Library; test coverage target 70%
**Test Stories**: SearchProcess (validation), BulkSearch (upload/export), ProcessDetails (filtering), etc
**Depends On**: None

---

### 🟠 HIGH SEVERITY (14 débitos - Next 2-3 sprints)

#### BE-ARCH-001: ProcessService → DataJudClient Coupling
**Category**: Code Quality
**Status**: OPEN
**Severity**: HIGH (Maintainability)
**Affected**: `backend/services/process_service.py`, `backend/services/datajud.py`
**Description**: Direct instantiation `self.client = DataJudClient()` → no dependency injection
**Impact**: Hard to mock for testing; tight coupling complicates refactoring
**Effort**: M (3 days)
**Recommendation**: Introduce `IDataJudClient` interface; use constructor injection
**Depends On**: None

---

#### BE-ARCH-002: No Retry Logic with Exponential Backoff
**Category**: Resilience
**Status**: OPEN
**Severity**: HIGH (API Reliability)
**Affected**: `backend/services/datajud.py` (error handling)
**Description**: DataJud errors (429, 503) not retried → user faces immediate failure
**Impact**: Transient failures become permanent failures
**Effort**: S (1 day)
**Recommendation**: Add exponential backoff (max 3 retries) for 429/503
**Depends On**: None

---

#### BE-ARCH-003: ... [listed above, CRITICAL]

---

#### DB-001: Missing Indexes on Movement
**Category**: Performance
**Status**: OPEN
**Severity**: HIGH (N+1 Query Problem)
**Affected**: `movements` table
**Description**: No indexes on `process_id`, `date`, `code` → full table scans (100-500ms per query)
**Current**: 50k movements, scan = 100ms, with 5k processes = 100ms per process
**Impact**: Bulk search delays; dashboard slow
**Target**: With indexes → <1ms per query
**Effort**: XS (30 min)
**SQL Fix**:
```sql
CREATE INDEX idx_movement_process_date ON movements(process_id, date DESC);
CREATE INDEX idx_movement_code ON movements(code);
CREATE INDEX idx_process_phase ON processes(phase);
```
**Depends On**: None
**Quick Win**: ✅ Do this first

---

#### DB-003: No Automated Backup
**Category**: Operations
**Status**: OPEN
**Severity**: HIGH (Data Loss Risk)
**Affected**: SQLite database file
**Description**: Manual backup only → data loss on disk failure or accidental deletion
**Impact**: Unrecoverable data loss
**Effort**: S (2 hours)
**Recommendation**: Daily backup via cron + gzip + 30-day retention
**Script**:
```bash
#!/bin/bash
sqlite3 consulta_processual.db ".dump" | gzip > backups/backup_$(date +%Y%m%d_%H%M%S).sql.gz
find backups -name "backup_*.sql.gz" -mtime +30 -delete
```
**Depends On**: None
**Quick Win**: ✅ Do this first

---

#### DB-004: SearchHistory Orphan Risk
**Category**: Integrity
**Status**: OPEN
**Severity**: HIGH (Referential Integrity)
**Affected**: `search_history` table (no FK to processes)
**Description**: No FK constraint → orphan records possible (historical choice for log independence)
**Impact**: Cleanup requires manual queries; data inconsistency
**Effort**: S (1 day)
**Recommendation**: Add optional FK with validation cleanup
**Depends On**: None

---

#### LOG-ARCH-002: No Centralized Logging
**Category**: Operations
**Status**: OPEN
**Severity**: HIGH (Observability)
**Affected**: Backend logging infrastructure
**Description**: Logs scattered (stdout, stderr, files) → hard to search/correlate
**Impact**: Troubleshooting blind; no audit trail
**Effort**: M (3-5 days)
**Recommendation**: Implement structured JSON logging (STORY-BR-001 partial); aggregate to ELK or Datadog
**Depends On**: Partially done (local JSON logger in STORY-BR-001)

---

#### SEC-ARCH-002: Rate Limiting Disabled
**Category**: Security
**Status**: OPEN
**Severity**: HIGH (DDoS/Abuse)
**Affected**: FastAPI app (all endpoints)
**Description**: No rate limiting → API vulnerable to brute force, DDoS
**Impact**: Malicious actors flood API; service becomes unavailable
**Effort**: S (1 day)
**Recommendation**: Implement `SlowAPI` (FastAPI extension); 100 req/min per IP default
**Code**:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
@app.get("/processes/{number}")
@limiter.limit("100/minute")
async def get_process(number: str):
    ...
```
**Depends On**: None

---

#### SEC-ARCH-003: Authentication Disabled by Default
**Category**: Security
**Status**: OPEN
**Severity**: HIGH (Access Control)
**Affected**: FastAPI app; all endpoints public
**Description**: No auth layer → anyone can query any process, manipulate data
**Impact**: Data exposure; compliance violations (LGPD)
**Effort**: M (3-5 days)
**Recommendation**: Implement JWT or session-based auth; require user login
**Depends On**: None (but blocks production)

---

#### DEPLOY-ARCH-001: No Containerization
**Category**: Deployment
**Status**: OPEN
**Severity**: HIGH (Ops Efficiency)
**Affected**: Deployment infrastructure
**Description**: No Docker → manual dependency management, environment drift
**Impact**: Deployment errors; environment inconsistency; hard to scale
**Effort**: L (1 week)
**Recommendation**: Create Dockerfile + docker-compose.yml; multi-stage builds
**Depends On**: None (but improves DEPLOY-002)

---

#### DEPLOY-ARCH-002: No CI/CD Pipeline
**Category**: Deployment
**Status**: OPEN
**Severity**: HIGH (Quality Gate Missing)
**Affected**: Git workflow; release process
**Description**: Manual testing/deployment → human error, no automated checks
**Impact**: Regressions ship; inconsistent deployments
**Effort**: L (1 week)
**Recommendation**: Setup GitHub Actions (test, lint, build, deploy)
**Depends On**: Tests must exist (TEST-ARCH-001)

---

#### FE-004: Dashboard Chart Accessibility (HIGH)
**Category**: Accessibility
**Status**: OPEN
**Severity**: HIGH (WCAG Non-Compliance)
**Affected**: `frontend/src/components/Dashboard.jsx` (charts)
**Description**: Charts are SVG/divs without semantic labels → completely inaccessible to screen readers
**Impact**: Blind/low-vision users cannot access analytics; WCAG AAA failure
**Effort**: 8 pts (2-3 hours)
**Recommendation**: Wrap charts in `<figure>/<figcaption>`, add `aria-label`, provide text fallback
**Depends On**: None

---

#### EXT-ARCH-001: No Circuit Breaker Pattern
**Category**: Resilience
**Status**: OPEN
**Severity**: HIGH (Cascade Failure Prevention)
**Affected**: DataJud API client
**Description**: No circuit breaker → repeated DataJud failures hammer API
**Impact**: Cascading failures; amplifies outage impact
**Effort**: M (3 days)
**Recommendation**: Implement circuit breaker (fail-fast when API consistently down)
**Depends On**: BE-ARCH-002 (retry logic)

---

### 🟡 MEDIUM SEVERITY (21 débitos - Sprints 4-5)

#### FE-001: Label HTML Associations
**Category**: Accessibility
**Severity**: MEDIUM
**Affected**: BulkSearch, Settings
**Description**: Form inputs without `htmlFor` associations → screen readers don't announce labels
**Impact**: Screen reader users confused
**Effort**: 2 pts (30 min)
**Quick Win**: ✅ Easy fix
**Recommendation**: Add `htmlFor` and `id` attributes to all label/input pairs

---

#### FE-003: Keyboard Navigation (Dropdowns)
**Category**: Accessibility
**Severity**: MEDIUM
**Affected**: BulkSearch, ProcessDetails
**Description**: Menu dropdowns not navigable via keyboard (arrow keys, escape)
**Impact**: Keyboard-only users trapped
**Effort**: 5 pts (1-2 hours)
**Recommendation**: Use Headless UI or implement WAI-ARIA menu pattern

---

#### FE-005: Color Contrast Issues
**Category**: Accessibility
**Severity**: MEDIUM
**Affected**: Settings (amber-800), BulkSearch, multiple
**Description**: Some color combinations may fail 4.5:1 contrast ratio
**Effort**: 3 pts (1 hour audit + fixes)
**Recommendation**: WebAIM Contrast Checker on critical combinations

---

#### FE-007: Prop Drilling Without Context API
**Category**: Code Quality
**Severity**: MEDIUM
**Affected**: Multiple components (prop chains 5+ levels)
**Description**: State passed via props → hard to maintain, poor reusability
**Effort**: 5 pts (1-2 hours)
**Recommendation**: Introduce Context API for labels, theme, settings

---

#### LOG-ARCH-001: Non-Structured Logging
**Category**: Operations
**Severity**: MEDIUM
**Affected**: Backend logging
**Description**: Human-readable logs (not JSON) → hard to parse/aggregate
**Effort**: S (1 day)
**Recommendation**: Implement structured JSON logging (partially done in STORY-BR-001)

---

#### DB-005: No Audit Trail
**Category**: Compliance
**Severity**: MEDIUM
**Affected**: Process/Movement tables
**Description**: No change tracking (who changed what when) → LGPD compliance gap
**Effort**: M (3 days)
**Recommendation**: Add `audit_log` table with triggers

---

#### DB-006: No CHECK Constraint on Phase
**Category**: Integrity
**Severity**: MEDIUM
**Affected**: `processes.phase` column
**Description**: Invalid phase values (01-15) not validated at DB level
**Effort**: XS (15 min)
**SQL**: `ALTER TABLE processes ADD CHECK (phase IS NULL OR (phase >= '01' AND phase <= '15'));`

---

#### DB-007: No CHECK Constraint on CNJ Number
**Category**: Integrity
**Severity**: MEDIUM
**Affected**: `processes.number` column
**Description**: CNJ number format (20 digits) not validated
**Effort**: XS (15 min)
**SQL**: `ALTER TABLE processes ADD CHECK (LENGTH(number) = 20 AND number GLOB '[0-9]*');`

---

#### DB-008: Raw JSON Not Indexed
**Category**: Performance
**Severity**: MEDIUM
**Affected**: `processes.raw_data` (JSON field)
**Description**: No full-text or JSON indexes → complex queries slow
**Effort**: M (3 days)
**Recommendation**: Add JSON index if advanced queries needed (future optimization)

---

#### ADR-ARCH-001: ADR Divergence Not Documented
**Category**: Governance
**Severity**: MEDIUM
**Affected**: `docs/decisions/` (ADRs)
**Description**: ADR specifies PostgreSQL, implementation uses SQLite → divergence not recorded
**Effort**: XS (30 min)
**Recommendation**: Document SQLite choice rationale in new ADR

---

#### PATTERN-ARCH-001: No Repository Abstraction
**Category**: Code Quality
**Severity**: MEDIUM
**Affected**: `backend/services/process_service.py`
**Description**: No explicit Repository layer → SQLAlchemy ORM mixed with business logic
**Effort**: M (3 days)
**Recommendation**: Extract Repository pattern for better testability

---

#### EXT-ARCH-002: Fixed Timeout Without Configuration
**Category**: Configuration
**Severity**: MEDIUM
**Affected**: DataJud client (30s timeout)
**Description**: Timeout hardcoded; no per-endpoint configuration
**Effort**: XS (1 hour)
**Recommendation**: Make timeout configurable via settings

---

#### EXT-ARCH-003: Cascade Failure Risk
**Category**: Resilience
**Severity**: MEDIUM
**Affected**: DataJud integration
**Description**: Repeated failures don't back off → hammers struggling API
**Effort**: M (3 days)
**Recommendation**: Circuit breaker + jitter backoff

---

#### PERF-ARCH-002: Missing Indexes on Movement (also DB-001)
**Category**: Performance
**Severity**: MEDIUM (see DB-001 HIGH)
**Affected**: `movements` table query performance
**Effort**: XS
**Quick Win**: ✅ Combined with DB-001

---

#### PERF-ARCH-003: No Caching Layer
**Category**: Performance
**Severity**: MEDIUM
**Affected**: Frequent process lookups
**Description**: No Redis/Memcached → every query hits DB
**Effort**: L (1 week)
**Recommendation**: Add Redis layer (TTL 24h for processes)

---

#### PERF-ARCH-004: No Frontend Code Splitting
**Category**: Performance
**Severity**: MEDIUM
**Affected**: React bundle
**Description**: All components bundled together → large initial load
**Effort**: M (3 days)
**Recommendation**: Lazy load Dashboard, Settings, HistoryTab

---

#### CONFIG-ARCH-001: Secrets in .env Plaintext
**Category**: Security (same as SEC-ARCH-001)
**Severity**: MEDIUM (already CRITICAL above)
**Affected**: Environment variables

---

#### CONFIG-ARCH-002: Dead Code (OpenRouter Configuration)
**Category**: Code Quality
**Severity**: MEDIUM
**Affected**: `backend/config.py`, unused `OPENROUTER_API_KEY`
**Description**: LLM integration configured but never used
**Effort**: S (1 day)
**Recommendation**: Remove dead code or document future plan

---

#### BE-ARCH-004: OpenRouter Dead Code
**Category**: Code Quality
**Severity**: MEDIUM
**Affected**: Config, services
**Description**: OpenRouter API key configured but never called
**Effort**: S (1 day)
**Quick Win**: ✅ Remove unused config
**Recommendation**: Delete or document why for future LLM integration

---

#### TEST-ARCH-002: Outdated Tests
**Category**: Testing
**Severity**: MEDIUM
**Affected**: `backend/tests/test_phase_rules.py` (anomaly in phase 15)
**Description**: Tests have known failures (phase classification edge case)
**Effort**: M (3 days)
**Recommendation**: Update phase rules tests to cover all 15 phases correctly

---

#### TEST-ARCH-003: No Integration Tests (E2E)
**Category**: Testing
**Severity**: MEDIUM
**Affected**: Full API + Frontend stack
**Description**: Unit tests only → no end-to-end workflow validation
**Effort**: L (1 week)
**Recommendation**: Add Playwright/Cypress for full user flows

---

#### DB-009: Denormalized `court` Field
**Category**: Design
**Severity**: LOW (future cleanup)
**Affected**: `processes.court` (redundant with tribunal info)
**Description**: Legacy field; data duplicated
**Effort**: M (3 days refactor)
**Recommendation**: Remove after verifying no dependencies

---

#### DB-010: No Soft Deletes
**Category**: Compliance
**Severity**: LOW (LGPD future requirement)
**Affected**: Process, Movement tables
**Description**: Hard deletes only; no audit trail of deleted data
**Effort**: M (3 days)
**Recommendation**: Add `deleted_at` timestamps for soft delete support

---

### 🟢 LOW SEVERITY (7 débitos - Backlog)

#### ADR-ARCH-002: Undocumented Architectural Decisions
**Severity**: LOW
**Description**: Critical decisions lack ADRs (deployment strategy, state management)
**Effort**: S (1 day documentation)

---

#### FE-ARCH-001: Prop Drilling (same as FE-007)
**Severity**: LOW (Code Quality)
**Effort**: M

---

#### FE-ARCH-002: No Design System
**Severity**: LOW
**Description**: Tailwind ad-hoc; no componentized design system
**Effort**: XL (3-4 weeks)
**Recommendation**: Build component library (Button, Input, Card atoms) → Storybook

---

#### FE-ARCH-003: Duplicated Component State
**Severity**: LOW
**Description**: State replicated across components
**Effort**: M

---

#### FE-002: Modal Dialog Accessibility
**Severity**: LOW
**Affected**: ProcessDetails (JSON modal)
**Description**: Missing `role="dialog"`, `aria-modal`
**Effort**: 2 pts (20 min)

---

#### FE-006 (duplicate): Testing
[See CRITICAL section]

---

#### DEPLOY-ARCH-003: No Process Manager
**Severity**: LOW
**Description**: No PM2/systemd → manual restart required
**Effort**: S (1 day)

---

#### DEPLOY-ARCH-005: No Rollback Strategy
**Severity**: LOW
**Description**: No automated rollback on deployment failure
**Effort**: M (3 days)

---

#### DEPLOY-ARCH-006: Frontend Dev Server in Production
**Severity**: LOW (if used)
**Description**: Vite dev server slower than production build
**Effort**: S (1 day)

---

#### SEC-ARCH-004: No HTTPS Enforcement
**Severity**: LOW (local only, but future production)
**Description**: HTTPS not enforced; local OK, production needs it
**Effort**: S (1 day)

---

#### ERROR-ARCH-001: ErrorBoundary Limitations
**Severity**: LOW
**Description**: React Error Boundary doesn't catch async/event handler errors
**Effort**: M (3 days)
**Recommendation**: Implement additional error handlers for non-React errors

---

---

## Prioritization Matrix (Impacto vs Esforço)

```
EFFORT
     |
  20 |                    DB-002 (XL)
     |                    DEPLOY-001/002 (L)
     |                    PERF-ARCH-003/004
  15 |              TEST-ARCH-001 (XL)
     |              FE-006 (13pts)
     |              BE-ARCH-001
  10 |         SEC-ARCH-003 (M)
     |         LOG-ARCH-002 (M)
     |    PERF-ARCH-001 (L)
   5 |    BE-ARCH-002
     |    BE-ARCH-003 ERROR-ARCH-002
     | DB-001 DB-003 SEC-ARCH-002
   1 |XX DB-006/007 BE-ARCH-004
     +------+------+------+------+
         IMPACT (user-facing severity)
         LOW   MED   HIGH  CRIT
```

### Quadrante 1: Quick Wins (High Impact, Low Effort) 🎯
**Do FIRST — < 1 day total:**
1. ✅ **DB-001**: Add indexes (30 min, HIGH impact)
2. ✅ **DB-003**: Backup script (2 hours, HIGH impact)
3. ✅ **SEC-ARCH-002**: Rate limiting (2 hours, HIGH impact)
4. ✅ **BE-ARCH-004**: Remove dead code (30 min, MEDIUM impact)
5. ✅ **FE-001**: Label HTML (30 min, MEDIUM impact)

**Total Sprint 1: < 1 day | Removes 40% HIGH debits**

---

### Quadrante 2: Strategic (High Impact, High Effort) 🏗️
**Sprint 1-2 (Week 2-3):**
1. 🔴 **PERF-ARCH-001**: Async bulk (L, CRITICAL)
2. 🔴 **ERROR-ARCH-002**: Monitoring (M, CRITICAL)
3. 🔴 **TEST-ARCH-001**: Test coverage (XL, CRITICAL)
4. 🔴 **DEPLOY-ARCH-004**: Health checks (M, CRITICAL)
5. 🟠 **SEC-ARCH-001**: Secrets management (S, CRITICAL)

**Total: 2-3 weeks | Unblocks production**

---

### Quadrante 3: Technical Debt (Medium Impact, Medium Effort)
**Sprint 3-4 (Week 4-6):**
- BE-ARCH-001 (coupling) → M effort
- BE-ARCH-002 (retry logic) → S effort
- LOG-ARCH-002 (logging) → M effort
- DB-005 (audit trail) → M effort

---

### Quadrante 4: Backlog (Low Impact, High Effort)
**Future (if resources available):**
- DEPLOY-ARCH-001 (Docker) → L
- DEPLOY-ARCH-002 (CI/CD) → L
- PERF-ARCH-003 (Caching) → L
- FE-ARCH-002 (Design system) → XL
- DB-002 (PostgreSQL migration) → XL

---

## Remediation Roadmap

### Sprint 1: Critical Stabilization (Week 1)
**Goal:** Remove all CRITICAL debits blocking production

**Tasks:**
- [ ] SEC-ARCH-001: Secrets management
- [ ] DB-001/003: Indexes + backups (quick wins)
- [ ] SEC-ARCH-002: Rate limiting
- [ ] BE-ARCH-004: Remove OpenRouter dead code
- [ ] FE-001: Label HTML (quick win)

**Effort:** 5 days (4 devs × 1 day each)
**Acceptance:** All CRITICAL marked DONE or UNBLOCKED

---

### Sprint 2: Performance & Monitoring (Week 2-3)
**Goal:** Fix performance bottleneck + implement observability

**Tasks:**
- [ ] PERF-ARCH-001: Async bulk processing
- [ ] ERROR-ARCH-002: Centralized error monitoring (Sentry)
- [ ] DEPLOY-ARCH-004: Health checks + metrics
- [ ] BE-ARCH-002: Retry logic
- [ ] LOG-ARCH-002: Structured logging

**Effort:** 15 days (2 devs × 1 week each)
**Acceptance:** Bulk processing <30s, Sentry dashboard operational

---

### Sprint 3: Testing & Code Quality (Week 4-5)
**Goal:** Establish test infrastructure + refactor core services

**Tasks:**
- [ ] TEST-ARCH-001: Backend + Frontend test suite (target 70%)
- [ ] TEST-ARCH-002: Fix outdated tests
- [ ] BE-ARCH-001: ProcessService dependency injection
- [ ] EXT-ARCH-001: Circuit breaker pattern
- [ ] FE-006: React Testing Library setup

**Effort:** 20 days (3 devs × 1 week each)
**Acceptance:** >50% test coverage, CI/CD pipeline green

---

### Sprint 4: Deployment & Infrastructure (Week 6-7)
**Goal:** Containerize + setup CI/CD

**Tasks:**
- [ ] DEPLOY-ARCH-001: Docker + docker-compose
- [ ] DEPLOY-ARCH-002: GitHub Actions pipeline
- [ ] FE-ARCH-003: State management refactor (Context API)
- [ ] DB-005: Audit trail implementation
- [ ] SEC-ARCH-003: Authentication layer

**Effort:** 15 days (2 devs × 1 week each)
**Acceptance:** Automated deploy working, production-ready

---

### Sprint 5+: Polish & Optimization (Week 8+)
**Goal:** Address MEDIUM/LOW priority, plan DB migration

**Tasks:**
- [ ] PERF-ARCH-003: Redis caching
- [ ] FE-ARCH-002: Design system / Storybook
- [ ] DB-002: PostgreSQL migration planning (if scale demands)
- [ ] FE-004/FE-005: Complete WCAG 2.1 AA compliance
- [ ] Documentation + ADRs

**Effort:** 25+ days (ongoing)
**Acceptance:** Production hardened, design system established

---

## Effort Summary by Role

### Backend Developer (@dev)
**Total Effort:** 35-40 days

| Category | Days | Tasks |
|----------|------|-------|
| Performance | 5 | PERF-ARCH-001 (async) |
| Security | 4 | SEC-ARCH-001/002/003 |
| Resilience | 3 | BE-ARCH-002 (retry), EXT-ARCH-001 |
| Code Quality | 8 | BE-ARCH-001 (injection), PATTERN-ARCH-001 |
| Testing | 8 | TEST-ARCH-001/002/003 (backend tests) |
| Logging | 3 | LOG-ARCH-002 |
| Monitoring | 5 | ERROR-ARCH-002 |

---

### Frontend Developer (@dev)
**Total Effort:** 20-25 days

| Category | Days | Tasks |
|----------|------|-------|
| Accessibility | 5 | FE-001/003/004/005 |
| Testing | 6 | FE-006 (test suite) |
| Code Quality | 4 | FE-ARCH-001/003 (Context API) |
| Performance | 3 | PERF-ARCH-004 (code splitting) |
| Design System | 8 | FE-ARCH-002 (Storybook) |

---

### DevOps / Infrastructure (@devops)
**Total Effort:** 10-12 days

| Category | Days | Tasks |
|----------|------|-------|
| Deployment | 5 | DEPLOY-ARCH-001/002 (Docker + CI/CD) |
| Monitoring | 3 | DEPLOY-ARCH-004 (health checks) |
| Backup | 1 | DB-003 (backup script) |

---

### Database / Data Engineer (@data-engineer)
**Total Effort:** 8-10 days

| Category | Days | Tasks |
|----------|------|-------|
| Performance | 1 | DB-001 (indexes) |
| Operations | 1 | DB-003 (backup) |
| Integrity | 1 | DB-006/007 (constraints) |
| Compliance | 3 | DB-005 (audit trail) |
| Migration | 10+ | DB-002 (PostgreSQL, future) |

---

## Implementation Dependencies Graph

```
SEC-ARCH-001 (Secrets)
    ↓
All deployment/monitoring tasks

PERF-ARCH-001 (Async)
    ↓
TEST-ARCH-001 (Tests needed)
    ↓
DEPLOY-ARCH-002 (CI/CD)

BE-ARCH-002 (Retry)
    ↓
EXT-ARCH-001 (Circuit breaker)

ERROR-ARCH-002 (Monitoring)
    ↓
DEPLOY-ARCH-004 (Health checks)
```

---

## Risk Assessment

### Risks if Debits NOT Fixed

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| Security breach (SEC-ARCH-001) | HIGH | CRITICAL | Fix in Sprint 1 |
| Production downtime (DEPLOY-ARCH-004) | MEDIUM | HIGH | Implement monitoring Sprint 2 |
| User abandonment (PERF-ARCH-001) | MEDIUM | HIGH | Async bulk Sprint 2 |
| Regressions ship (TEST-ARCH-001) | HIGH | MEDIUM | Test suite Sprint 3 |
| Database failure (DB-002/003) | MEDIUM | HIGH | Backup + monitoring Sprint 1 |
| Accessibility violations (FE-004/006) | LOW | MEDIUM | Gradual WCAG compliance Sprint 4+ |

---

## Success Criteria

### End of Sprint 1
- ✅ All CRITICAL debits in progress or unblocked
- ✅ Database has backups + indexes
- ✅ Secrets management working
- ✅ Rate limiting deployed

### End of Sprint 2
- ✅ Bulk processing <30s for 50 items
- ✅ Sentry monitoring dashboard operational
- ✅ Health checks + metrics exposed
- ✅ Error tracking working (frontend + backend)

### End of Sprint 3
- ✅ Backend test coverage >60%
- ✅ Frontend test coverage >40%
- ✅ ProcessService refactored + dependency injection
- ✅ CI/CD pipeline validates tests

### End of Sprint 4
- ✅ Docker containers built + running
- ✅ GitHub Actions pipeline fully automated
- ✅ Production deployment workflow established
- ✅ Rollback strategy tested

### Production Readiness Checklist
- [ ] All CRITICAL debits resolved
- [ ] Test coverage >70% (backend), >60% (frontend)
- [ ] Monitoring/alerting operational
- [ ] Backup/disaster recovery tested
- [ ] WCAG 2.1 AA >80% compliance
- [ ] Authentication/authorization implemented
- [ ] Rate limiting active
- [ ] CI/CD pipeline fully automated
- [ ] Docker deployment working
- [ ] Documentation complete (ADRs, runbooks)

---

## Consolidated Debit Table (Reference)

| ID | Category | Severity | Effort | Status | Sprint |
|----|----------|----------|--------|--------|--------|
| SEC-ARCH-001 | Security | CRITICAL | S | OPEN | 1 |
| PERF-ARCH-001 | Performance | CRITICAL | L | OPEN | 2 |
| ERROR-ARCH-002 | Ops | CRITICAL | M | OPEN | 2 |
| TEST-ARCH-001 | Testing | CRITICAL | XL | OPEN | 3 |
| DEPLOY-ARCH-004 | Ops | CRITICAL | M | OPEN | 2 |
| DB-002 | Scalability | CRITICAL | XL | OPEN | Future |
| FE-006 | Testing | CRITICAL | 13pts | OPEN | 3 |
| BE-ARCH-001 | Quality | HIGH | M | OPEN | 3 |
| BE-ARCH-002 | Resilience | HIGH | S | OPEN | 2 |
| DB-001 | Performance | HIGH | XS | OPEN | 1 |
| DB-003 | Ops | HIGH | S | OPEN | 1 |
| DB-004 | Integrity | HIGH | S | OPEN | 2 |
| LOG-ARCH-002 | Ops | HIGH | M | OPEN | 2 |
| SEC-ARCH-002 | Security | HIGH | S | OPEN | 1 |
| SEC-ARCH-003 | Security | HIGH | M | OPEN | 4 |
| DEPLOY-ARCH-001 | Ops | HIGH | L | OPEN | 4 |
| DEPLOY-ARCH-002 | Ops | HIGH | L | OPEN | 4 |
| FE-004 | A11y | HIGH | 8pts | OPEN | 4 |
| EXT-ARCH-001 | Resilience | HIGH | M | OPEN | 3 |
| [... 29 MEDIUM/LOW debits ...] | ... | ... | ... | OPEN | 3-5+ |

---

## Next Steps

### Fase 4 → Complete ✅
Document consolidated with categorization, severity, effort, dependencies, roadmap

### Fase 5 → @data-engineer
Validar débitos DB-* + fornecer DDL concreto para fixes

### Fase 6 → @ux-design-expert
Validar débitos FE-* + fornecer design tokens/accessibility roadmap

### Fase 7 → @qa
QA Gate: APPROVED (proceed to Fase 8) or NEEDS WORK (gaps to address)

---

## Document Metadata

**Created:** 2026-02-21
**Author:** @architect (Aria)
**Status:** DRAFT (awaiting specialist reviews Fases 5-6)
**Consolidation Source:**
- system-architecture.md (Fase 1) → 32 debits
- DB-AUDIT.md (Fase 2) → 10 debits
- frontend-spec.md (Fase 3) → 7 debits

**Total Debits:** 49
**CRITICAL:** 7 (14%)
**HIGH:** 14 (29%)
**MEDIUM:** 21 (43%)
**LOW:** 7 (14%)

**Next Review:** Fase 5 (@data-engineer) — Database specialist validation

---

**Fim da Fase 4: Draft de Débito Técnico** ✅
