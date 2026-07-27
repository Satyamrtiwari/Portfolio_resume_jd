"""
API v1 router (v3 ATS Platform).

Registered Endpoints:
    GET  /api/v1/          — Simple health check
    GET  /api/v1/health    — Detailed health with CPU, Memory, Model status, Uptime
    GET  /api/v1/model     — Model metadata
    POST /api/v1/match     — Main matching endpoint with strategy & preset support
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import psutil
from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.dependencies import get_matching_service, get_startup_time
from app.config.settings import get_settings
from app.models.document import PresetType, StrategyType
from app.schemas.response import (
    ErrorResponse,
    HealthResponse,
    MatchResponse,
    ModelInfoResponse,
)
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["v1"])


# ── Health Check ────────────────────────────────────────────────────────


@router.get(
    "/",
    summary="Simple Health Check",
    description="Returns a minimal health status.",
)
async def root() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok", "message": "FatPai Resume-JD Matching API is running."}


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Detailed Health Check",
    description="Returns detailed health information including CPU, Memory, Model status, and Uptime.",
)
async def health(
    matching_service: MatchingService = Depends(get_matching_service),
    startup_time: datetime = Depends(get_startup_time),
) -> HealthResponse:
    """Detailed health check with system metrics and model status."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    uptime = now - startup_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    embedding_service = matching_service._embedding
    process = psutil.Process()
    mem_info = process.memory_info()
    memory_mb = round(mem_info.rss / (1024 * 1024), 2)
    cpu_pct = psutil.cpu_percent(interval=None)

    return HealthResponse(
        status="healthy",
        model_loaded=embedding_service.is_loaded,
        model_name=embedding_service.model_name,
        embedding_dimension=embedding_service.embedding_dimension,
        model_size="1.34 GB",
        device=embedding_service.device,
        uptime=f"{hours}h {minutes}m {seconds}s",
        version=settings.APP_VERSION,
        memory_usage_mb=memory_mb,
        cpu_percent=cpu_pct,
        cache_status="active - 362 taxonomy skills & model cached",
    )


# ── Model Info ──────────────────────────────────────────────────────────


@router.get(
    "/model",
    response_model=ModelInfoResponse,
    summary="Model Information",
    description="Returns metadata about the loaded embedding model.",
)
async def model_info(
    embedding_service: EmbeddingService = Depends(
        lambda: get_matching_service()._embedding  # noqa: E501
    ),
) -> ModelInfoResponse:
    """Return model name, dimension, device, and load time."""
    info = embedding_service.get_model_info()
    return ModelInfoResponse(**info)


# ── Match Endpoint ──────────────────────────────────────────────────────


@router.post(
    "/match",
    response_model=MatchResponse,
    summary="Match Resume to Job Description",
    description=(
        "Accepts a resume and job description (PDF upload or plain text) "
        "along with weight strategy options (AUTO, MANUAL, PRESET) and returns "
        "a comprehensive ATS match analysis, entity extraction, confidence score, "
        "and hiring decision recommendation."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input / Manual weights error"},
        413: {"model": ErrorResponse, "description": "File too large"},
        415: {"model": ErrorResponse, "description": "Unsupported file type"},
        422: {"model": ErrorResponse, "description": "Empty document"},
        503: {"model": ErrorResponse, "description": "Model not loaded"},
    },
)
async def match(
    resume_file: UploadFile | None = File(None, description="Resume PDF file"),
    jd_file: UploadFile | None = File(None, description="Job Description PDF file"),
    resume_text: str | None = Form(None, description="Resume as plain text"),
    jd_text: str | None = Form(None, description="Job Description as plain text"),
    strategy: StrategyType = Form(StrategyType.AUTO, description="Weight strategy: AUTO, MANUAL, or PRESET"),
    preset_name: PresetType | None = Form(None, description="Role preset name if strategy=PRESET (e.g. backend_engineer, ai_engineer, healthcare_rcm)"),
    manual_weights: str | None = Form(None, description="JSON string of custom weights if strategy=MANUAL (e.g. '{\"skills\":40, \"experience\":30, \"semantic\":15, \"education\":10, \"projects\":5}')"),
    matching_service: MatchingService = Depends(get_matching_service),
) -> MatchResponse:
    """
    Match a resume against a job description with dynamic weight strategy support.
    """
    logger.info("Match request received (strategy=%s).", strategy)

    result = await matching_service.match(
        resume_file=resume_file,
        resume_text=resume_text,
        jd_file=jd_file,
        jd_text=jd_text,
        strategy=strategy,
        preset_name=preset_name,
        manual_weights_json=manual_weights,
    )

    return result
