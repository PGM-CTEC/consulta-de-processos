# Sprint 3 Planning: Testing Foundation
**Weeks 4-5** | **Duration:** 10-15 days | **Team Effort:** 15 days (Backend Dev: 10d, Frontend Dev: 5d)

---

## Sprint Goal
Build regression safety net with comprehensive unit, integration, and E2E tests. Target 70% code coverage on both backend and frontend.

---

## Sprint Scope (5 Tasks)

### 1️⃣ TEST-ARCH-001: Backend Unit & Integration Tests (10-15 days)
**Type:** Testing | **Severity:** CRITICAL
**Impact:** 70% backend test coverage, catch regressions early
**Files:** backend/tests/*.py, backend/requirements.txt

**Current State:**
- Minimal tests exist (database indexed, basic fixtures)
- Most business logic untested
- No integration tests for DataJud API
- ProcessService has complex logic without coverage

**Target Implementation:**
```python
# Test structure
backend/tests/
├── conftest.py              # Pytest fixtures (db, mocks, client)
├── test_process_service.py  # ProcessService business logic
├── test_datajud_client.py   # DataJud API integration
├── test_endpoints.py        # FastAPI endpoint tests
├── test_phase_analyzer.py   # Phase classification logic
├── test_models.py           # Database models validation
├── test_schemas.py          # Request/response schemas
└── test_utils.py            # Utility functions
```

**Acceptance Criteria:**
- [ ] Backend test coverage >70% lines, >60% branches
- [ ] Unit tests for ProcessService methods
- [ ] Integration tests for DataJud client (mocked API)
- [ ] Endpoint tests for /processes/{number}, /processes/bulk, /health, /ready
- [ ] Tests for phase analyzer (15 phase classifications)
- [ ] Database model tests (constraints, relationships)
- [ ] All tests passing with pytest
- [ ] Coverage report generated (pytest-cov)

**Test Categories:**

**A. ProcessService Tests (10+ tests)**
```python
- test_get_or_update_process_new()      # Create new process
- test_get_or_update_process_update()   # Update existing
- test_get_or_update_process_api_error() # Handle DataJud error
- test_get_from_db()                     # Local query
- test_get_bulk_processes_async()        # Async parallel (PERF-ARCH-001)
- test_get_bulk_processes_error_handling() # Individual failures
- test_save_process_data_transaction()   # Transaction handling
- test_parse_datajud_response()          # Response parsing
- test_get_all_instances()               # Multiple instances
```

**B. DataJud Client Tests (8+ tests)**
```python
- test_get_process_success()             # Valid CNJ number
- test_get_process_404()                 # Not found
- test_get_process_auth_error()          # 401
- test_get_process_timeout()             # Timeout (retry logic)
- test_get_process_rate_limit()          # 429 (retry + backoff)
- test_tribunal_alias_resolution()       # CNJ parsing
- test_instance_selection()              # Pick latest instance
```

**C. Endpoint Tests (5+ tests)**
```python
- test_get_process_endpoint()            # GET /processes/{number}
- test_get_bulk_endpoint()               # POST /processes/bulk
- test_health_endpoint()                 # GET /health
- test_ready_endpoint()                  # GET /ready
- test_rate_limiting()                   # 100/min limit
```

**D. Phase Analyzer Tests (5+ tests)**
```python
- test_classify_phase_01()               # G1 civil
- test_classify_phase_PGM_Rio()          # PGM-Rio specific
- test_classify_all_15_phases()          # All classifications
```

**Files to Create/Modify:**
- backend/tests/conftest.py (new - pytest fixtures)
- backend/tests/test_process_service.py (new - ProcessService tests)
- backend/tests/test_datajud_client.py (new - DataJud tests)
- backend/tests/test_endpoints.py (new - endpoint tests)
- backend/tests/test_phase_analyzer.py (new - phase tests)
- backend/tests/test_models.py (new - model tests)
- backend/tests/test_schemas.py (new - schema tests)
- backend/requirements.txt (add pytest-cov, pytest-mock)

**Dependencies:**
- pytest-cov: Coverage reporting
- pytest-mock: Mock fixtures
- pytest-asyncio: Async test support (already installed)
- httpx.AsyncClient for mocking DataJud calls

---

### 2️⃣ FE-006: Frontend Test Setup (2-3 days)
**Type:** Testing | **Severity:** HIGH
**Impact:** 70% frontend test coverage, UI regression prevention
**Files:** frontend/src/**/*.test.js, vitest.config.js

**Current State:**
- Only 1 test file exists (phases.test.js)
- 2% coverage (9 components untested)
- No React Testing Library setup
- No Vitest configuration

**Target Implementation:**
```javascript
// Test structure
frontend/src/
├── components/
│   ├── __tests__/
│   │   ├── ProcessSearch.test.jsx
│   │   ├── BulkSearch.test.jsx
│   │   ├── ProcessDetails.test.jsx
│   │   ├── Dashboard.test.jsx
│   │   ├── Settings.test.jsx
│   │   └── ... (7 components total)
│   └── ...
├── services/
│   └── __tests__/
│       ├── api.test.js
│       └── storage.test.js
└── utils/
    └── __tests__/
        └── helpers.test.js
```

**Acceptance Criteria:**
- [ ] Vitest + React Testing Library configured
- [ ] Coverage >70% lines for all components
- [ ] Component tests (9 components)
- [ ] API service tests
- [ ] Utility function tests
- [ ] All tests passing with `npm test`
- [ ] Coverage report available

**Test Categories:**

**A. Component Tests (9 components)**
```javascript
- ProcessSearch: form input, submit, validation
- BulkSearch: textarea, bulk submit, errors
- ProcessDetails: display data, movements, export
- Dashboard: charts, analytics, data display
- Settings: config input, validation
- SearchHistory: list, clear, pagination
- Phases: phase badge display, colors
- App: routing, component mounting
```

**B. API Service Tests**
```javascript
- getProcess(cnj) - success, 404, error
- getProcessesBulk(numbers) - success, partial failure
- getProcessInstances(cnj) - multiple instances
- testSQLConnection(config) - valid, invalid
- importFromSQL(config) - success, error
```

**C. Utility Tests**
```javascript
- formatDate() - various formats
- parsePhase() - valid phases
- sanitizeInput() - XSS prevention
```

**Files to Create/Modify:**
- vitest.config.js (new - Vitest configuration)
- frontend/vitest.setup.js (new - test environment)
- frontend/src/components/__tests__/*.test.jsx (new - component tests)
- frontend/src/services/__tests__/api.test.js (new - service tests)
- frontend/src/utils/__tests__/helpers.test.js (new - utility tests)
- frontend/package.json (add @testing-library/react, @vitest/ui, happy-dom)
- frontend/.nycrc (new - coverage config)

**Dependencies:**
- vitest: Test runner
- @testing-library/react: Component testing
- @testing-library/jest-dom: DOM matchers
- happy-dom: DOM implementation (faster than jsdom)
- @vitest/ui: Coverage UI

---

### 3️⃣ TEST-ARCH-002: E2E Tests with Playwright (5-7 days)
**Type:** Testing | **Severity:** HIGH
**Impact:** Critical user flows tested end-to-end
**Files:** e2e/**, playwright.config.js

**Current State:**
- No E2E tests
- No Playwright setup

**Target Implementation:**
```javascript
// Test critical flows
e2e/
├── playwright.config.js
├── tests/
│   ├── search-single.spec.js      # Search single process
│   ├── search-bulk.spec.js        # Bulk search (50 items)
│   ├── dashboard.spec.js          # View analytics
│   └── export.spec.js             # Export data (CSV, PDF)
└── fixtures/
    └── test-data.json             # CNJ test numbers
```

**Critical Flows:**

**Flow 1: Single Process Search**
```
1. Load app
2. Enter CNJ number
3. Click search
4. Verify results (process details, movements)
5. Verify health checks working (/health 200)
```

**Flow 2: Bulk Search (50 items)**
```
1. Load app
2. Open bulk search
3. Paste 50 CNJ numbers
4. Click bulk search
5. Verify results <30s (PERF-ARCH-001)
6. Verify partial failures handled
```

**Flow 3: Dashboard & Analytics**
```
1. Load app
2. Navigate to dashboard
3. Verify charts display
4. Check stats aggregation
5. Verify loading states
```

**Acceptance Criteria:**
- [ ] Playwright configured for Chrome, Firefox, Safari
- [ ] 3 critical user flows covered
- [ ] Headless execution for CI
- [ ] Screenshots on failure
- [ ] Load time assertions (health checks <200ms)
- [ ] Performance assertions (bulk <30s)

---

### 4️⃣ BE-ARCH-001: ProcessService Refactor (3-5 days)
**Type:** Code Quality | **Severity:** HIGH
**Impact:** Decoupled architecture, easier testing
**Files:** backend/services/process_service.py, backend/services/datajud.py

**Current State:**
- ProcessService tightly coupled to DataJud
- Hard to test without mocking DataJud
- No dependency injection

**Refactor Goals:**
```python
# Before: Tightly coupled
class ProcessService:
    def __init__(self, db: Session):
        self.client = DataJudClient()  # Hard dependency

# After: Dependency injection
class ProcessService:
    def __init__(self, db: Session, datajud_client: Optional[DataJudClient] = None):
        self.client = datajud_client or DataJudClient()
```

**Benefits:**
- Easy to inject mock DataJud client in tests
- ProcessService fully testable without API calls
- Better separation of concerns

---

### 5️⃣ EXT-ARCH-001: Circuit Breaker Pattern (3-5 days)
**Type:** Resilience | **Severity:** HIGH
**Impact:** Graceful degradation when DataJud unavailable
**Files:** backend/services/circuit_breaker.py, backend/services/datajud.py

**Current State:**
- Direct DataJud calls with retries
- No circuit breaker protection
- Could cause cascading failures

**Target Implementation:**
```python
# Circuit breaker states
class CircuitBreaker:
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open" # Test if recovered

# Usage
@circuit_breaker(failures=5, timeout=60)
async def fetch_datajud(numero):
    return await datajud_client.get_process(numero)
```

**Benefits:**
- Prevent cascading failures
- Fast-fail when service unavailable
- Automatic recovery testing (half-open state)

---

## Test Technology Stack

### Backend Testing:
- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking fixtures
- **pytest-asyncio**: Async test support
- **httpx**: Mock HTTP client

### Frontend Testing:
- **vitest**: Fast unit test runner
- **@testing-library/react**: Component testing
- **@testing-library/jest-dom**: DOM matchers
- **happy-dom**: Light-weight DOM implementation

### E2E Testing:
- **playwright**: Cross-browser E2E testing
- **@playwright/test**: Test runner

---

## Success Metrics

### Backend Coverage:
- `pytest-cov` report: >70% lines, >60% branches
- All ProcessService methods tested
- All DataJud client paths covered
- All endpoints tested

### Frontend Coverage:
- Vitest + @testing-library report: >70% lines
- All 9 components tested
- All critical user interactions tested
- Happy path + error paths

### E2E Coverage:
- 3 critical flows passing
- All flows <5s (except bulk <30s)
- Screenshots on failure captured
- Performance assertions green

### Code Quality:
- All tests passing
- No linter errors
- No console warnings
- Type checking clean

---

## Implementation Order

**Days 1-4:** FE-006 (Frontend test setup - faster)
**Days 2-5:** TEST-ARCH-002 (E2E setup - can run in parallel)
**Days 5-10:** TEST-ARCH-001 (Backend tests - heaviest)
**Days 8-10:** BE-ARCH-001 (Refactor - during backend tests)
**Days 10-12:** EXT-ARCH-001 (Circuit breaker - final)

---

## Sprint Acceptance Criteria

- [ ] Backend test coverage >70% lines, >60% branches (pytest-cov report)
- [ ] Frontend test coverage >70% lines (vitest report)
- [ ] E2E test suite operational (3 critical flows passing)
- [ ] All tests passing (npm test + pytest)
- [ ] CI pipeline green (GitHub Actions)
- [ ] Zero console warnings/errors
- [ ] Type checking clean (no TS errors)

---

**Sprint 3 Plan Created:** 2026-02-22
**Based on:** technical-debt-assessment.md (Phase 8)
**Approval Gate:** Ready for @dev implementation
