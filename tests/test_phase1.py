"""
Phase 1 Verification Tests.

Tests:
1. Environment Settings Loading
2. Logging Setup
3. FastAPI Application Initialization
4. Health Endpoint GET /api/v1/health
5. Root Endpoint GET /api/v1/
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config.settings import get_settings, Settings
from app.config.logging_config import setup_logging, get_logger
from app.main import app


def test_settings_loading():
    """Verify settings load correctly from .env or defaults."""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.MODEL_NAME == "BAAI/bge-large-en-v1.5"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.PORT == 8000
    assert settings.LOG_LEVEL == "INFO"


def test_logging_setup():
    """Verify logging setup initializes without exceptions."""
    setup_logging()
    logger = get_logger("test_logger")
    assert logger is not None
    logger.info("Phase 1 logging verification test.")


def test_fastapi_app_initialization():
    """Verify FastAPI application instance configuration."""
    assert app.title == "FatPai Resume-JD Semantic Matching API"
    assert app.version == "1.0.0"
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"


def test_root_endpoint():
    """Verify GET /api/v1/ returns 200 OK."""
    with TestClient(app) as client:
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


def test_health_endpoint():
    """Verify GET /api/v1/health returns 200 OK with healthy status and metadata."""
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert data["model_name"] == "BAAI/bge-large-en-v1.5"
        assert data["embedding_dimension"] == 1024
        assert "memory_usage_mb" in data
        assert "cpu_percent" in data
        assert "cache_status" in data
