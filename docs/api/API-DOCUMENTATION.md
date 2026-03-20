# Consulta Processo API Documentation

**OpenAPI 3.0** documentation for the Consulta Processo API.

---

## Quick Start

### Interactive API Explorer
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI Schema:** `/openapi.json`

---

## Base Information

**Base URL:** `http://localhost:8000` (development) or your deployment URL
**API Version:** See `/health` endpoint
**Content-Type:** `application/json`
**Rate Limit:** 100 requests/minute per IP

---

## Endpoints Overview

### Health & Status

#### GET /health
Check API health and database connectivity.

**Response:** 200 OK
```json
{
  "status": "healthy",
  "service": "Consulta Processual API",
  "database": "connected",
  "environment": "production",
  "version": "1.0.0"
}
```

---

### Process Queries

#### GET /processes/{number}
Retrieve a single legal process by CNJ number.

**Parameters:**
- `number` (string, required): CNJ process number (e.g., `0001745-64.1989.8.19.0002`)

**Response:** 200 OK
```json
{
  "id": 1,
  "number": "0001745-64.1989.8.19.0002",
  "tribunal_name": "TJRJ",
  "phase": "01",
  "subject": "Direito Civil",
  "judge": "Juiz Nome",
  "distribution_date": "1989-12-31T00:00:00",
  "last_update": "2026-02-23T10:00:00",
  "movements": []
}
```

**Errors:**
- `404 Not Found`: Process not found in DataJud
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: DataJud API unavailable

**Rate Limit:** 100 requests/minute

---

#### POST /processes/bulk
Query multiple processes in a single request.

**Request Body:**
```json
{
  "numbers": [
    "0001745-64.1989.8.19.0002",
    "0001234-12.2020.8.19.0001"
  ]
}
```

**Response:** 200 OK
```json
{
  "results": [
    {
      "number": "0001745-64.1989.8.19.0002",
      "tribunal_name": "TJRJ",
      "phase": "01"
    }
  ],
  "failures": [
    {
      "number": "0001234-12.2020.8.19.0001",
      "error": "Not found"
    }
  ]
}
```

**Parameters:**
- `numbers` (array of strings): CNJ process numbers
- `max_concurrent` (optional, integer): Maximum concurrent requests (default: 10)

**Rate Limit:** 10 requests/minute

---

#### GET /processes/{number}/movements
Get all movements (updates) for a process.

**Parameters:**
- `number` (string, required): CNJ process number

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "date": "2026-02-23T10:00:00",
    "description": "Sentença prolatada",
    "code": "00150"
  }
]
```

---

### Performance Monitoring

#### GET /metrics
Get real-time performance metrics.

**Query Parameters:**
- `hours` (integer, optional): Historical data span in hours (default: 24)

**Response:** 200 OK
```json
{
  "current": {
    "timestamp": "2026-02-23T10:00:00",
    "latency_p50": 250.5,
    "latency_p95": 1500.2,
    "latency_p99": 3500.8,
    "throughput": 45.3,
    "error_rate": 0.5,
    "db_query_time": 85.2,
    "cache_hit_ratio": 78.5
  },
  "history": [],
  "alerts": []
}
```

**Metrics Explained:**
- `latency_p50`: Median response time (50th percentile) in milliseconds
- `latency_p95`: 95th percentile response time
- `latency_p99`: 99th percentile response time
- `throughput`: Requests per second
- `error_rate`: Percentage of failed requests
- `db_query_time`: Average database query duration
- `cache_hit_ratio`: Percentage of cache hits

---

#### GET /metrics/alerts
Get recent performance alerts.

**Query Parameters:**
- `limit` (integer, optional): Maximum alerts to return (default: 20)

**Response:** 200 OK
```json
[
  {
    "type": "LATENCY_HIGH",
    "message": "P99 latency 5500ms exceeds threshold 5000ms",
    "severity": "warning",
    "timestamp": "2026-02-23T10:00:00"
  }
]
```

---

### Database Statistics

#### GET /stats
Get database statistics and analytics.

**Response:** 200 OK
```json
{
  "total_processes": 15234,
  "total_searches": 45890,
  "phases_distribution": {
    "01": 5234,
    "02": 4123
  },
  "last_update": "2026-02-23T10:00:00"
}
```

---

### Search History

#### GET /history
Retrieve search history.

**Query Parameters:**
- `limit` (integer, optional): Maximum records (default: 50)

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "number": "0001745-64.1989.8.19.0002",
    "created_at": "2026-02-23T10:00:00"
  }
]
```

---

#### DELETE /history
Clear all search history.

**Response:** 200 OK
```json
{
  "message": "Histórico limpo"
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message explaining what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid CNJ number |
| 404 | Not Found | Process not in DataJud |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Database/API failure |
| 503 | Service Unavailable | DataJud API down |

---

## Authentication & Security

### Rate Limiting
- **Default:** 100 requests/minute per IP
- **Bulk Endpoint:** 10 requests/minute per IP

### Security Features
- CORS enabled for configured origins
- Rate limiting with slowapi
- Input validation on all endpoints
- SQL injection protection with SQLAlchemy
- Error messages sanitized (no sensitive data)

### Headers
```
Content-Type: application/json
CORS-Allow-Origin: *
```

---

## Examples

### Example 1: Get Single Process
```bash
curl -X GET \
  "http://localhost:8000/processes/0001745-64.1989.8.19.0002" \
  -H "Content-Type: application/json"
```

### Example 2: Bulk Search
```bash
curl -X POST \
  "http://localhost:8000/processes/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "numbers": [
      "0001745-64.1989.8.19.0002",
      "0001234-12.2020.8.19.0001"
    ]
  }'
```

### Example 3: Get Metrics
```bash
curl -X GET \
  "http://localhost:8000/metrics?hours=24" \
  -H "Content-Type: application/json"
```

### Example 4: Get Performance Alerts
```bash
curl -X GET \
  "http://localhost:8000/metrics/alerts?limit=10" \
  -H "Content-Type: application/json"
```

---

## Response Times

Typical response times (p50):

| Endpoint | Time |
|----------|------|
| /health | <50ms |
| /metrics | <100ms |
| /stats | <150ms |
| /processes/{number} | <500ms |
| /processes/bulk (10 items) | <5s |
| /history | <200ms |

---

## Development

### Run API Server
```bash
cd backend
python -m uvicorn main:app --reload
```

### View OpenAPI Schema
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- JSON: http://localhost:8000/openapi.json

### Testing
```bash
# Run backend tests
pytest

# Check specific endpoint
curl http://localhost:8000/health
```

---

## Support

For issues or questions:
1. Check this documentation
2. Review OpenAPI schema in Swagger UI
3. Check application logs
4. Review GitHub issues

---

**Last Updated:** 2026-02-23
**API Version:** 1.0.0
**Status:** ✅ Production Ready
