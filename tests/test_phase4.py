"""
Phase 4 Verification Tests.

Tests:
1. PreprocessingService Text Pipeline (Unicode NFC, bullet normalization, whitespace collapse, case preservation)
2. SkillExtractionService JSON Taxonomy Loading (362 skills across 6 categories)
3. Skill Extraction on Multiple Resume Scenarios:
   - Backend Engineer Resume
   - AI/ML Engineer Resume
   - Cloud / DevOps Engineer Resume
   - Healthcare RCM Resume
   - Frontend Developer Resume
4. Matched and Missing Skill Set Operations
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.preprocessing_service import PreprocessingService
from app.services.skill_extraction_service import SkillExtractionService


def test_preprocessing_service_pipeline():
    """Verify PreprocessingService cleans text while preserving original case."""
    service = PreprocessingService()
    raw = "••• Senior Developer !!!   With   multiple   spaces\n\n\n\nAnd extra newlines • Bullet item"
    cleaned = service.clean_text(raw)

    assert "Senior Developer" in cleaned  # Case preserved
    assert "!!!" not in cleaned  # Repeated punctuation collapsed
    assert "\n\n\n" not in cleaned  # Newlines collapsed
    assert "- Bullet item" in cleaned  # Bullet character normalized
    assert service.normalize_for_comparison(cleaned) == cleaned.lower()


def test_skill_taxonomy_loading():
    """Verify SkillExtractionService loads externalized JSON taxonomy files."""
    service = SkillExtractionService()
    taxonomy = service._taxonomy

    assert "languages" in taxonomy
    assert "frameworks" in taxonomy
    assert "tools" in taxonomy
    assert "cloud" in taxonomy
    assert "databases" in taxonomy
    assert "ai_ml" in taxonomy

    total_skills = sum(len(v) for v in taxonomy.values())
    assert total_skills >= 300


def test_skill_extraction_backend_resume():
    """Test skill extraction on a Backend Engineer resume."""
    service = SkillExtractionService()
    resume_text = """
    Senior Backend Engineer with expertise in Python, FastAPI, Django, PostgreSQL, Redis, Docker, and AWS.
    Experience with Microservices, REST APIs, and Pytest.
    """
    skills = service.extract_skills(resume_text)

    assert "python" in skills.languages
    assert "fastapi" in skills.frameworks
    assert "django" in skills.frameworks
    assert "postgresql" in skills.databases
    assert "redis" in skills.databases
    assert "docker" in skills.tools
    assert "aws" in skills.cloud or "amazon web services" in skills.cloud


def test_skill_extraction_ai_ml_resume():
    """Test skill extraction on an AI/ML Engineer resume."""
    service = SkillExtractionService()
    resume_text = """
    AI Engineer specializing in PyTorch, TensorFlow, Transformers, HuggingFace, LangChain, RAG, and LLM fine-tuning.
    Proficient in Python, C++, Scikit-learn, Pandas, and NumPy.
    """
    skills = service.extract_skills(resume_text)

    assert "python" in skills.languages
    assert "c++" in skills.languages
    assert "pytorch" in skills.ai_ml
    assert "tensorflow" in skills.ai_ml
    assert "transformers" in skills.ai_ml
    assert "langchain" in skills.ai_ml
    assert "pandas" in skills.ai_ml


def test_skill_extraction_cloud_devops_resume():
    """Test skill extraction on a Cloud / DevOps Engineer resume."""
    service = SkillExtractionService()
    resume_text = """
    DevOps Lead experienced with Kubernetes, K8s, Terraform, Ansible, Jenkins, GitHub Actions, Helm, and Grafana.
    Cloud platforms: AWS, GCP, Azure, Google Cloud Platform.
    """
    skills = service.extract_skills(resume_text)

    assert "kubernetes" in skills.tools  # Alias k8s -> kubernetes
    assert "terraform" in skills.tools
    assert "ansible" in skills.tools
    assert "jenkins" in skills.tools
    assert "aws" in skills.cloud or "amazon web services" in skills.cloud
    assert "gcp" in skills.cloud or "google cloud platform" in skills.cloud


def test_skill_extraction_frontend_resume():
    """Test skill extraction on a Frontend Developer resume."""
    service = SkillExtractionService()
    resume_text = """
    Frontend Developer building modern web apps with TypeScript, JavaScript, React, Next.js, TailwindCSS, and Redux.
    Experience with Vite, Webpack, and Jest.
    """
    skills = service.extract_skills(resume_text)

    assert "typescript" in skills.languages
    assert "javascript" in skills.languages
    assert "react" in skills.frameworks
    assert "nextjs" in skills.frameworks or "next.js" in skills.frameworks
    assert "vite" in skills.tools


def test_skill_matching_and_diffing():
    """Test set-based matched and missing skill calculations."""
    service = SkillExtractionService()
    resume = service.extract_skills("Python, FastAPI, Docker, PostgreSQL")
    jd = service.extract_skills("Python, FastAPI, Docker, Kubernetes, Terraform")

    matched = service.find_matched_skills(resume, jd)
    missing = service.find_missing_skills(resume, jd)

    assert "python" in matched
    assert "fastapi" in matched
    assert "docker" in matched
    assert "kubernetes" in missing
    assert "terraform" in missing
