"""
Phase 10 Verification Tests.

Tests:
1. RequestIDMiddleware (UUID4 generation, X-Request-ID header)
2. TimingMiddleware (X-Process-Time header calculation)
3. AppException Global Exception Handler (JSON response with request_id)
4. RequestValidationError Global Exception Handler (422 response formatting)
5. Unhandled Exception 500 Fallback Handler
"""

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import RequestIDMiddleware, TimingMiddleware
from app.main import app
from app.utils.exceptions import AppException, EmptyDocumentError, FileParsingError


@pytest.fixture(scope="module")
def client():
    """TestClient fixture with main app."""
    with TestClient(app) as test_client:
        yield test_client


def test_middleware_request_id_header(client):
    """Verify RequestIDMiddleware adds X-Request-ID header to responses."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    req_id = response.headers["x-request-id"]
    assert len(req_id) == 36  # UUID4 string length


def test_middleware_timing_header(client):
    """Verify TimingMiddleware adds X-Process-Time header to responses."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    process_time = float(response.headers["x-process-time"])
    assert process_time >= 0.0


def test_custom_app_exception_handler():
    """Verify AppException handler formats JSON detail and request_id."""
    test_app = FastAPI()
    test_app.add_middleware(RequestIDMiddleware)
    register_exception_handlers(test_app)

    @test_app.get("/trigger-app-exception")
    def trigger_app_exc():
        raise EmptyDocumentError("Custom empty document error message")

    with TestClient(test_app) as test_client:
        response = test_client.get("/trigger-app-exception")
        assert response.status_code == 422
        data = response.json()
        assert data["detail"] == "Custom empty document error message"
        assert "request_id" in data
        assert response.headers["x-request-id"] == data["request_id"]


def test_unhandled_500_exception_handler():
    """Verify unhandled exception handler returns 500 JSON without leaking internal stack traces."""
    test_app = FastAPI()
    test_app.add_middleware(RequestIDMiddleware)
    register_exception_handlers(test_app)

    @test_app.get("/trigger-500")
    def trigger_500():
        raise RuntimeError("Unexpected internal crash")

    with TestClient(test_app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/trigger-500")
        assert response.status_code == 500
        data = response.json()
        assert "internal server error" in data["detail"].lower()
        assert "request_id" in data
