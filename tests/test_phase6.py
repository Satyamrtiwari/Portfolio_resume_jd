"""
Phase 6 Verification Tests.

Unit tests every matcher independently:
1. BaseMatcher Cosine Similarity Utility
2. SkillMatcher (Set ratio scoring, matched/missing skill sets)
3. ExperienceMatcher (YoE delta penalty, tech stack & domain overlap, section embeddings)
4. EducationMatcher (Degree tier hierarchy, branch specialization, section embeddings)
5. ProjectsMatcher (Project section presence, tech stack overlap, section embeddings)
6. SemanticMatcher (Full-document cosine similarity, top-N matching section pairs)
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.matchers.base_matcher import BaseMatcher
from app.matchers.education_matcher import EducationMatcher
from app.matchers.experience_matcher import ExperienceMatcher
from app.matchers.projects_matcher import ProjectsMatcher
from app.matchers.semantic_matcher import SemanticMatcher
from app.matchers.skill_matcher import SkillMatcher
from app.models.document import (
    CandidateProfile,
    DocumentSection,
    DocumentType,
    InputSource,
    JDEntity,
    ParsedDocument,
    SkillSet,
)
from app.services.embedding_service import EmbeddingService


@pytest.fixture(scope="module")
def embedding_service():
    return EmbeddingService()


def test_base_matcher_cosine_similarity():
    """Test BaseMatcher cosine similarity calculation."""
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([1.0, 0.0, 0.0])
    vec_c = np.array([0.0, 1.0, 0.0])

    sim_identical = BaseMatcher.compute_cosine_similarity(vec_a, vec_b)
    sim_orthogonal = BaseMatcher.compute_cosine_similarity(vec_a, vec_c)

    assert abs(sim_identical - 1.0) < 1e-4
    assert abs(sim_orthogonal - 0.0) < 1e-4


def test_skill_matcher_independent():
    """Unit test SkillMatcher independently."""
    matcher = SkillMatcher()
    resume_skills = SkillSet(languages=["python"], frameworks=["fastapi"], tools=["docker"])
    jd_skills = SkillSet(languages=["python"], frameworks=["fastapi"], tools=["docker", "kubernetes"])

    score = matcher.score(resume_skills, jd_skills)
    matched = matcher.get_matched_skills(resume_skills, jd_skills)
    missing = matcher.get_missing_skills(resume_skills, jd_skills)

    # 3 matched / 4 required = 75.0%
    assert score == 75.0
    assert "fastapi" in matched
    assert "kubernetes" in missing

    # Edge case: Empty JD skills returns neutral 50.0
    assert matcher.score(resume_skills, SkillSet()) == 50.0


def test_experience_matcher_independent(embedding_service):
    """Unit test ExperienceMatcher (YoE delta, domain, tech overlap)."""
    matcher = ExperienceMatcher()

    # Case 1: Candidate YoE (5.0) >= Required YoE (3.0) -> High score
    prof1 = CandidateProfile(total_years_experience=5.0, current_designation="Senior Backend Engineer")
    jd_ent1 = JDEntity(required_years_experience=3.0, domain_industry="Backend Engineering")

    res_doc1 = ParsedDocument(
        doc_type=DocumentType.RESUME,
        source=InputSource.TEXT,
        raw_text="Experience...",
        cleaned_text="Senior Backend Engineer...",
        sections={"experience": DocumentSection("Experience", "Senior Engineer built APIs")},
    )
    jd_doc1 = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION,
        source=InputSource.TEXT,
        raw_text="Requirements...",
        cleaned_text="Requires 3 years backend experience...",
        sections={"responsibilities": DocumentSection("Responsibilities", "Build APIs")},
    )

    res_doc1.embedding = embedding_service.encode(res_doc1.cleaned_text)
    jd_doc1.embedding = embedding_service.encode(jd_doc1.cleaned_text)
    res_doc1.sections["experience"].embedding = embedding_service.encode(res_doc1.sections["experience"].content)
    jd_doc1.sections["responsibilities"].embedding = embedding_service.encode(jd_doc1.sections["responsibilities"].content)

    score_high = matcher.score(res_doc1, jd_doc1, prof1, jd_ent1)
    assert score_high >= 80.0

    # Case 2: Candidate YoE (1.0) < Required YoE (5.0) -> Penalty applied
    prof2 = CandidateProfile(total_years_experience=1.0)
    jd_ent2 = JDEntity(required_years_experience=5.0)
    score_low = matcher.score(res_doc1, jd_doc1, prof2, jd_ent2)

    assert score_low < score_high


def test_education_matcher_independent(embedding_service):
    """Unit test EducationMatcher (Degree Tier & Branch specialization)."""
    matcher = EducationMatcher()

    # Case 1: Master's in CS vs Bachelor's required -> 100% tier score
    prof_cs = CandidateProfile(highest_degree="Master's", degree_branch="Computer Science")
    jd_cs = JDEntity(required_degree="Bachelor's", required_branch="Computer Science")

    doc_res = ParsedDocument(
        doc_type=DocumentType.RESUME,
        source=InputSource.TEXT,
        raw_text="Edu",
        cleaned_text="Master's in Computer Science",
    )
    doc_jd = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION,
        source=InputSource.TEXT,
        raw_text="Req",
        cleaned_text="Bachelor's degree required",
    )

    doc_res.embedding = embedding_service.encode(doc_res.cleaned_text)
    doc_jd.embedding = embedding_service.encode(doc_jd.cleaned_text)

    score_cs = matcher.score(doc_res, doc_jd, prof_cs, jd_cs)
    assert score_cs >= 85.0

    # Case 2: Associate degree vs Ph.D. required -> lower score
    prof_assoc = CandidateProfile(highest_degree="Associate / Diploma", degree_branch="General")
    jd_phd = JDEntity(required_degree="Ph.D.", required_branch="Computer Science")

    score_assoc = matcher.score(doc_res, doc_jd, prof_assoc, jd_phd)
    assert score_assoc < score_cs


def test_projects_matcher_independent(embedding_service):
    """Unit test ProjectsMatcher independently."""
    matcher = ProjectsMatcher()

    resume_skills = SkillSet(frameworks=["fastapi"], tools=["docker"])
    jd_skills = SkillSet(frameworks=["fastapi"], tools=["docker", "kubernetes"])

    doc_res = ParsedDocument(
        doc_type=DocumentType.RESUME,
        source=InputSource.TEXT,
        raw_text="Projects",
        cleaned_text="Built AI Resume Matcher using FastAPI and Docker",
        sections={"projects": DocumentSection("Projects", "Built AI Resume Matcher using FastAPI and Docker")},
    )
    doc_jd = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION,
        source=InputSource.TEXT,
        raw_text="JD",
        cleaned_text="Backend Developer role using FastAPI",
    )

    doc_res.embedding = embedding_service.encode(doc_res.cleaned_text)
    doc_jd.embedding = embedding_service.encode(doc_jd.cleaned_text)
    doc_res.sections["projects"].embedding = embedding_service.encode(doc_res.sections["projects"].content)

    score_proj = matcher.score(doc_res, doc_jd, resume_skills, jd_skills)
    assert score_proj >= 70.0


def test_semantic_matcher_independent(embedding_service):
    """Unit test SemanticMatcher independently."""
    matcher = SemanticMatcher()

    doc_res = ParsedDocument(
        doc_type=DocumentType.RESUME,
        source=InputSource.TEXT,
        raw_text="Resume",
        cleaned_text="Python Backend Engineer with FastAPI and Docker experience",
        sections={"experience": DocumentSection("Experience", "Built Python microservices with FastAPI")},
    )
    doc_jd = ParsedDocument(
        doc_type=DocumentType.JOB_DESCRIPTION,
        source=InputSource.TEXT,
        raw_text="JD",
        cleaned_text="Seeking Python Backend Developer for FastAPI microservices",
        sections={"responsibilities": DocumentSection("Responsibilities", "Develop Python microservices")},
    )

    doc_res.embedding = embedding_service.encode(doc_res.cleaned_text)
    doc_jd.embedding = embedding_service.encode(doc_jd.cleaned_text)
    doc_res.sections["experience"].embedding = embedding_service.encode(doc_res.sections["experience"].content)
    doc_jd.sections["responsibilities"].embedding = embedding_service.encode(doc_jd.sections["responsibilities"].content)

    score = matcher.score(doc_res, doc_jd)
    top_sections = matcher.find_top_matching_sections(doc_res, doc_jd, top_n=3)

    assert score >= 80.0
    assert len(top_sections) > 0
    assert top_sections[0]["similarity"] > 0.70
