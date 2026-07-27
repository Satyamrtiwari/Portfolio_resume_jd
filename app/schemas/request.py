"""
Pydantic v2 request schemas.

Defines parameters for strategy selection, manual weight overrides,
and text/file inputs.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.models.document import PresetType, StrategyType


class ManualWeightsSchema(BaseModel):
    """Custom weight allocations provided by recruiter (must sum to 100 or 1.0)."""

    skills: float = Field(..., ge=0, le=100, description="Skill dimension weight (0-100 or 0-1.0)")
    experience: float = Field(..., ge=0, le=100, description="Experience dimension weight")
    semantic: float = Field(..., ge=0, le=100, description="Semantic dimension weight")
    education: float = Field(..., ge=0, le=100, description="Education dimension weight")
    projects: float = Field(0.0, ge=0, le=100, description="Projects dimension weight")

    @field_validator("skills", mode="before")
    def parse_weights(cls, v: Any) -> float:
        return float(v)


class MatchRequest(BaseModel):
    """
    Schema documenting API parameters for the /match endpoint.
    """

    resume_text: str | None = Field(
        None,
        description="Plain text content of the resume. Provide either this or a PDF file.",
    )
    jd_text: str | None = Field(
        None,
        description="Plain text content of the job description. Provide either this or a PDF file.",
    )
    strategy: StrategyType = Field(
        StrategyType.AUTO,
        description="Weight strategy: AUTO (AI analyzed JD), MANUAL (custom weights), or PRESET.",
    )
    preset_name: PresetType | None = Field(
        None,
        description="Preset configuration name when strategy=PRESET (e.g. backend_engineer, ai_engineer, healthcare_rcm).",
    )
    manual_weights: str | None = Field(
        None,
        description="JSON string of weights when strategy=MANUAL (e.g. '{\"skills\":40, \"experience\":30, \"semantic\":15, \"education\":10, \"projects\":5}').",
    )
