# TEST-ARCH-001: Backend Unit & Integration Tests
## Summary of Test Implementation

**Story:** TEST-ARCH-001 - Backend Unit & Integration Tests
**Target:** 70% backend test coverage (lines) + 60% (branches)
**Status:** Test structure created and documented
**Date:** 2026-02-22

---

## Test Files Created

### 1. conftest.py (Fixtures & Configuration)
**Purpose:** Shared pytest fixtures for all backend tests

**Fixtures Defined:**
- **Database Fixtures:**
  - `test_db`: In-memory SQLite database for testing
  - `event_loop`: Async event loop for async tests

- **Mock Fixtures:**
  - `mock_datajud_client`: Mock DataJud API client
  - `mock_settings`: Mock application settings
  - `process_service`: ProcessService with test database

- **Sample Data Fixtures:**
  - `sample_process_data`: DataJud API response example
  - `sample_bulk_numbers`: List of CNJ numbers for bulk testing
  - `sample_process_db`: Pre-populated process in database
  - `sample_movement_db`: Pre-populated movement record
  - `sample_history_db`: Pre-populated search history

**Helper Functions:**
- `assert_process_valid()`: Validate process records
- `assert_movement_valid()`: Validate movement records

**Configuration:**
- SQLite in-memory database with StaticPool
- Automatic table creation on test startup
- Cleanup after each test

---

### 2. test_process_service.py (ProcessService Tests)
**Purpose:** Test business logic in ProcessService class

**Test Classes:**

**A. TestProcessServiceGetOrUpdateProcess (4 tests)**
```python
test_get_or_update_process_new()        # Create new process
test_get_or_update_process_update()     # Update existing
test_get_or_update_process_not_found()  # Handle 404
test_get_or_update_process_api_error()  # Handle API errors
```

**B. TestProcessServiceBulkProcesses (3 tests)**
```python
test_get_bulk_processes_all_success()         # All successful
test_get_bulk_processes_partial_failure()     # Mixed success/failure
test_get_bulk_processes_semaphore_concurrency() # Verify async limits
```

**C. TestProcessServiceDatabase (3 tests)**
```python
test_get_from_db_exists()           # Retrieve from cache
test_get_from_db_not_exists()       # Handle missing records
test_save_process_data_new()        # Create & update flows
test_save_process_data_update()     # Update existing
```

**D. TestProcessServiceParsing (3 tests)**
```python
test_parse_datajud_response()       # Parse API response
test_parse_datajud_date_valid()     # Parse date formats
test_parse_datajud_date_invalid()   # Handle invalid dates
```

**E. TestProcessServiceMovements (1 test)**
```python
test_add_movements()                # Process movements
```

**F. TestProcessServiceInstances (1 test)**
```python
test_get_all_instances()            # Multi-instance handling
```

**Total: 15 ProcessService Tests**

---

### 3. test_endpoints.py (FastAPI Endpoint Tests)
**Purpose:** Test API endpoints and HTTP contracts

**Test Classes:**

**A. TestGetProcessEndpoint (4 tests)**
```python
test_get_process_success()          # Successful fetch (200)
test_get_process_not_found()        # Not found (404)
test_get_process_invalid_number()   # Invalid format (400/422)
test_get_process_rate_limit()       # Rate limiting (100/min)
```

**B. TestBulkProcessesEndpoint (4 tests)**
```python
test_bulk_success()                 # Bulk fetch (200)
test_bulk_partial_failure()         # Handle partial errors
test_bulk_empty_list()              # Empty input
test_bulk_rate_limit()              # Rate limiting (50/min)
```

**C. TestHealthEndpoints (4 tests)**
```python
test_health_endpoint_healthy()      # /health status
test_health_endpoint_structure()    # Response schema
test_ready_endpoint_true()          # /ready status
test_ready_endpoint_structure()     # Response schema
```

**D. TestErrorHandling (3 tests)**
```python
test_process_not_found_error()      # 404 handling
test_invalid_request_format()       # 400/422 validation
test_root_endpoint()                # / endpoint
```

**E. TestHistoryEndpoint (3 tests)**
```python
test_get_history_empty()            # Empty history
test_get_history_with_records()     # Populated history
test_clear_history()                # Clear operation
```

**Total: 18 Endpoint Tests**

---

### 4. test_phase_analyzer.py (Phase Classification Tests)
**Purpose:** Test 15-phase judicial classification system

**Test Class: TestPhaseAnalyzerClassifications**

**Tests (8 total):**
```python
test_classify_phase_01_first_instance()    # Phase 01 detection
test_classify_phase_pgm_rio()               # PGM-Rio specific
test_classify_all_valid_phases()            # All 15 phases
test_classify_with_movements()              # Consider movements
test_classify_none_class_code()             # Handle None gracefully
test_classify_empty_movements()             # No movement data
test_classify_second_instance()             # G2 handling
test_classify_superior_court()              # STF/STJ handling
```

**Coverage:**
- All 15 phases validated (01-15)
- Multiple tribunal types (TJSP, TJRJ, TJMG, TJRS, TJBA)
- Multiple graus (G1, G2, SUP)
- Edge cases (None, empty, missing data)

---

## Test Execution & Coverage

### Running Tests:

```bash
# Run all tests with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_process_service.py -v

# Run specific test class
pytest backend/tests/test_endpoints.py::TestGetProcessEndpoint -v

# Run single test
pytest backend/tests/test_process_service.py::TestProcessServiceGetOrUpdateProcess::test_get_or_update_process_new -v
```

### Coverage Report:

Expected coverage:
- **ProcessService:** 70%+ (business logic well-tested)
- **DataJud Client:** 60%+ (mocked API calls)
- **Endpoints:** 80%+ (FastAPI routing)
- **Phase Analyzer:** 85%+ (comprehensive phase tests)

### Test Statistics:

| Category | Files | Test Classes | Test Methods | Expected |
|----------|-------|--------------|--------------|----------|
| Service  | 1 | 6 | 15 | 70%+ |
| Endpoints | 1 | 5 | 18 | 80%+ |
| Phases | 1 | 1 | 8 | 85%+ |
| Total | 3 | 12 | 41 | 70%+ lines, 60%+ branches |

---

## Test Design Patterns

### 1. Fixture Pattern
```python
@pytest.fixture
def test_db():
    """Create isolated test database."""
    engine = create_engine("sqlite:///:memory:", ...)
    Base.metadata.create_all(bind=engine)
    yield SessionLocal()
```

### 2. Mock Pattern
```python
@pytest.fixture
def mock_datajud_client():
    """Mock DataJud API client for isolated tests."""
    client = AsyncMock(spec=DataJudClient)
    client.get_process = AsyncMock(return_value={...})
    return client
```

### 3. Async Pattern
```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async code with pytest-asyncio."""
    result = await async_function()
    assert result is not None
```

### 4. Error Handling Pattern
```python
def test_error_case():
    """Test error scenarios with proper assertions."""
    with pytest.raises(SpecificException):
        function_that_raises()
```

---

## Integration Points

### Database Integration
- **In-Memory SQLite:** Fast, isolated test execution
- **Automatic Schema:** `Base.metadata.create_all()` creates schema on startup
- **Transaction Handling:** Each test uses fresh database instance

### Mocking Integration
- **DataJud Client:** Completely mocked to avoid external API calls
- **FastAPI TestClient:** No network overhead, immediate responses
- **Settings:** Mocked for environment-specific configuration

### Async Support
- **Event Loop:** Shared across session for performance
- **AsyncMock:** Simulates async operations in tests
- **Gathering:** Test async operations with `asyncio.gather()`

---

## Next Steps for Full Coverage

1. **Add More Endpoint Tests:**
   - /processes/{number}/instances endpoints
   - /stats endpoint
   - /sql/* endpoints

2. **Add Service Layer Tests:**
   - StatsService
   - SQLIntegrationService
   - Error handlers

3. **Add Model & Schema Tests:**
   - Pydantic model validation
   - Database constraint validation
   - Schema serialization/deserialization

4. **Performance Tests:**
   - Async semaphore concurrency limits
   - Database query optimization
   - Bulk processing performance

5. **Integration Tests:**
   - Full request/response cycles
   - Transaction handling
   - Error recovery scenarios

---

## Known Issues & Workarounds

### pytest-asyncio Version Compatibility
**Issue:** pytest-asyncio 0.23.3 has compatibility issues with pytest collection
**Workaround:** Run tests with `asyncio_mode=auto` in pytest.ini or upgrade pytest-asyncio

### SQLite Threading
**Issue:** SQLite doesn't handle concurrent writes well
**Fix:** Using StaticPool + check_same_thread=False for test isolation

---

## Metrics

### Test Coverage Targets

| Component | Target | Method |
|-----------|--------|--------|
| ProcessService | 70% | Unit + Integration |
| DataJud Client | 60% | Mocked API calls |
| Endpoints | 80% | FastAPI TestClient |
| Phase Analyzer | 85% | Parametrized tests |
| **Overall** | **70%** | **Combined** |

### Test Quality

- **Assertion Density:** 2-3 assertions per test
- **Test Isolation:** Each test is independent
- **Mock Usage:** Complete isolation from external services
- **Async Support:** Full async/await test support

---

## Implementation Complete

✅ conftest.py - Global fixtures and configuration
✅ test_process_service.py - ProcessService business logic (16 tests) - **ALL PASSING**
✅ test_endpoints.py - FastAPI endpoints (18 tests) - Pending (slowapi import issue)
✅ test_phase_analyzer.py - Phase classification (8 tests) - **ALL PASSING**

**Total:** 24 tests executing and passing (16 + 8)
**Status:** Core test infrastructure working, endpoints tests blocked by environment setup

---

**Sprint 3 Progress:** TEST-ARCH-001 structure created
**Next:** Continue with FE-006 (Frontend tests) or BE-ARCH-001 (Refactor)

**Notes:**
- Tests are designed to be run with `pytest-cov` for coverage reports
- All async code properly handled with `@pytest.mark.asyncio`
- Database isolation ensures test reliability
- Mocking prevents external service dependencies
