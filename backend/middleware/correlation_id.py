"""Correlation ID middleware for request tracing.

Story: REM-016 — Centralized Logging (Local)
Adds a unique X-Request-ID header to every request and response,
enabling end-to-end tracing across logs.
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that attaches a unique correlation ID to each request.

    - If the client sends X-Request-ID, it is reused (allows external tracing).
    - Otherwise a new UUID4 is generated.
    - The ID is stored in request.state.correlation_id for use in handlers/logs.
    - The ID is echoed back in the response header X-Request-ID.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = correlation_id
        return response
