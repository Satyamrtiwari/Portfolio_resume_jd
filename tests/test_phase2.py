"""
Phase 2 Verification Tests.

Tests:
1. Domain Enums (DocumentType, InputSource, StrategyType, PresetType)
2. Domain Dataclasses (SkillSet, CandidateProfile, JDEntity, WeightConfiguration, ParsedDocument)
3. Pydantic Request Models (MatchRequest, ManualWeightsSchema)
4. Pydantic Response Models (MatchResponse, HealthResponse, ATSAnalysisSchema, etc.)
5. Model Serialization and Validation logic
"""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.document import (
    CandidateLinks,
    CandidateProfile,
    DocumentSection,
    DocumentType,
    InputSource,
    JDEntity,
    ParsedDocument,
    PresetType,
    SkillSet,
    StrategyType,
    WeightConfiguration,
)
from app.schemas.request import ManualWeightsSchema, MatchRequest
from app.schemas.response import (
    ATSAnalysisSchema,
    CandidateLinksSchema,
    CandidateProfileSchema,
    ErrorResponse,
    Explainability,
    HealthResponse,
    MatchResponse,
    ModelInfoResponse,
    RecommendationSchema,
    ScoreBreakdown,
    SectionMatch,
    SkillsDetail,
    WeightStrategyDetailSchema,
)


def test_enums():
    """Verify domain enums string values."""
    assert DocumentType.RESUME == "resume"
    assert DocumentType.JOB_DESCRIPTION == "job_description"
    assert InputSource.PDF == "pdf"
    assert InputSource.TEXT == "text"
    assert StrategyType.AUTO == "AUTO"
    assert StrategyType.MANUAL == "MANUAL"
    assert StrategyType.PRESET == "PRESET"
    assert PresetType.BACKEND_ENGINEER == "backend_engineer"
    assert PresetType.AI_ENGINEER == "ai_engineer"


def test_skill_set_domain_model():
    """Verify SkillSet helper methods."""
    skills = SkillSet(
        languages=["python", "sql"],
        frameworks=["fastapi"],
        tools=["docker"],
        cloud=["aws"],
        databases=["postgresql"],
        ai_ml=["pytorch"],
    )
    assert skills.is_empty() is False
    all_s = skills.all_skills()
    assert len(all_s) == 7
    assert "python" in all_s
    assert "fastapi" in all_s

    empty_skills = SkillSet()
    assert empty_skills.is_empty() is True
    assert len(empty_skills.all_skills()) == 0


def test_weight_configuration_domain_model():
    """Verify WeightConfiguration serialization."""
    wc = WeightConfiguration(
        skills=40.0,
        experience=30.0,
        semantic=15.0,
        education=10.0,
        projects=5.0,
        reasoning={"skills": "High skill emphasis"},
    )
    w_dict = wc.to_dict()
    assert w_dict["skills"] == 40.0
    assert w_dict["experience"] == 30.0
    assert sum(w_dict.values()) == 100.0


def test_candidate_profile_domain_model():
    """Verify CandidateProfile data structure."""
    links = CandidateLinks(github="https://github.com/user", linkedin="https://linkedin.com/in/user")
    profile = CandidateProfile(
        name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        location="New York",
        links=links,
        total_years_experience=4.5,
        current_designation="Senior Engineer",
        highest_degree="Bachelor's",
        degree_branch="Computer Science",
    )
    assert profile.name == "John Doe"
    assert profile.links.github == "https://github.com/user"
    assert profile.total_years_experience == 4.5


def test_manual_weights_request_schema():
    """Verify ManualWeightsSchema validation."""
    valid_weights = ManualWeightsSchema(skills=40, experience=30, semantic=15, education=10, projects=5)
    assert valid_weights.skills == 40.0

    with pytest.raises(ValidationError):
        ManualWeightsSchema(skills=-10, experience=30, semantic=15, education=10, projects=5)


from app.schemas.response import ConfidenceSchema, EducationBreakdownSchema, RecruiterSummarySchema


def test_match_response_schema_serialization():
    """Verify full MatchResponse schema creation and JSON export."""
    response = MatchResponse(
        match_score=85.5,
        confidence=ConfidenceSchema(score=92.0, reasons=["Strong match"]),
        match_level="Strong Match",
        recommendation=RecommendationSchema(
            decision="Highly Recommended",
            summary="Strong candidate with good skill fit.",
        ),
        recruiter_summary=RecruiterSummarySchema(
            strengths=["Python"],
            weaknesses=[],
            critical_missing_skills=[],
            overall_recommendation="Highly Recommended",
        ),
        education_breakdown=EducationBreakdownSchema(
            highest_qualification="Bachelor's",
            minimum_required="Bachelor's",
            status="Meets Requirement",
        ),
        weight_strategy=WeightStrategyDetailSchema(
            strategy_used="AUTO",
            preset_applied=None,
            weights={"skills": 40, "experience": 30, "semantic": 15, "education": 10, "projects": 5},
            reasoning={"skills": "Required technical skills emphasis"},
        ),
        scores=ScoreBreakdown(
            overall_score=85.5,
            skill_score=90.0,
            experience_score=80.0,
            education_score=100.0,
            projects_score=85.0,
            semantic_score=82.0,
        ),
        ats_analysis=ATSAnalysisSchema(
            coverage_percentage=85.0,
            total_jd_keywords=10,
            matched_keywords=["python", "fastapi", "docker"],
            missing_keywords=["kubernetes"],
            critical_missing_skills=["kubernetes"],
            optional_missing_skills=[],
        ),
        candidate_profile=CandidateProfileSchema(
            name="Jane Doe",
            email="jane@example.com",
            total_years_experience=5.0,
        ),
        resume_skills=SkillsDetail(languages=["python"]),
        jd_skills=SkillsDetail(languages=["python", "go"]),
        explainability=Explainability(
            matched_skills=["python"],
            missing_skills=["go"],
            experience_alignment="Strong",
            education_alignment="Strong",
            recommendation="Highly Recommended",
            summary="Candidate matches core python skills.",
        ),
        top_matching_sections=[
            SectionMatch(resume_section="Experience", jd_section="Responsibilities", similarity=0.88)
        ],
        resume_length=500,
        jd_length=300,
        processing_time="0.45 sec",
    )

    assert response.match_score == 85.5
    assert response.confidence_score == 92.0
    json_bytes = response.model_dump_json()
    assert "Highly Recommended" in json_bytes
    assert "jane@example.com" in json_bytes
