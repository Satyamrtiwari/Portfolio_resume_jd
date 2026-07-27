"""
Phase 7 Verification Tests.

Tests:
1. WeightStrategyService — AUTO Strategy Analysis & Reasoning
2. WeightStrategyService — MANUAL Strategy Validation & Error Handling
3. WeightStrategyService — PRESET Strategy Resolution (backend_engineer, healthcare_rcm, etc.)
4. ATSService — Coverage % calculation and Critical vs Optional skill split
5. RecommendationService — Decision rules (Highly Recommended, Recommended, Needs Review, Reject)
6. ConfidenceService — Reliability calculation based on length, entity fidelity, score variance
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.document import (
    CandidateProfile,
    DocumentSection,
    DocumentType,
    InputSource,
    JDEntity,
    ParsedDocument,
    PresetType,
    SkillSet,
    StrategyType,
)
from app.schemas.response import ATSAnalysisSchema, ScoreBreakdown
from app.services.ats_service import ATSService
from app.services.confidence_service import ConfidenceService
from app.services.recommendation_service import RecommendationService
from app.services.skill_extraction_service import SkillExtractionService
from app.services.weight_strategy_service import WeightStrategyService
from app.utils.exceptions import AppException


def test_weight_strategy_auto():
    """Test AUTO strategy dynamic JD analysis and reasoning generation."""
    service = WeightStrategyService()

    # 1. Senior Role JD requiring 5+ YoE
    jd_doc = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION,
        source=InputSource.TEXT,
        raw_text="Requires 5+ years experience in Python backend development.",
        cleaned_text="Requires 5+ years experience in Python backend development.",
    )
    jd_entity = JDEntity(required_years_experience=5.0)

    weights, strat, preset = service.resolve_weights(
        strategy=StrategyType.AUTO,
        jd_doc=jd_doc,
        jd_entity=jd_entity,
    )

    assert strat == "AUTO"
    assert preset is None
    assert weights.experience >= 35.0  # Increased experience weight for senior role
    assert "skills" in weights.reasoning
    assert "experience" in weights.reasoning
    assert "5.0+" in weights.reasoning["experience"]

    # 2. Healthcare RCM Role JD
    jd_rcm = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION,
        source=InputSource.TEXT,
        raw_text="Healthcare RCM specialist required for medical billing.",
        cleaned_text="Healthcare RCM specialist required for medical billing.",
    )
    jd_entity_rcm = JDEntity(domain_industry="Healthcare RCM")

    weights_rcm, _, _ = service.resolve_weights(
        strategy=StrategyType.AUTO,
        jd_doc=jd_rcm,
        jd_entity=jd_entity_rcm,
    )
    assert weights_rcm.skills == 45.0
    assert weights_rcm.experience == 35.0
    assert "Healthcare RCM" in weights_rcm.reasoning["skills"]


def test_weight_strategy_manual():
    """Test MANUAL strategy validation logic and error handling."""
    service = WeightStrategyService()

    # 1. Valid manual weights (0-100 scale)
    valid_json = json.dumps({"skills": 40, "experience": 30, "semantic": 15, "education": 10, "projects": 5})
    weights, strat, _ = service.resolve_weights(strategy=StrategyType.MANUAL, manual_weights_json=valid_json)
    assert strat == "MANUAL"
    assert weights.skills == 40.0
    assert weights.experience == 30.0

    # 2. Valid manual weights (0-1.0 scale auto-conversion)
    valid_dec = json.dumps({"skills": 0.40, "experience": 0.30, "semantic": 0.15, "education": 0.10, "projects": 0.05})
    weights_dec, _, _ = service.resolve_weights(strategy=StrategyType.MANUAL, manual_weights_json=valid_dec)
    assert weights_dec.skills == 40.0

    # 3. Invalid manual weights sum != 100
    invalid_sum = json.dumps({"skills": 50, "experience": 50, "semantic": 50, "education": 10, "projects": 0})
    with pytest.raises(AppException) as exc_info:
        service.resolve_weights(strategy=StrategyType.MANUAL, manual_weights_json=invalid_sum)
    assert exc_info.value.status_code == 400
    assert "must sum to 100%" in exc_info.value.detail

    # 4. Invalid negative weights
    invalid_neg = json.dumps({"skills": -10, "experience": 60, "semantic": 30, "education": 20, "projects": 0})
    with pytest.raises(AppException) as exc_info2:
        service.resolve_weights(strategy=StrategyType.MANUAL, manual_weights_json=invalid_neg)
    assert exc_info2.value.status_code == 400


def test_weight_strategy_preset():
    """Test PRESET strategy loading and applied preset reasoning."""
    service = WeightStrategyService()

    weights, strat, preset_applied = service.resolve_weights(
        strategy=StrategyType.PRESET,
        preset_name=PresetType.BACKEND_ENGINEER,
    )
    assert strat == "PRESET"
    assert preset_applied == "backend_engineer"
    assert weights.skills == 45.0
    assert weights.experience == 30.0
    assert "skills" in weights.reasoning

    # Test AI Engineer preset
    weights_ai, _, preset_ai = service.resolve_weights(
        strategy=StrategyType.PRESET,
        preset_name=PresetType.AI_ENGINEER,
    )
    assert preset_ai == "ai_engineer"
    assert weights_ai.projects == 10.0


def test_ats_service_coverage():
    """Test ATSService coverage calculation and critical missing skill classification."""
    skill_extractor = SkillExtractionService()
    ats_service = ATSService(skill_extractor)

    resume_skills = SkillSet(languages=["python"], frameworks=["fastapi"], tools=["docker"])
    jd_skills = SkillSet(languages=["python"], frameworks=["fastapi"], tools=["docker", "kubernetes", "terraform"])

    jd_doc = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION,
        source=InputSource.TEXT,
        raw_text="Requirements...",
        cleaned_text="Requirements...",
        sections={
            "required_skills": DocumentSection("Required Skills", "Must have Python, FastAPI, Docker, Kubernetes."),
            "preferred_skills": DocumentSection("Preferred Skills", "Nice to have Terraform."),
        },
    )

    ats_res = ats_service.analyze_coverage(resume_skills, jd_skills, jd_doc)

    assert ats_res.total_jd_keywords == 5
    assert len(ats_res.matched_keywords) == 3
    assert abs(ats_res.coverage_percentage - 60.0) < 1e-2
    assert "kubernetes" in ats_res.critical_missing_skills
    assert "terraform" in ats_res.optional_missing_skills


def test_recommendation_service():
    """Test RecommendationService decision thresholds and executive summaries."""
    rec_service = RecommendationService()

    # Case 1: High Score (88%) -> Highly Recommended
    scores_high = ScoreBreakdown(
        overall_score=88.0, skill_score=90.0, experience_score=85.0,
        education_score=100.0, projects_score=80.0, semantic_score=82.0
    )
    ats_clean = ATSAnalysisSchema(
        coverage_percentage=90.0, total_jd_keywords=10, matched_keywords=["a"],
        missing_keywords=[], critical_missing_skills=[], optional_missing_skills=[]
    )
    rec1 = rec_service.generate_recommendation(scores_high, ats_clean, candidate_yoe=5.0, required_yoe=3.0)
    assert rec1.decision == "Highly Recommended"
    assert "exceptional match" in rec1.summary

    # Case 2: Score 60% -> Needs Review
    scores_mid = ScoreBreakdown(
        overall_score=60.0, skill_score=60.0, experience_score=60.0,
        education_score=70.0, projects_score=50.0, semantic_score=60.0
    )
    rec2 = rec_service.generate_recommendation(scores_mid, ats_clean)
    assert rec2.decision == "Needs Review"


def test_confidence_service():
    """Test ConfidenceService reliability score logic."""
    conf_service = ConfidenceService()

    res_doc = ParsedDocument(
        doc_type=DocumentType.RESUME, source=InputSource.TEXT,
        raw_text="...", cleaned_text="...", word_count=400
    )
    jd_doc = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION, source=InputSource.TEXT,
        raw_text="...", cleaned_text="...", word_count=250
    )
    profile = CandidateProfile(name="Jane", email="jane@example.com", total_years_experience=5.0, highest_degree="Master's")

    scores_consistent = ScoreBreakdown(
        overall_score=80.0, skill_score=82.0, experience_score=78.0,
        education_score=80.0, projects_score=80.0, semantic_score=80.0
    )

    conf = conf_service.calculate_confidence(res_doc, jd_doc, profile, scores_consistent)
    assert conf.score >= 85.0
