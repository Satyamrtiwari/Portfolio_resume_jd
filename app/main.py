"""
FastAPI application factory.

Creates and configures the FastAPI application with:
- Lifespan context manager for model loading (load once, serve forever)
- CORS middleware
- Request ID and timing middleware
- Global exception handlers
- API v1 router registration
- Swagger and ReDoc documentation
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import set_matching_service, set_startup_time
from app.api.v1.router import router as v1_router
from app.config.logging_config import setup_logging
from app.config.settings import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import RequestIDMiddleware, TimingMiddleware
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService
from app.services.preprocessing_service import PreprocessingService
from app.services.skill_extraction_service import SkillExtractionService

logger = logging.getLogger(__name__)


# ── Lifespan ────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Application lifespan context manager.

    Startup:
        - Configure logging
        - Load embedding model (ONCE)
        - Initialize all services
        - Set dependency injection references

    Shutdown:
        - Log shutdown message
    """
    # ── Startup ─────────────────────────────────────────────────────
    setup_logging()
    settings = get_settings()

    logger.info("=" * 60)
    logger.info("Starting FatPai Resume-JD Matching API v%s", settings.APP_VERSION)
    logger.info("=" * 60)

    # Record startup time
    startup_time = datetime.now(timezone.utc)
    set_startup_time(startup_time)

    # Initialize services
    logger.info("Initializing services...")

    embedding_service = EmbeddingService()
    preprocessing_service = PreprocessingService()
    skill_extraction_service = SkillExtractionService()

    matching_service = MatchingService(
        embedding_service=embedding_service,
        preprocessing_service=preprocessing_service,
        skill_extraction_service=skill_extraction_service,
    )

    # Set DI references
    set_matching_service(matching_service)

    logger.info("All services initialized successfully.")
    logger.info("API is ready to accept requests.")
    logger.info("=" * 60)

    yield

    # ── Shutdown ────────────────────────────────────────────────────
    logger.info("Shutting down FatPai Resume-JD Matching API...")
    logger.info("Goodbye.")


# ── Application Factory ────────────────────────────────────────────────


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Fully configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="FatPai Resume-JD Semantic Matching API",
        description=(
            "Production-grade AI backend for semantic matching between "
            "resumes and job descriptions. Uses BAAI/bge-large-en-v1.5 "
            "embeddings, section-wise matching, weighted hybrid scoring, "
            "and structured explainability."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware (order matters: outermost first) ──────────────────
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ──────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ─────────────────────────────────────────────────────
    app.include_router(v1_router)

    return app


# ── Application Instance ───────────────────────────────────────────────

app = create_app()
