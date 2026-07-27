"""
Phase 8 Verification Tests.

Integration tests the complete matching pipeline end-to-end:
Resume / JD
↓
Parser & Preprocessing
↓
Entity Extraction
↓
Weight Strategy Resolution (AUTO / MANUAL / PRESET)
↓
Skill Extraction & ATS Keyword Analysis
↓
Vector Embeddings (BAAI/bge-large-en-v1.5)
↓
Multi-Dimensional Matchers (Skill, Experience, Education, Projects, Semantic)
↓
Weighted Composite Scoring
↓
Confidence & Hiring Recommendation Engine
↓
Structured MatchResponse Output
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.document import PresetType, StrategyType
from app.schemas.response import MatchResponse
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService
from app.services.preprocessing_service import PreprocessingService
from app.services.skill_extraction_service import SkillExtractionService


@pytest.fixture(scope="module")
def matching_service():
    """Module-scoped matching service with pre-loaded embedding model."""
    embedding_service = EmbeddingService()
    preprocessing_service = PreprocessingService()
    skill_extraction_service = SkillExtractionService()

    return MatchingService(
        embedding_service=embedding_service,
        preprocessing_service=preprocessing_service,
        skill_extraction_service=skill_extraction_service,
    )


@pytest.mark.asyncio
async def test_pipeline_integration_auto_strategy(matching_service):
    """Integration test full pipeline using AUTO strategy on a Senior Backend Engineer profile."""
    resume_text = """
    Jane Doe
    jane.doe@example.com | +1-555-0199 | San Francisco, CA
    GitHub: https://github.com/janedoe | LinkedIn: https://linkedin.com/in/janedoe

    Professional Summary:
    Senior Backend Engineer with 5 years of experience building high-throughput microservices using Python, FastAPI, Django, PostgreSQL, Docker, AWS, and Redis.

    Technical Skills:
    - Languages: Python, SQL, Bash
    - Frameworks: FastAPI, Django, React
    - DevOps & Tools: Docker, Git, Pytest
    - Cloud & DB: AWS, S3, EC2, PostgreSQL, Redis

    Experience:
    Senior Software Engineer — TechCorp (2021 - Present)
    - Designed scalable FastAPI backend APIs handling 5M daily requests.
    - Containerized microservices using Docker and deployed on AWS EC2.
    - Optimized PostgreSQL query performance reducing latency by 40%.

    Education:
    Bachelor of Science in Computer Science — University of California (2016 - 2020)
    """

    jd_text = """
    Job Description: Senior Backend Developer
    We are looking for a Senior Backend Developer with minimum 3+ years of experience.

    Requirements:
    - 3+ years of hands-on experience in Python backend development.
    - Strong expertise in FastAPI or Django.
    - Experience with Docker, Kubernetes, and cloud infrastructure (AWS/GCP).
    - Database proficiency in PostgreSQL and Redis.
    - Bachelor's degree in Computer Science or related STEM field.
    """

    response = await matching_service.match(
        resume_text=resume_text,
        jd_text=jd_text,
        strategy=StrategyType.AUTO,
    )

    assert isinstance(response, MatchResponse)
    assert response.match_score > 70.0
    assert response.confidence_score > 50.0
    assert response.weight_strategy.strategy_used == "AUTO"
    assert response.weight_strategy.weights["skills"] == 35.0
    assert response.weight_strategy.weights["experience"] == 35.0
    assert response.candidate_profile.name == "Jane Doe"
    assert response.candidate_profile.total_years_experience == 5.0
    assert response.candidate_profile.highest_degree == "Bachelor's"
    assert response.ats_analysis.coverage_percentage > 70.0
    assert "python" in response.ats_analysis.matched_keywords
    assert response.recommendation.decision in ("Highly Recommended", "Recommended", "Needs Review")


@pytest.mark.asyncio
async def test_pipeline_integration_preset_strategy(matching_service):
    """Integration test full pipeline using PRESET strategy (backend_engineer)."""
    resume_text = "Python Backend Engineer with FastAPI, PostgreSQL, Docker, AWS."
    jd_text = "Senior Backend Engineer required: Python, FastAPI, Docker, Kubernetes."

    response = await matching_service.match(
        resume_text=resume_text,
        jd_text=jd_text,
        strategy=StrategyType.PRESET,
        preset_name=PresetType.BACKEND_ENGINEER,
    )

    assert response.weight_strategy.strategy_used == "PRESET"
    assert response.weight_strategy.preset_applied == "backend_engineer"
    assert response.weight_strategy.weights["skills"] == 45.0
    assert response.weight_strategy.weights["experience"] == 30.0
    assert response.scores.skill_score > 0.0


@pytest.mark.asyncio
async def test_pipeline_integration_manual_strategy(matching_service):
    """Integration test full pipeline using MANUAL strategy with recruiter weight overrides."""
    resume_text = "Python Developer with FastAPI, PostgreSQL, Docker."
    jd_text = "Python Backend Developer required with FastAPI, Docker, Kubernetes."
    manual_json = json.dumps({"skills": 50, "experience": 25, "semantic": 15, "education": 10, "projects": 0})

    response = await matching_service.match(
        resume_text=resume_text,
        jd_text=jd_text,
        strategy=StrategyType.MANUAL,
        manual_weights_json=manual_json,
    )

    assert response.weight_strategy.strategy_used == "MANUAL"
    assert response.weight_strategy.weights["skills"] == 50.0
    assert response.weight_strategy.weights["experience"] == 25.0
    assert response.weight_strategy.weights["projects"] == 0.0
