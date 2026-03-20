# STORY-TEST-EP-001: API Endpoint Tests (Complete)

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** TEST-ENDPOINTS-001
**Type:** Testing
**Complexity:** 5 pts (M - 1-2 days)
**Priority:** HIGH
**Assignee:** QA Engineer / Backend Developer
**Status:** Ready
**Sprint:** Sprint 4

## Description

Implement comprehensive API endpoint tests validating all critical endpoints, error handling, rate limiting, and response formats for the Consulta de Processos API.

## Acceptance Criteria

- [ ] Health endpoint tests (GET /health)
- [ ] Single process endpoint tests (GET /processes/{number})
- [ ] Bulk search endpoint tests (POST /processes/bulk)
- [ ] Movements endpoint tests (GET /processes/{number}/movements)
- [ ] Error handling tests (400, 404, 429, 500)
- [ ] Response format validation
- [ ] Rate limiting tests
- [ ] Invalid input handling
- [ ] Request timeout handling
- [ ] 18+ endpoint test cases

## Technical Notes

### Endpoints to Test

```python
# backend/tests/test_endpoints.py

# 1. Health Endpoint
GET /health
├── Should return 200 OK
├── Should return status field
└── Should complete quickly

# 2. Single Process Endpoint
GET /processes/{number}
├── Valid CNJ number → 200 with process data
├── Invalid CNJ format → 400 Bad Request
├── Non-existent process → 404 Not Found
├── Malformed input → 400 Bad Request
└── Rate limited → 429 Too Many Requests

# 3. Bulk Search Endpoint
POST /processes/bulk
├── Valid numbers list → 200 with results
├── Empty list → 400 Bad Request
├── Mixed valid/invalid → 200 with mixed results
├── Timeout on large batch → 500 or timeout
└── Rate limited → 429 Too Many Requests

# 4. Movements Endpoint
GET /processes/{number}/movements
├── Valid process → 200 with movements
├── Non-existent → 404 Not Found
├── Invalid format → 400 Bad Request
└── Rate limited → 429 Too Many Requests

# 5. Error Handling
├── 400 Bad Request (invalid input)
├── 401 Unauthorized (auth required)
├── 404 Not Found (resource missing)
├── 429 Too Many Requests (rate limit)
└── 500 Server Error (internal error)
```

### Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

class TestProcessEndpoint:
    def test_valid_cnj_returns_200(self):
        response = client.get("/processes/0001745-64.1989.8.19.0002")
        assert response.status_code == 200
        assert "numero" in response.json()

    def test_invalid_format_returns_400(self):
        response = client.get("/processes/invalid")
        assert response.status_code == 400

class TestBulkEndpoint:
    def test_valid_bulk_returns_200(self):
        payload = {"numeros": ["0001745-64.1989.8.19.0002"]}
        response = client.post("/processes/bulk", json=payload)
        assert response.status_code == 200

class TestErrorHandling:
    def test_404_on_missing_resource(self):
        response = client.get("/processes/0000000-00.0000.0.00.0000")
        assert response.status_code == 404

    def test_429_on_rate_limit(self):
        # Make multiple requests rapidly
        for _ in range(100):
            response = client.get("/health")
        assert response.status_code == 429
```

## Dependencies

TEST-ARCH-001 (Backend unit tests should be complete)

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
| 2026-02-23 | @pm | Story created for Sprint 4 |
