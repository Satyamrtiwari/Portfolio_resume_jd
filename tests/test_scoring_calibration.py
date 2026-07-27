"""
Scoring Calibration Test Suite.

Verifies mathematical Experience score grounding for freshers (0 YoE)
and continuous Skill Coverage Multiplier calibration.
"""

import pytest
from app.models.document import CandidateProfile, JDEntity, ParsedDocument, SkillSet, DocumentType, InputSource
from app.matchers.experience_matcher import ExperienceMatcher
from app.services.matching_service import MatchingService


@pytest.fixture
def exp_matcher() -> ExperienceMatcher:
    return ExperienceMatcher()


def test_experience_score_zero_yoe_grounding(exp_matcher: ExperienceMatcher):
    """Verify freshers with 0 YoE get 0.0 experience score for experienced roles."""
    profile = CandidateProfile(
        name="Rohit Pawar",
        total_years_experience=0.0,
        company_names=[],
    )
    jd_entity = JDEntity(required_years_experience=5.0)

    resume_doc = ParsedDocument(
        doc_type=DocumentType.RESUME,
        source=InputSource.PDF,
        raw_text="Rohit Pawar\n0 years experience\nEducation: B.A",
        cleaned_text="Rohit Pawar\n0 years experience\nEducation: B.A",
    )
    jd_doc = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION,
        source=InputSource.TEXT,
        raw_text="Senior MLOps Engineer. Required: 5+ years experience.",
        cleaned_text="Senior MLOps Engineer. Required: 5+ years experience.",
    )

    score = exp_matcher.score(
        resume_doc=resume_doc,
        jd_doc=jd_doc,
        candidate_profile=profile,
        jd_entity=jd_entity,
    )
    assert score == 0.0


def test_explainability_zero_yoe(exp_matcher: ExperienceMatcher):
    """Verify explainability message for 0 YoE candidate."""
    profile = CandidateProfile(name="Rohit Pawar", total_years_experience=0.0, company_names=[])
    jd_entity = JDEntity(required_years_experience=5.0)

    resume_doc = ParsedDocument(doc_type=DocumentType.RESUME, source=InputSource.PDF, raw_text="Rohit Pawar", cleaned_text="Rohit Pawar")
    jd_doc = ParsedDocument(doc_type=DocumentType.JOB_DESCRIPTION, source=InputSource.TEXT, raw_text="Senior MLOps", cleaned_text="Senior MLOps")

    explain = exp_matcher.generate_explainability(
        resume_doc=resume_doc,
        jd_doc=jd_doc,
        candidate_profile=profile,
        jd_entity=jd_entity,
        resume_skills=None,
        jd_skills=None,
    )
    assert any("0.0 years" in item or "below requirement" in item for item in explain)
