"""
Domain models for document processing.

Defines enums and dataclasses that represent the core domain objects
flowing through the parsing, preprocessing, entity extraction, and matching pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np


# ── Enums ───────────────────────────────────────────────────────────────


class DocumentType(StrEnum):
    """Type of document being processed."""

    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"


class InputSource(StrEnum):
    """How the document was provided to the API."""

    PDF = "pdf"
    TEXT = "text"


class StrategyType(StrEnum):
    """Weight strategy selection."""

    AUTO = "AUTO"
    MANUAL = "MANUAL"
    PRESET = "PRESET"


class PresetType(StrEnum):
    """Industry role presets for weight configuration."""

    AI_ENGINEER = "ai_engineer"
    BACKEND_ENGINEER = "backend_engineer"
    FRONTEND_ENGINEER = "frontend_engineer"
    DATA_SCIENTIST = "data_scientist"
    HEALTHCARE_RCM = "healthcare_rcm"
    FINANCE = "finance"
    SALES = "sales"
    HR = "hr"
    GENERAL_SOFTWARE_ENGINEER = "general_software_engineer"
    CUSTOM = "custom"


# ── Data Structures ────────────────────────────────────────────────────


@dataclass
class CandidateLinks:
    """Links extracted from candidate resume."""

    github: str | None = None
    linkedin: str | None = None
    portfolio: str | None = None


@dataclass
class CandidateProfile:
    """Structured entities extracted from candidate resume."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: CandidateLinks = field(default_factory=CandidateLinks)
    total_years_experience: float = 0.0
    current_designation: str | None = None
    highest_degree: str | None = None
    degree_branch: str | None = None
    company_names: list[str] = field(default_factory=list)


@dataclass
class JDEntity:
    """Structured requirements extracted from job description."""

    required_years_experience: float = 0.0
    required_degree: str | None = None
    required_branch: str | None = None
    domain_industry: str | None = None
    mandatory_skills: set[str] = field(default_factory=set)
    preferred_skills: set[str] = field(default_factory=set)


@dataclass
class DocumentSection:
    """
    A single named section extracted from a document.

    Attributes:
        name: Section heading (e.g., 'Skills', 'Experience', 'Required Skills').
        content: Cleaned text content of this section.
        embedding: Embedding vector, populated during the matching pipeline.
    """

    name: str
    content: str
    embedding: np.ndarray | None = None


@dataclass
class ParsedDocument:
    """
    Structured output from the parser layer.

    Represents a fully parsed and section-aware document ready for
    the matching pipeline.

    Attributes:
        doc_type: Whether this is a resume or job description.
        source: How the document was provided (pdf or text).
        raw_text: Original unprocessed text.
        cleaned_text: Text after preprocessing pipeline.
        sections: Named sections extracted from the document.
        word_count: Total word count of the cleaned text.
        embedding: Full-document embedding vector, populated later.
        candidate_profile: Extracted candidate entities (if resume).
        jd_entity: Extracted job requirements (if JD).
    """

    doc_type: DocumentType
    source: InputSource
    raw_text: str
    cleaned_text: str
    sections: dict[str, DocumentSection] = field(default_factory=dict)
    word_count: int = 0
    embedding: np.ndarray | None = None
    candidate_profile: CandidateProfile | None = None
    jd_entity: JDEntity | None = None
    filename: str | None = None


@dataclass
class SkillSet:
    """
    Categorized skills extracted from a document.

    Each category is a list of normalized skill names.
    Provides helper methods for set operations (matching, diffing).
    """

    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    cloud: list[str] = field(default_factory=list)
    databases: list[str] = field(default_factory=list)
    ai_ml: list[str] = field(default_factory=list)

    def all_skills(self) -> set[str]:
        """Return a flattened set of all skills across all categories."""
        return set(
            self.languages
            + self.frameworks
            + self.tools
            + self.cloud
            + self.databases
            + self.ai_ml
        )

    def is_empty(self) -> bool:
        """Return True if no skills were extracted."""
        return len(self.all_skills()) == 0


@dataclass
class WeightConfiguration:
    """Active weight allocation across dynamic scoring dimensions (0-100 scale)."""

    skills: float = 40.0
    experience: float = 30.0
    semantic: float = 15.0
    education: float = 10.0
    projects: float = 5.0
    reasoning: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, float]:
        return {
            "skills": round(self.skills, 2),
            "experience": round(self.experience, 2),
            "semantic": round(self.semantic, 2),
            "education": round(self.education, 2),
            "projects": round(self.projects, 2),
        }
