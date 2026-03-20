# STORY-REM-017: Backend Unit Tests - Implementation Plan

**Story:** REM-017 - Backend Unit Tests (70% Coverage)
**Complexity:** 21 pts (XL - 2-3 weeks)
**Priority:** CRITICAL
**Sprint:** Sprint 3

---

## Objective

Create comprehensive backend unit test suite achieving:
- **70% line coverage**
- **60% branch coverage**
- All critical functions tested
- Async functions properly tested

---

## Test Coverage Target

### 1. ProcessService (process_service.py) - PRIORITY 1
**Current coverage:** ~30%
**Target:** 80%

Tests needed:
- [x] `get_or_update_process()` - Happy path + error cases
- [x] `_save_process_data()` - Data parsing
- [x] `_parse_datajud_response()` - Field extraction
- [x] `get_bulk_processes()` - Async bulk processing
- [x] `get_process_instance()` - Instance selection
- [x] `_add_movements()` - Movement parsing

### 2. DataJudClient (datajud.py) - PRIORITY 2
**Current coverage:** ~20%
**Target:** 70%

Tests needed:
- [x] `_get_tribunal_alias()` - CNJ number parsing
- [x] `_search_index()` - Async API calls + retry logic
- [x] `_search_aliases()` - Parallel searches
- [x] `get_process()` - Full process fetch
- [x] `get_process_instances()` - Multi-instance handling

### 3. PhaseAnalyzer (phase_analyzer.py) - PRIORITY 3
**Current coverage:** ~40%
**Target:** 75%

Tests needed:
- [x] `analyze()` - Phase classification logic
- [x] `_classify_by_movements()` - Movement-based classification
- [x] All classification rules (G1, G2, G1R, G2R, STJ, STF)

### 4. API Endpoints (main.py) - PRIORITY 4
**Current coverage:** ~10%
**Target:** 60%

Tests needed:
- [x] `GET /health` - Health check
- [x] `GET /ready` - Readiness probe
- [x] `POST /processes/bulk` - Bulk search endpoint
- [x] Rate limiting verification

### 5. Database Models (models.py) - PRIORITY 5
**Current coverage:** ~50%
**Target:** 85%

Tests needed:
- [x] `Process` model constraints
- [x] `Movement` model relationships
- [x] Cascade deletes
- [x] Unique constraints

---

## Test Structure

```
backend/tests/
├── test_process_service.py          (NEW - 25 tests)
├── test_datajud_client.py           (NEW - 18 tests)
├── test_phase_analyzer.py           (NEW - 20 tests)
├── test_api_endpoints.py            (NEW - 12 tests)
├── test_models.py                   (NEW - 10 tests)
├── conftest.py                      (fixtures - UPDATED)
└── fixtures/
    ├── sample_datajud_responses.py  (test data)
    └── mock_data.py                 (mocks)
```

---

## Implementation Order

### Phase 1: Setup & Fixtures (Day 1)
- [x] Configure pytest.ini (remove asyncio conflicts)
- [x] Create conftest.py with shared fixtures
- [x] Create fixture files (sample data, mocks)
- [x] Setup coverage reporting

**Files:**
- `backend/tests/conftest.py` (NEW)
- `backend/tests/fixtures/sample_datajud_responses.py` (NEW)
- `backend/tests/fixtures/mock_data.py` (NEW)

### Phase 2: ProcessService Tests (Days 2-3)
- [x] Happy path tests
- [x] Error handling tests
- [x] Async bulk processing tests
- [x] Data transformation tests

**File:** `backend/tests/test_process_service.py` (NEW - 25 tests)

### Phase 3: DataJudClient Tests (Days 4-5)
- [x] CNJ parsing tests
- [x] API call tests (with mocks)
- [x] Retry logic tests
- [x] Multi-instance tests

**File:** `backend/tests/test_datajud_client.py` (NEW - 18 tests)

### Phase 4: PhaseAnalyzer Tests (Days 6)
- [x] Classification logic tests
- [x] All phase types (G1, G2, G1R, G2R, STJ, STF)
- [x] Edge cases (missing data, unusual patterns)

**File:** `backend/tests/test_phase_analyzer.py` (NEW - 20 tests)

### Phase 5: API Endpoints Tests (Day 7)
- [x] Health endpoint tests
- [x] Readiness endpoint tests
- [x] Rate limiting tests
- [x] Error handling tests

**File:** `backend/tests/test_api_endpoints.py` (NEW - 12 tests)

### Phase 6: Model Tests (Day 8)
- [x] Model creation tests
- [x] Constraint tests
- [x] Relationship tests

**File:** `backend/tests/test_models.py` (NEW - 10 tests)

### Phase 7: Coverage Analysis & Refinement (Days 9-10)
- [x] Generate coverage report
- [x] Identify gaps
- [x] Add missing tests
- [x] Achieve 70% lines / 60% branches

**Command:** `pytest --cov=backend --cov-report=html`

---

## Test Statistics Target

| Module | Lines | Branches | Target |
|--------|-------|----------|--------|
| process_service.py | 150 | 45 | 80% / 70% |
| datajud.py | 200 | 60 | 70% / 60% |
| phase_analyzer.py | 180 | 55 | 75% / 65% |
| main.py | 100 | 30 | 60% / 50% |
| models.py | 50 | 10 | 85% / 80% |
| **TOTAL** | **680** | **200** | **70% / 60%** |

---

## Testing Patterns

### Unit Test Pattern
```python
def test_function_behavior():
    # Arrange
    input_data = {"key": "value"}
    expected_output = "result"

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

### Async Test Pattern
```python
import asyncio

def test_async_function():
    async def run_test():
        result = await async_function()
        assert result == expected

    asyncio.run(run_test())
```

### Mock Pattern
```python
from unittest.mock import patch, AsyncMock

def test_with_mock():
    with patch('module.external_service') as mock_service:
        mock_service.return_value = {"data": "mocked"}
        result = function_that_uses_service()
        assert result == expected
```

### Fixture Pattern
```python
@pytest.fixture
def mock_process():
    return models.Process(
        number="0000001-01.0000.1.00.0001",
        tribunal_name="TJSP",
        phase="G1"
    )

def test_with_fixture(mock_process):
    assert mock_process.number == "0000001-01.0000.1.00.0001"
```

---

## Coverage Report Target

```
Name                          Stmts   Miss  Cover   Branch  BrPart  Cover
────────────────────────────────────────────────────────────────────────
backend/services/__init__.py      0      0   100%      0      0   100%
backend/services/datajud.py     200     60    70%     60     15    75%
backend/services/phase_analyzer   180     45    75%     55     10    82%
backend/services/process_service  150     30    80%     45      8    82%
backend/main.py                  100     40    60%     30     10    67%
backend/models.py                 50      8    85%     10      2    80%
────────────────────────────────────────────────────────────────────────
TOTAL                            680    183    73%    200     45    78%
```

---

## Acceptance Criteria Mapping

- [ ] **pytest + pytest-cov configured** → Phase 1
- [ ] **Tests for process_service.py** → Phase 2 (25 tests)
- [ ] **Tests for phase_analyzer.py** → Phase 4 (20 tests)
- [ ] **Tests for API endpoints** → Phase 5 (12 tests)
- [ ] **Tests for database models** → Phase 6 (10 tests)
- [ ] **Async tests using pytest-asyncio** → All phases (asyncio.run pattern)
- [ ] **Coverage report: 70% lines, 60% branches** → Phase 7
- [ ] **CI pipeline runs tests automatically** → Integration (separate task)

---

## Files to Create/Modify

### New Files
1. `backend/tests/test_process_service.py` (25 tests)
2. `backend/tests/test_datajud_client.py` (18 tests)
3. `backend/tests/test_phase_analyzer.py` (20 tests)
4. `backend/tests/test_api_endpoints.py` (12 tests)
5. `backend/tests/test_models.py` (10 tests)
6. `backend/tests/fixtures/sample_datajud_responses.py` (test data)
7. `backend/tests/fixtures/mock_data.py` (fixtures)

### Modified Files
1. `backend/tests/conftest.py` (add shared fixtures)
2. `pytest.ini` (ensure no asyncio conflicts)
3. `pyproject.toml` (pytest configuration)

---

## Success Criteria

✅ **Coverage Targets:**
- [ ] 70% line coverage (overall)
- [ ] 60% branch coverage (overall)
- [ ] 80%+ coverage for critical modules (ProcessService, DataJudClient)

✅ **Test Quality:**
- [ ] All tests pass (0 failures)
- [ ] All tests independent (no shared state)
- [ ] Clear test names describing behavior
- [ ] Proper mocking (no external API calls)

✅ **Maintainability:**
- [ ] Reusable fixtures in conftest.py
- [ ] Well-organized test file structure
- [ ] Documentation for complex test scenarios
- [ ] Easy to add new tests

---

## Timeline

| Phase | Duration | Goal |
|-------|----------|------|
| 1. Setup | 1 day | Pytest configured + fixtures ready |
| 2. ProcessService | 2 days | 25 tests, 80% coverage |
| 3. DataJudClient | 2 days | 18 tests, 70% coverage |
| 4. PhaseAnalyzer | 1 day | 20 tests, 75% coverage |
| 5. API Endpoints | 1 day | 12 tests, 60% coverage |
| 6. Models | 1 day | 10 tests, 85% coverage |
| 7. Analysis & Polish | 2 days | Final coverage report, gap filling |
| **TOTAL** | **10 days** | **70% / 60% coverage achieved** |

---

## Next Steps

1. **Today:** Read Phase 1 (setup & fixtures)
2. **Tomorrow:** Implement ProcessService tests (Phase 2)
3. **Day 3+:** Follow phases sequentially
4. **Week 2:** Coverage analysis & refinement
5. **Completion:** Update STORY-REM-017 with results

---

**Plan Status:** READY FOR IMPLEMENTATION
**Start Date:** 2026-02-23
**Target Completion:** 2026-03-05 (10 business days)
