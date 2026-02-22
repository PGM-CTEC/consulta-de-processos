# STORY-REM-017: Backend Unit Tests (70% Coverage)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** TEST-ARCH-001
**Type:** Testing
**Complexity:** 21 pts (XL - 2-3 weeks)
**Priority:** CRITICAL
**Assignee:** Backend Developer
**Status:** Ready
**Sprint:** Sprint 3

## Description

Create comprehensive backend unit test suite using pytest, achieving 70% line coverage and 60% branch coverage.

## Acceptance Criteria

- [ ] pytest + pytest-cov configured
- [ ] Tests for process_service.py (bulk_search, get_or_update_process)
- [ ] Tests for phase_analyzer.py (classification logic)
- [ ] Tests for API endpoints (search, bulk, health)
- [ ] Tests for database models (Process, Movement)
- [ ] Async tests for async functions (using pytest-asyncio)
- [ ] Coverage report: 70% lines, 60% branches
- [ ] CI pipeline runs tests automatically

## Technical Notes

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

## Dependencies

PERF-ARCH-001 (async tests require async code)

## Definition of Done

- [ ] Code complete and peer-reviewed
- [ ] Unit tests written (if applicable)
- [ ] Acceptance criteria met (all checkboxes ✅)
- [ ] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

_To be updated during development_

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
