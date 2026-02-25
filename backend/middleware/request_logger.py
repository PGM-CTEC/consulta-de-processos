"""Request/Response logging middleware.

Story: REM-016 — Centralized Logging (Local)
Logs every HTTP request with method, path, status code, duration, and
correlation ID — equivalent to an access log, but in structured JSON.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..utils.logger import get_logger

logger = get_logger("access")

# Paths to skip (health probes generate too much noise)
_SKIP_PATHS = {"/health", "/ready", "/metrics"}


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that writes one structured log entry per HTTP request.

    Fields logged:
        method        — HTTP verb (GET, POST, …)
        path          — URL path (without query string)
        status_code   — HTTP response status
        duration_ms   — Response time in milliseconds (2 decimal places)
        client_ip     — Remote address
        correlation_id — From CorrelationIdMiddleware (if installed)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip noisy health-check endpoints
        if path in _SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        correlation_id = getattr(request.state, "correlation_id", None)
        client_ip = request.client.host if request.client else "unknown"

        level = "warning" if response.status_code >= 400 else "info"

        getattr(logger, level)(
            f"{request.method} {path} → {response.status_code} ({duration_ms}ms)",
            extra={
                "method": request.method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "correlation_id": correlation_id,
            },
        )

        return response
