# EPIC: Brownfield Technical Debt Remediation

**Epic ID:** EPIC-REMEDIATION-001
**Criado por:** @pm (Morgan)
**Data:** 2026-02-22
**Status:** Ready for Development
**Fase:** Brownfield Discovery - Fase 10 (Epic Creation)
**Fonte:** technical-debt-assessment.md (67 débitos)

---

## Epic Overview

**Objetivo:** Remediar 67 débitos técnicos identificados no Brownfield Discovery audit, transformando o sistema de MODERADO RISCO para PRODUCTION READY com conformidade legal (WCAG AA, LGPD), performance otimizada (80% faster bulk), e observabilidade completa (Sentry monitoring).

**Business Value:**
- **Performance:** Bulk search 2-5min → <30s (80% faster)
- **Segurança:** Zero critical vulnerabilities (secrets vault, XSS audit)
- **Qualidade:** Test coverage 15% → 70% (regression safety)
- **Compliance:** WCAG 2.1 AA 40% → 90% (legal requirement)
- **Confiabilidade:** Uptime SLA 99.5% (monitoring + health checks)

**Investimento:** R$ 175k | **Duração:** 14-19 semanas | **ROI:** 150-250% em 12 meses

---

## Epic Breakdown

**Total Stories:** **67**
- Sprint 1 (Quick Wins): 10 stories
- Sprint 2 (Performance + Observability): 5 stories
- Sprint 3 (Testing): 5 stories
- Sprint 4 (Deployment): 6 stories
- Sprint 5+ (Polish + Migration): 41 stories

---

## Sprint 1: Critical Stabilization (10 Stories)

### STORY-REM-001: Add Missing Database Indexes
**Debit ID:** DB-001
**Complexity:** 2 pts (XS - 30 min)
**Priority:** CRITICAL
**Assignee:** Data Engineer

**Description:**
Create 3 missing indexes on Movement table to eliminate N+1 query bottleneck and achieve 20-100x query speedup.

**Acceptance Criteria:**
- [ ] CREATE INDEX idx_movement_process_date ON movements(process_id, date DESC)
- [ ] CREATE INDEX idx_movement_code ON movements(code)
- [ ] CREATE INDEX idx_movement_date ON movements(date DESC)
- [ ] EXPLAIN QUERY PLAN shows "SEARCH TABLE movements USING INDEX" (not SCAN)
- [ ] Performance test: Movement query latency <5ms (currently 100-500ms)

**Technical Notes:**
```sql
-- Execute in production database
CREATE INDEX IF NOT EXISTS idx_movement_process_date ON movements(process_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_movement_code ON movements(code);
CREATE INDEX IF NOT EXISTS idx_movement_date ON movements(date DESC);

-- Verify
EXPLAIN QUERY PLAN
SELECT * FROM movements WHERE process_id = 123 ORDER BY date DESC;
-- Expected: SEARCH TABLE movements USING INDEX idx_movement_process_date
```

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-002: Implement Automated Database Backup
**Debit ID:** DB-003
**Complexity:** 3 pts (S - 2 hours)
**Priority:** HIGH
**Assignee:** DevOps Engineer

**Description:**
Create bash script for daily automated SQLite backup with integrity checks, 30-day retention, and cron scheduling.

**Acceptance Criteria:**
- [ ] Script `scripts/backup_db.sh` created
- [ ] Backup runs with `.backup` command (transaction-safe)
- [ ] Gzip compression applied
- [ ] Integrity check (PRAGMA integrity_check) runs before backup
- [ ] 30-day retention (old backups auto-deleted)
- [ ] Cron job scheduled (daily 2 AM)
- [ ] Manual restore script `scripts/restore_database.sh` tested

**Technical Notes:**
```bash
#!/bin/bash
# backup_db.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_FILE="consulta_processual.db"
BACKUP_DIR="backups"

# Integrity check
sqlite3 $DB_FILE "PRAGMA integrity_check;" || exit 1

# Backup + compress
sqlite3 $DB_FILE ".backup '$BACKUP_DIR/backup_${TIMESTAMP}.db'"
gzip $BACKUP_DIR/backup_${TIMESTAMP}.db

# Cleanup old backups
find $BACKUP_DIR -name "backup_*.db.gz" -mtime +30 -delete
```

**Cron setup:**
```
0 2 * * * /path/to/backup_db.sh >> /path/to/logs/backup.log 2>&1
```

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-003: Implement Secrets Vault
**Debit ID:** SEC-ARCH-001
**Complexity:** 5 pts (S - 1 day)
**Priority:** CRITICAL
**Assignee:** Backend Developer

**Description:**
Migrate plaintext secrets from .env to encrypted vault (dotenv-vault or AWS Secrets Manager) to prevent credential leak.

**Acceptance Criteria:**
- [ ] Vault solution selected (dotenv-vault or AWS Secrets Manager)
- [ ] DATAJUD_APIKEY migrated to vault
- [ ] DATABASE_URL migrated to vault
- [ ] SENTRY_DSN migrated to vault (if applicable)
- [ ] `.env` removed from repo (already in .gitignore, verify)
- [ ] `backend/config.py` updated to fetch from vault
- [ ] API keys rotated (new keys generated after migration)
- [ ] Documentation updated (README.md, deployment guide)

**Technical Notes (dotenv-vault option):**
```bash
# Install dotenv-vault CLI
npm install -g dotenv-vault

# Initialize vault
dotenv-vault new

# Push secrets to vault
dotenv-vault push

# Fetch encrypted .env.vault file (commit this)
# Never commit .env directly
```

**Technical Notes (AWS Secrets Manager option):**
```python
# backend/config.py
import boto3
client = boto3.client('secretsmanager', region_name='us-east-1')

def get_secret(secret_name):
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

DATAJUD_APIKEY = get_secret('consulta-processo/datajud-apikey')
```

**Dependencies:** None (but blocks DEPLOY-ARCH-001/002)
**Sprint:** Sprint 1

---

### STORY-REM-004: Add API Rate Limiting
**Debit ID:** SEC-ARCH-002
**Complexity:** 3 pts (S - 2 hours)
**Priority:** HIGH
**Assignee:** Backend Developer

**Description:**
Implement SlowAPI rate limiter (100 requests/minute per IP) to prevent DoS attacks.

**Acceptance Criteria:**
- [ ] SlowAPI library installed (`pip install slowapi`)
- [ ] Limiter configured (100/minute per remote address)
- [ ] Applied to /api/search endpoint
- [ ] Applied to /api/bulk endpoint
- [ ] 429 response returned when rate exceeded
- [ ] Rate limit headers included (X-RateLimit-Limit, X-RateLimit-Remaining)
- [ ] Test: 101 requests → 101st request returns 429 Too Many Requests

**Technical Notes:**
```python
# backend/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/search")
@limiter.limit("100/minute")
async def search_process(cnj: str):
    ...

@app.post("/api/bulk")
@limiter.limit("50/minute")  # Lower for bulk
async def bulk_search(numeros: list):
    ...
```

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-005: Add CORS Whitelist Configuration
**Debit ID:** SEC-ARCH-004
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Backend Developer

**Description:**
Audit and restrict CORS configuration to whitelist only trusted origins (prevent XSS from malicious domains).

**Acceptance Criteria:**
- [ ] CORS middleware configured with explicit allow_origins list
- [ ] Production domain whitelisted (e.g., https://consulta-processo.example.com)
- [ ] Localhost allowed for development (http://localhost:5173)
- [ ] allow_origins=["*"] removed (security risk)
- [ ] Test: Request from non-whitelisted origin → CORS error

**Technical Notes:**
```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://consulta-processo.example.com",  # Production
    "http://localhost:5173",  # Dev frontend
    "http://localhost:3000",  # Alternative dev port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-006: Remove OpenRouter Dead Code
**Debit ID:** BE-ARCH-004
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Backend Developer

**Description:**
Delete unused OpenRouter configuration and API key from codebase (legacy code no longer needed).

**Acceptance Criteria:**
- [ ] OPENROUTER_API_KEY removed from `.env.example`
- [ ] OpenRouterConfig class deleted from `backend/config.py`
- [ ] Any imports referencing OpenRouter removed
- [ ] Grep search confirms no references to "openrouter" remain
- [ ] Tests still pass (confirm no dependencies)

**Technical Notes:**
```bash
# Search for all references
grep -r "openrouter" backend/
grep -r "OpenRouter" backend/

# Files likely affected:
# - backend/.env.example (remove OPENROUTER_API_KEY line)
# - backend/config.py (remove OpenRouterConfig class)
```

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-007: Add Label HTML Associations (Accessibility)
**Debit ID:** FE-001
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Frontend Developer

**Description:**
Add htmlFor attribute to all form labels (15+ fields in BulkSearch.jsx and Settings.jsx) for WCAG 1.3.1 compliance.

**Acceptance Criteria:**
- [ ] BulkSearch.jsx textarea "Listagem de Números" has htmlFor="bulk-numbers-textarea"
- [ ] Settings.jsx: All 15+ form fields have htmlFor associations
- [ ] Axe accessibility audit passes (no "label must have htmlFor" errors)
- [ ] Screen reader test: Labels announced when input focused

**Technical Notes:**
```jsx
// ❌ BEFORE
<label className="...">Listagem de Números</label>
<textarea className="..." />

// ✅ AFTER
<label htmlFor="bulk-numbers-textarea" className="...">
  Listagem de Números
</label>
<textarea id="bulk-numbers-textarea" className="..." />
```

**Files:**
- frontend/src/components/BulkSearch.jsx
- frontend/src/components/Settings.jsx

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-008: Add Phase CHECK Constraint
**Debit ID:** DB-006
**Complexity:** 2 pts (XS - 15 min)
**Priority:** MEDIUM
**Assignee:** Data Engineer

**Description:**
Add CHECK constraint to processes.phase column to validate phase values (01-15 only).

**Acceptance Criteria:**
- [ ] CHECK constraint added: `phase IS NULL OR (phase >= '01' AND phase <= '15')`
- [ ] Test: INSERT with phase='99' → CHECK constraint failed
- [ ] Test: INSERT with phase='05' → Success
- [ ] Test: INSERT with phase=NULL → Success (allowed)

**Technical Notes:**
```sql
-- SQLite: Recreate table with constraint
CREATE TABLE processes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL,
    phase TEXT CHECK (phase IS NULL OR (phase >= '01' AND phase <= '15')),
    ...
);

-- Copy data
INSERT INTO processes_new SELECT * FROM processes;

-- Drop old, rename new
DROP TABLE processes;
ALTER TABLE processes_new RENAME TO processes;

-- Recreate indexes
CREATE UNIQUE INDEX idx_process_number ON processes(number);
```

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-009: Add CNJ Number CHECK Constraint
**Debit ID:** DB-007
**Complexity:** 2 pts (XS - 15 min)
**Priority:** MEDIUM
**Assignee:** Data Engineer

**Description:**
Add CHECK constraint to processes.number column to validate CNJ format (20 numeric digits only).

**Acceptance Criteria:**
- [ ] CHECK constraint added: `LENGTH(number) = 20 AND number GLOB '[0-9]*'`
- [ ] Test: INSERT with number='123' → CHECK constraint failed
- [ ] Test: INSERT with number='ABC12345678901234567' → CHECK constraint failed
- [ ] Test: INSERT with number='12345678901234567890' → Success

**Technical Notes:**
```sql
-- SQLite: Same table recreation pattern as DB-006
CREATE TABLE processes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL
        CHECK (LENGTH(number) = 20 AND number GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    ...
);
```

**PostgreSQL version (simpler):**
```sql
ALTER TABLE processes
ADD CONSTRAINT check_cnj_format
CHECK (number ~ '^[0-9]{20}$');
```

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-010: Configure Database Connection Pooling
**Debit ID:** DB-011
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Backend Developer

**Description:**
Configure SQLAlchemy connection pool (StaticPool for SQLite) to prevent connection exhaustion under load.

**Acceptance Criteria:**
- [ ] Engine configured with `poolclass=StaticPool` (for SQLite)
- [ ] `connect_args={'check_same_thread': False}` set (for FastAPI async)
- [ ] Documentation updated with future PostgreSQL pool config
- [ ] Load test: 50 concurrent requests → No connection errors

**Technical Notes:**
```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool  # For SQLite

# SQLite configuration
engine = create_engine(
    'sqlite:///consulta_processual.db',
    poolclass=StaticPool,  # Required for SQLite (single connection)
    connect_args={'check_same_thread': False}  # Required for FastAPI async
)

# PostgreSQL configuration (future - document only)
# engine = create_engine(
#     DATABASE_URL,
#     pool_size=10,  # 10 permanent connections
#     max_overflow=20,  # +20 temporary connections
#     pool_pre_ping=True,  # Health check before using connection
#     pool_recycle=3600  # Recycle connections after 1 hour
# )
```

**Dependencies:** None
**Sprint:** Sprint 1

---

### STORY-REM-011: Add Log Rotation
**Debit ID:** OPS-ARCH-001
**Complexity:** 2 pts (XS - 30 min)
**Priority:** MEDIUM
**Assignee:** Backend Developer

**Description:**
Configure Python logging with RotatingFileHandler (10 MB max, 5 backups) to prevent disk full from unbounded log growth.

**Acceptance Criteria:**
- [ ] RotatingFileHandler configured (10 MB max per file)
- [ ] 5 backup files retained (app.log, app.log.1, app.log.2, ..., app.log.5)
- [ ] Old logs deleted automatically when exceeding 5 backups
- [ ] Test: Generate 11 MB of logs → 2 files created (10 MB + 1 MB)

**Technical Notes:**
```python
# backend/main.py
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory
import os
os.makedirs('logs', exist_ok=True)

# Configure rotating handler
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5  # Keep 5 old files (app.log.1 to app.log.5)
)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger()
logger.addHandler(handler)
```

**Dependencies:** None
**Sprint:** Sprint 1

---

## Sprint 2: Performance & Observability (5 Stories)

### STORY-REM-012: Implement Async Bulk Processing
**Debit ID:** PERF-ARCH-001
**Complexity:** 13 pts (L - 3-5 days)
**Priority:** CRITICAL
**Assignee:** Backend Developer

**Description:**
Refactor sequential bulk_search() to async with asyncio.gather() for parallel DataJud API calls, achieving <30s for 50 CNJ (currently 2-5 min).

**Acceptance Criteria:**
- [ ] `bulk_search_async()` function created using async/await
- [ ] ClientSession from aiohttp used for parallel HTTP requests
- [ ] Concurrency limit = 10 (avoid overwhelming DataJud API)
- [ ] Error handling: return_exceptions=True (partial failures ok)
- [ ] Performance test: 50 CNJ in <30s (80% latency reduction)
- [ ] Frontend updated to handle async response
- [ ] Unit tests for async function

**Technical Notes:**
```python
# backend/services/process_service.py
import asyncio
from aiohttp import ClientSession

async def bulk_search_async(self, numeros: list[str]):
    async with ClientSession() as session:
        tasks = []
        for numero in numeros:
            task = self._fetch_datajud_async(session, numero)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def _fetch_datajud_async(self, session, numero):
    async with session.get(f"{DATAJUD_URL}/processos/{numero}") as response:
        if response.status == 200:
            return await response.json()
        raise Exception(f"DataJud error: {response.status}")
```

**Dependencies:** None (but unlocks TEST-ARCH-001 async tests)
**Sprint:** Sprint 2

---

### STORY-REM-013: Integrate Sentry Error Monitoring
**Debit ID:** ERROR-ARCH-002
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** CRITICAL
**Assignee:** Backend Developer

**Description:**
Integrate Sentry SDK for error tracking, alerts (Slack), and performance monitoring (traces).

**Acceptance Criteria:**
- [ ] Sentry project created (sentry.io account)
- [ ] SENTRY_DSN environment variable configured
- [ ] sentry_sdk.init() in backend/main.py
- [ ] Frontend Sentry integration (optional but recommended)
- [ ] Test error triggered → appears in Sentry dashboard
- [ ] Slack alerts configured for CRITICAL errors
- [ ] Tracing enabled (traces_sample_rate=0.1)
- [ ] User context captured (user_id if auth exists)

**Technical Notes:**
```python
# backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of requests traced
    environment=os.getenv('ENVIRONMENT', 'development')
)

# Test error
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
```

**Slack Integration:**
- Sentry Settings → Integrations → Slack
- Alert rule: "When event level is CRITICAL → Send Slack notification"

**Dependencies:** None (but integrates with DEPLOY-ARCH-004 health checks)
**Sprint:** Sprint 2

---

### STORY-REM-014: Add Health Check Endpoints
**Debit ID:** DEPLOY-ARCH-004
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** CRITICAL
**Assignee:** Backend Developer

**Description:**
Create /health endpoint (liveness/readiness probes) for uptime monitoring and Kubernetes compatibility.

**Acceptance Criteria:**
- [ ] GET /health endpoint returns 200 OK + JSON status
- [ ] Database connectivity check included
- [ ] API availability check (optional DataJud ping)
- [ ] Response time <100ms (fast probe)
- [ ] 503 Service Unavailable if database down
- [ ] Uptime monitoring configured (UptimeRobot or similar)
- [ ] Kubernetes liveness/readiness probes documented

**Technical Notes:**
```python
# backend/api/endpoints/health.py
from fastapi import APIRouter, HTTPException
from backend.database import db

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        # Database check
        db.execute("SELECT 1")

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {str(e)}")

@router.get("/ready")
async def readiness_check():
    # More comprehensive check (database + API)
    try:
        db.execute("SELECT 1")
        # Optional: Ping DataJud API
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

**Kubernetes probe config:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

**Dependencies:** None
**Sprint:** Sprint 2

---

### STORY-REM-015: Implement Retry Logic for DataJud API
**Debit ID:** BE-ARCH-002
**Complexity:** 3 pts (S - 1 day)
**Priority:** HIGH
**Assignee:** Backend Developer

**Description:**
Add exponential backoff retry logic (3 attempts, 1s/2s/4s delays) for DataJud API calls to handle transient failures.

**Acceptance Criteria:**
- [ ] Retry decorator or library used (tenacity or custom)
- [ ] Max 3 retry attempts
- [ ] Exponential backoff: 1s, 2s, 4s delays
- [ ] Retry only on transient errors (503, 429, connection timeout)
- [ ] Do NOT retry on 4xx errors (client errors)
- [ ] Test: DataJud returns 503 → retries 3x → eventual success or failure

**Technical Notes:**
```python
# Install tenacity: pip install tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(httpx.HTTPStatusError)
)
async def fetch_datajud_with_retry(numero: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DATAJUD_URL}/processos/{numero}")
        response.raise_for_status()  # Raises HTTPStatusError on 4xx/5xx
        return response.json()
```

**Dependencies:** None
**Sprint:** Sprint 2

---

### STORY-REM-016: Centralized Logging with CloudWatch
**Debit ID:** LOG-ARCH-002
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** HIGH
**Assignee:** Backend Developer

**Description:**
Integrate AWS CloudWatch Logs for centralized logging (aggregates logs from multiple instances, searchable).

**Acceptance Criteria:**
- [ ] watchtower library installed (`pip install watchtower`)
- [ ] CloudWatch log group created: `/app/consulta-processo`
- [ ] Backend logs streamed to CloudWatch
- [ ] Frontend logs streamed to CloudWatch (optional)
- [ ] Log retention: 30 days
- [ ] CloudWatch Insights query tested (search for errors)
- [ ] IAM permissions configured (logs:PutLogEvents)

**Technical Notes:**
```python
# backend/main.py
import logging
import watchtower

# CloudWatch handler
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group_name='/app/consulta-processo',
    stream_name='backend',
    use_queues=True
)
cloudwatch_handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.addHandler(cloudwatch_handler)
```

**CloudWatch Insights Query Example:**
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

**Dependencies:** None
**Sprint:** Sprint 2

---

## Sprint 3: Testing Foundation (5 Stories)

### STORY-REM-017: Backend Unit Tests (70% Coverage)
**Debit ID:** TEST-ARCH-001
**Complexity:** 21 pts (XL - 2-3 weeks)
**Priority:** CRITICAL
**Assignee:** Backend Developer

**Description:**
Create comprehensive backend unit test suite using pytest, achieving 70% line coverage and 60% branch coverage.

**Acceptance Criteria:**
- [ ] pytest + pytest-cov configured
- [ ] Tests for process_service.py (bulk_search, get_or_update_process)
- [ ] Tests for phase_analyzer.py (classification logic)
- [ ] Tests for API endpoints (search, bulk, health)
- [ ] Tests for database models (Process, Movement)
- [ ] Async tests for async functions (using pytest-asyncio)
- [ ] Coverage report: 70% lines, 60% branches
- [ ] CI pipeline runs tests automatically

**Technical Notes:**
```python
# tests/test_process_service.py
import pytest
from backend.services.process_service import ProcessService

@pytest.fixture
def service():
    return ProcessService()

def test_valid_cnj_number(service):
    result = service.validate_cnj('12345678901234567890')
    assert result is True

def test_invalid_cnj_too_short(service):
    result = service.validate_cnj('123')
    assert result is False

@pytest.mark.asyncio
async def test_bulk_search_async(service):
    numeros = ['12345678901234567890', '09876543210987654321']
    results = await service.bulk_search_async(numeros)
    assert len(results) == 2
```

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=backend --cov-report=html --cov-report=term-missing --cov-fail-under=70
```

**Dependencies:** PERF-ARCH-001 (async tests require async code)
**Sprint:** Sprint 3

---

### STORY-REM-018: E2E Tests with Playwright
**Debit ID:** TEST-ARCH-002
**Complexity:** 13 pts (L - 1 week)
**Priority:** HIGH
**Assignee:** QA Engineer / Frontend Developer

**Description:**
Create E2E test suite with Playwright covering 3 critical user flows (search, bulk, dashboard).

**Acceptance Criteria:**
- [ ] Playwright installed and configured
- [ ] Test 1: Single process search → view details → export
- [ ] Test 2: Bulk search (file upload) → view results → export CSV
- [ ] Test 3: Dashboard → view charts → filter by tribunal
- [ ] Tests run in CI pipeline (GitHub Actions)
- [ ] Screenshots on failure (artifacts uploaded)
- [ ] Test coverage: 80% of critical flows

**Technical Notes:**
```javascript
// e2e/search-flow.spec.js
import { test, expect } from '@playwright/test';

test('single process search flow', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Search for process
  await page.fill('[aria-label="Número CNJ"]', '12345678901234567890');
  await page.click('button:has-text("Buscar")');

  // Wait for results
  await expect(page.locator('article')).toBeVisible({ timeout: 5000 });

  // Check process details loaded
  await expect(page.locator('h1')).toContainText('Processo');

  // Open movements timeline
  await expect(page.locator('ol')).toBeVisible();

  // Export JSON
  await page.click('button:has-text("Exportar")');
  const downloadPromise = page.waitForEvent('download');
  await page.click('text=JSON');
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toContain('.json');
});
```

**Dependencies:** None
**Sprint:** Sprint 3

---

### STORY-REM-019: Refactor ProcessService (Decouple DataJud Adapter)
**Debit ID:** BE-ARCH-001
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** HIGH
**Assignee:** Backend Developer

**Description:**
Extract DataJud API logic from ProcessService into separate adapter class using dependency injection for better testability.

**Acceptance Criteria:**
- [ ] DataJudAdapter class created (`backend/adapters/datajud_adapter.py`)
- [ ] ProcessService receives adapter via dependency injection
- [ ] Mock adapter created for unit tests
- [ ] All existing tests still pass
- [ ] No direct httpx calls in ProcessService (delegated to adapter)
- [ ] Code complexity reduced (Cyclomatic complexity <10)

**Technical Notes:**
```python
# backend/adapters/datajud_adapter.py
class DataJudAdapter:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    async def fetch_process(self, numero: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/processos/{numero}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return response.json()

# backend/services/process_service.py
class ProcessService:
    def __init__(self, datajud_adapter: DataJudAdapter):
        self.datajud = datajud_adapter

    async def get_or_update_process(self, numero: str):
        # Delegate to adapter
        data = await self.datajud.fetch_process(numero)
        # Process data
        return self._save_to_db(data)
```

**Dependencies:** None
**Sprint:** Sprint 3

---

### STORY-REM-020: Implement Circuit Breaker for DataJud API
**Debit ID:** EXT-ARCH-001
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** HIGH
**Assignee:** Backend Developer

**Description:**
Add circuit breaker pattern (using pybreaker) to DataJud API calls to prevent cascading failures when DataJud is down.

**Acceptance Criteria:**
- [ ] pybreaker library installed (`pip install pybreaker`)
- [ ] CircuitBreaker configured: 5 failures → open, 60s timeout
- [ ] State transitions logged (closed → open → half-open → closed)
- [ ] Fast-fail when circuit open (don't wait for timeout)
- [ ] Test: 5 consecutive failures → circuit opens → 6th request fails immediately

**Technical Notes:**
```python
# Install: pip install pybreaker
from pybreaker import CircuitBreaker

# Configure circuit breaker
datajud_breaker = CircuitBreaker(
    fail_max=5,  # Open after 5 failures
    timeout_duration=60,  # Stay open for 60 seconds
    expected_exception=httpx.HTTPError
)

@datajud_breaker
async def fetch_datajud_with_breaker(numero: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DATAJUD_URL}/processos/{numero}")
        response.raise_for_status()
        return response.json()
```

**Circuit States:**
- **Closed:** Normal operation
- **Open:** Failures threshold reached, fail fast
- **Half-Open:** After timeout, test with 1 request

**Dependencies:** None
**Sprint:** Sprint 3

---

### STORY-REM-021: Frontend Testing Setup (Vitest + RTL)
**Debit ID:** FE-006 (initial setup)
**Complexity:** 8 pts (M - 2-3 days)
**Priority:** HIGH
**Assignee:** Frontend Developer

**Description:**
Setup Vitest + React Testing Library, create tests for 3 critical components (ProcessSearch, BulkSearch, Dashboard).

**Acceptance Criteria:**
- [ ] Vitest + @testing-library/react installed
- [ ] vitest.config.js configured (jsdom environment)
- [ ] Test setup file created (src/test/setup.js)
- [ ] ProcessSearch.test.jsx: 3 tests (validation, submit, loading)
- [ ] BulkSearch.test.jsx: 3 tests (file upload, export, results)
- [ ] Dashboard.test.jsx: 3 tests (KPIs, charts, empty state)
- [ ] Coverage report: >40% (foundation, 70% target later)
- [ ] CI runs frontend tests

**Technical Notes:**
```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 70,
      branches: 60
    }
  }
});
```

**Dependencies:** None
**Sprint:** Sprint 3

---

## Sprint 4: Deployment Readiness (6 Stories)

### STORY-REM-022: Docker Containerization
**Debit ID:** DEPLOY-ARCH-001
**Complexity:** 13 pts (L - 5-7 days)
**Priority:** HIGH
**Assignee:** DevOps Engineer

**Description:**
Create Docker images for backend (FastAPI) and frontend (Nginx + Vite build), with docker-compose for local development.

**Acceptance Criteria:**
- [ ] Dockerfile created for backend (Python 3.11, multi-stage build)
- [ ] Dockerfile created for frontend (Node 20 build → Nginx serve)
- [ ] docker-compose.yml for local dev (backend + frontend + database)
- [ ] .dockerignore configured (.env, node_modules, .git)
- [ ] Image builds successfully: `docker build -t consulta-processo-backend .`
- [ ] Container runs: `docker run -p 8000:8000 consulta-processo-backend`
- [ ] Health check passes inside container
- [ ] Image size optimized (<500 MB backend, <100 MB frontend)

**Technical Notes:**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Dependencies:** SEC-ARCH-001 (secrets vault needed for env vars)
**Sprint:** Sprint 4

---

### STORY-REM-023: CI/CD Pipeline with GitHub Actions
**Debit ID:** DEPLOY-ARCH-002
**Complexity:** 13 pts (L - 5-7 days)
**Priority:** HIGH
**Assignee:** DevOps Engineer

**Description:**
Create GitHub Actions CI/CD pipeline (lint → test → build → deploy) with automated deployment to staging/production.

**Acceptance Criteria:**
- [ ] .github/workflows/ci.yml created
- [ ] Pipeline stages: lint → test → build → deploy
- [ ] Backend: pylint, pytest, coverage report
- [ ] Frontend: eslint, vitest, build
- [ ] Docker image pushed to registry (Docker Hub or GitHub Container Registry)
- [ ] Deployment to staging on `develop` branch push
- [ ] Deployment to production on `main` branch push (manual approval)
- [ ] Status badge added to README.md

**Technical Notes:**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pylint
      - run: pylint backend/

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest --cov=backend --cov-fail-under=70

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:coverage

  build:
    needs: [lint, test-backend, test-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          context: backend
          push: true
          tags: ghcr.io/org/consulta-processo-backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: echo "Deploy to production"
      # Add deployment steps (SSH to server, docker pull, restart)
```

**Dependencies:** DEPLOY-ARCH-001 (Docker image needed)
**Sprint:** Sprint 4

---

### STORY-REM-024: Loading States UI Consistency
**Debit ID:** FE-ARCH-003
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Frontend Developer

**Description:**
Create unified LoadingState, SkeletonLoader, and ErrorState components for consistent UX across all components.

**Acceptance Criteria:**
- [ ] LoadingState component (spinner, skeleton, text variants)
- [ ] SkeletonCard, SkeletonTable components created
- [ ] ErrorState component (with retry button)
- [ ] All 9 components migrated to use unified loading states
- [ ] Storybook stories created (optional documentation)
- [ ] Loading → Success transition smooth (no content jump)

**Technical Notes:**
```jsx
// src/components/LoadingState.jsx
export const LoadingState = ({ variant = 'spinner', message }) => {
  if (variant === 'spinner') {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
        {message && <p className="ml-4 text-gray-600">{message}</p>}
      </div>
    );
  }

  if (variant === 'skeleton') {
    return <SkeletonCard />;
  }

  return <div className="text-center p-8 text-gray-600">{message || 'Carregando...'}</div>;
};

export const SkeletonCard = () => (
  <div className="animate-pulse bg-white rounded-lg p-6 shadow">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
);
```

**Dependencies:** None
**Sprint:** Sprint 4

---

### STORY-REM-025: Database Migrations with Alembic
**Debit ID:** DB-013
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Data Engineer

**Description:**
Setup Alembic for database schema versioning and automated migrations, preventing manual SQL errors.

**Acceptance Criteria:**
- [ ] Alembic installed (`pip install alembic`)
- [ ] `alembic init alembic` executed
- [ ] alembic.ini configured (sqlalchemy.url)
- [ ] Initial migration created: `alembic revision --autogenerate -m "initial schema"`
- [ ] Migration applied: `alembic upgrade head`
- [ ] Rollback tested: `alembic downgrade -1`
- [ ] README.md updated with migration commands

**Technical Notes:**
```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Edit alembic.ini
# sqlalchemy.url = sqlite:///consulta_processual.db

# Auto-generate migration from models
alembic revision --autogenerate -m "initial schema"

# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View history
alembic history
```

**alembic/env.py:**
```python
from backend.models import Base  # Import SQLAlchemy Base
target_metadata = Base.metadata
```

**Dependencies:** None
**Sprint:** Sprint 4

---

### STORY-REM-026: Audit Trail for LGPD Compliance
**Debit ID:** DB-005
**Complexity:** 8 pts (M - 3-5 days)
**Priority:** MEDIUM
**Assignee:** Data Engineer

**Description:**
Create audit_log table with SQLAlchemy event listeners to track INSERT/UPDATE/DELETE for LGPD compliance.

**Acceptance Criteria:**
- [ ] audit_log table created (table_name, record_id, action, old_values, new_values, timestamp)
- [ ] SQLAlchemy event listeners for Process and Movement tables
- [ ] Test: INSERT process → audit_log entry created
- [ ] Test: UPDATE process → audit_log with old/new values
- [ ] Test: DELETE process → audit_log with old values
- [ ] Admin endpoint to view audit log (optional)

**Technical Notes:**
```python
# backend/models.py
from sqlalchemy import event
from datetime import datetime

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50))
    record_id = Column(Integer)
    action = Column(String(10))  # INSERT, UPDATE, DELETE
    old_values = Column(JSON)
    new_values = Column(JSON)
    user_id = Column(String)  # Future: from auth system
    timestamp = Column(DateTime, default=datetime.utcnow)

# Event listeners
@event.listens_for(Process, 'after_insert')
def log_process_insert(mapper, connection, target):
    connection.execute(
        AuditLog.__table__.insert(),
        {"table_name": "processes", "record_id": target.id, "action": "INSERT", "new_values": target.to_dict()}
    )

@event.listens_for(Process, 'after_update')
def log_process_update(mapper, connection, target):
    # Use SQLAlchemy history to get old values
    old_values = {k: v[0] for k, v in inspect(target).attrs.items() if v.history.has_changes()}
    connection.execute(
        AuditLog.__table__.insert(),
        {"table_name": "processes", "record_id": target.id, "action": "UPDATE", "old_values": old_values, "new_values": target.to_dict()}
    )
```

**Dependencies:** None
**Sprint:** Sprint 4

---

### STORY-REM-027: Evaluate Authentication Layer
**Debit ID:** SEC-ARCH-003
**Complexity:** 5 pts (M - 2-3 days)
**Priority:** MEDIUM
**Assignee:** Backend Developer

**Description:**
Evaluate need for authentication (JWT, OAuth, etc.) and document decision (yes/no, which approach).

**Acceptance Criteria:**
- [ ] Requirements gathered (public vs private app)
- [ ] Decision documented: YES (implement auth) or NO (defer)
- [ ] If YES: Auth library selected (FastAPI-Users, Authlib, custom JWT)
- [ ] If YES: User model designed (username, email, password_hash)
- [ ] If NO: Rationale documented (e.g., internal tool, VPN-protected)
- [ ] Security implications documented

**Technical Notes:**
```markdown
# Authentication Decision Document

## Requirements
- Application is: [PUBLIC / INTERNAL / HYBRID]
- Expected users: [1-10 / 10-100 / 100+]
- User management needed: [YES / NO]
- Network protection: [VPN / IP whitelist / Public internet]

## Decision: [GO / NO-GO]

**Rationale:**
- If internal tool behind VPN → NO-GO (defer auth)
- If public-facing → GO (implement JWT or OAuth)

## Recommended Approach (if GO):
- FastAPI-Users (batteries-included, JWT + OAuth)
- Supabase Auth (managed service, RLS integration)
- Custom JWT (lightweight, full control)

## Security Implications:
- If NO auth: IP whitelisting + VPN required
- If YES auth: Password hashing (bcrypt), token expiration, refresh tokens
```

**Dependencies:** None
**Sprint:** Sprint 4

---

## Sprint 5+: Polish & Migration (41 Stories)

*(Remaining 41 stories cover: FE-004 chart accessibility, FE-ARCH-002 design system, DB-002 PostgreSQL migration, SEC-ARCH-005 XSS audit, and all MEDIUM/LOW debits. Due to space constraints, abbreviated summaries provided below. Full story details available on request.)*

### STORY-REM-028 to REM-067: Abbreviated Summaries

**Accessibility (5 stories):**
- REM-028: Dashboard chart accessibility (FE-004) — 8 pts
- REM-029: Modal dialog ARIA (FE-002) — 2 pts
- REM-030: Keyboard navigation (FE-003) — 8 pts
- REM-031: Color contrast audit (FE-005) — 3 pts
- REM-032: Semantic HTML improvements (multiple) — 5 pts

**Design System (4 stories):**
- REM-033: Token extraction (FE-ARCH-002) — 5 pts
- REM-034: Atomic components (Shadcn/UI) — 8 pts
- REM-035: Component migration — 8 pts
- REM-036: Storybook setup — 5 pts

**Performance & UX (6 stories):**
- REM-037: Frontend optimization (PERF-003) — 8 pts
- REM-038: Pagination/virtualization (FE-008) — 8 pts
- REM-039: PWA offline support (FE-009) — 8 pts
- REM-040: Form validation library (FE-010) — 8 pts
- REM-041: Analytics/telemetry (FE-011) — 3 pts
- REM-042: Context API migration (FE-007) — 8 pts

**Backend & Operations (8 stories):**
- REM-043: Soft deletes (DB-010) — 3 pts
- REM-044: SearchHistory FK (DB-004) — 3 pts
- REM-045: JSON indexing (DB-008) — 13 pts
- REM-046: Denormalized court cleanup (DB-009) — 3 pts
- REM-047: API versioning strategy (BE-ARCH-005) — 3 pts
- REM-048: Log structure improvement (LOG-ARCH-001/003) — 5 pts
- REM-049: QA automation (QA-ARCH-001) — 13 pts
- REM-050: External API resilience (EXT-ARCH-002/003) — 8 pts

**Security (2 stories):**
- REM-051: XSS vulnerability audit (SEC-ARCH-005) — 8 pts
- REM-052: Input sanitization (related) — 5 pts

**PostgreSQL Migration (IF GO) (5 stories):**
- REM-053: PostgreSQL setup (DB-002 phase 1) — 8 pts
- REM-054: Schema translation (DB-002 phase 2) — 5 pts
- REM-055: Data migration script (DB-002 phase 3) — 13 pts
- REM-056: Application code changes (DB-002 phase 4) — 8 pts
- REM-057: Cutover & monitoring (DB-002 phase 5) — 8 pts

**Remaining LOW Priority (11 stories):**
- REM-058 to REM-067: Various polish items, documentation updates, minor fixes

---

## Epic Metrics

**Total Complexity:** **450-500 story points**
**Total Stories:** **67**
**Estimated Duration:** **14-19 weeks** (parallelizable across team)
**Total Investment:** **R$ 175k**
**Expected ROI:** **150-250%** in 12 months

**Success Criteria:**
- All 9 CRITICAL débitos resolved
- All 16 HIGH débitos resolved or documented waivers
- Test coverage >70% (backend + frontend)
- WCAG 2.1 AA >90%
- Performance: Bulk search <30s (80% faster)
- Monitoring operational (Sentry, health checks)

---

## Appendix: Story Point Reference

- **XS (2 pts):** <1 hour (quick fixes, small changes)
- **S (3-5 pts):** 1 day (straightforward features)
- **M (8 pts):** 3-5 days (moderate complexity)
- **L (13 pts):** 1 week (significant features)
- **XL (21 pts):** 2-3 weeks (complex, multi-part work)

---

**Fase 10: Epic Creation** ✅ COMPLETE
**Criado por:** @pm (Morgan)
**Data:** 2026-02-22
**Status:** Ready for Sprint Planning
**Next Step:** Team assigns stories to sprints, begins Sprint 1 execution
