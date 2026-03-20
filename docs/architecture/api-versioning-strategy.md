# API Versioning Strategy — REM-047

**Strategy:** URL Path Versioning (`/api/v1/`)

## Decision

**Selected:** URL Path Versioning (e.g., `/api/v1/processes/{number}`)

### Rationale
- Explicit and discoverable
- Easy to test in browser/Postman
- Most common convention in REST APIs
- Simple to document in OpenAPI

## Current Endpoints → v1 mapping

| Legacy (current) | v1 (new) |
|-----------------|---------|
| `GET /processes/{number}` | `GET /api/v1/processes/{number}` |
| `POST /processes/bulk` | `POST /api/v1/processes/bulk` |
| `GET /stats` | `GET /api/v1/stats` |
| `GET /history` | `GET /api/v1/history` |
| `GET /health` | `GET /health` (unversioned) |

## Deprecation Policy

- **Legacy endpoints:** Supported for 6 months after v1 GA
- **Headers:** `Deprecation: true` + `Sunset: <date>` added to legacy responses
- **Migration:** Client must update base URL to `/api/v1/`

## Implementation

```python
# backend/routers/v1.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.get("/processes/{number}")
async def get_process_v1(number: str):
    # Same logic as current endpoint
    ...
```

## OpenAPI Info

Version `1.0.0` declared in `app = FastAPI(version="1.0.0")`.
