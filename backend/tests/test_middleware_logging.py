"""Tests for CorrelationIdMiddleware and RequestLoggerMiddleware.

Story: REM-016 — Centralized Logging (Local)
"""

import json
import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.middleware import CorrelationIdMiddleware, RequestLoggerMiddleware
from backend.utils.logger import setup_access_logger


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def app_with_middlewares(tmp_path):
    """Minimal FastAPI app with both middlewares attached."""
    test_access_log = tmp_path / "access.log"

    app = FastAPI()

    # Set up access logger pointing to test file
    import logging
    logger = logging.getLogger("access")
    logger.handlers.clear()
    from logging.handlers import RotatingFileHandler
    from pythonjsonlogger import jsonlogger
    handler = RotatingFileHandler(str(test_access_log), maxBytes=1_000_000, backupCount=1)
    handler.setFormatter(jsonlogger.JsonFormatter("%(timestamp)s %(level)s %(message)s %(path)s %(status_code)s %(correlation_id)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    # Middlewares (add in reverse — Starlette processes outermost last)
    app.add_middleware(RequestLoggerMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/ping")
    def ping():
        return {"pong": True}

    @app.get("/echo-id")
    def echo_id(request):
        return {"id": getattr(request.state, "correlation_id", None)}

    return app, test_access_log


# ---------------------------------------------------------------------------
# CorrelationIdMiddleware tests
# ---------------------------------------------------------------------------

class TestCorrelationIdMiddleware:
    def test_generates_id_when_not_provided(self, app_with_middlewares):
        app, _ = app_with_middlewares
        client = TestClient(app)
        resp = client.get("/ping")
        assert resp.status_code == 200
        req_id = resp.headers.get("X-Request-ID")
        assert req_id is not None
        # Must be a valid UUID4
        uuid.UUID(req_id, version=4)

    def test_reuses_client_id(self, app_with_middlewares):
        app, _ = app_with_middlewares
        client_id = str(uuid.uuid4())
        client = TestClient(app)
        resp = client.get("/ping", headers={"X-Request-ID": client_id})
        assert resp.headers.get("X-Request-ID") == client_id

    def test_different_requests_get_different_ids(self, app_with_middlewares):
        app, _ = app_with_middlewares
        client = TestClient(app)
        id1 = client.get("/ping").headers.get("X-Request-ID")
        id2 = client.get("/ping").headers.get("X-Request-ID")
        assert id1 != id2


# ---------------------------------------------------------------------------
# RequestLoggerMiddleware tests
# ---------------------------------------------------------------------------

class TestRequestLoggerMiddleware:
    def test_logs_request_to_file(self, app_with_middlewares):
        app, log_file = app_with_middlewares
        client = TestClient(app)
        client.get("/ping")

        assert log_file.exists()
        lines = [l for l in log_file.read_text().splitlines() if l.strip()]
        assert len(lines) >= 1
        entry = json.loads(lines[-1])
        assert entry.get("path") == "/ping"

    def test_logs_status_code(self, app_with_middlewares):
        app, log_file = app_with_middlewares
        client = TestClient(app)
        client.get("/ping")

        lines = [l for l in log_file.read_text().splitlines() if l.strip()]
        entry = json.loads(lines[-1])
        assert entry.get("status_code") == 200

    def test_logs_correlation_id(self, app_with_middlewares):
        app, log_file = app_with_middlewares
        req_id = str(uuid.uuid4())
        client = TestClient(app)
        client.get("/ping", headers={"X-Request-ID": req_id})

        lines = [l for l in log_file.read_text().splitlines() if l.strip()]
        entry = json.loads(lines[-1])
        assert entry.get("correlation_id") == req_id

    def test_skips_health_paths(self, app_with_middlewares):
        app, log_file = app_with_middlewares

        @app.get("/health")
        def health():
            return {"ok": True}

        client = TestClient(app)
        # Reset log file
        log_file.write_text("")
        client.get("/health")
        content = log_file.read_text().strip()
        # Health endpoint should NOT produce an access log entry
        assert content == ""
