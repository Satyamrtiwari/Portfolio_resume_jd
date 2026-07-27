"""
Phase 3 Verification Tests.

Tests:
1. BaseDocumentParser PDF and Upload Handling
2. ResumeParser Section Detection & Parsing
3. JDParser Section Detection & Parsing
4. EntityExtractionService (Candidate Profile & JD Entities)
"""

import io
import sys
from pathlib import Path

import pytest
from pypdf import PdfWriter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.document import DocumentType, InputSource
from app.parsers.base_parser import BaseDocumentParser
from app.parsers.jd_parser import JDParser
from app.parsers.resume_parser import ResumeParser
from app.services.entity_extraction_service import EntityExtractionService
from app.utils.exceptions import EmptyDocumentError, FileParsingError, UnsupportedFileTypeError


def create_sample_pdf_bytes(text_content: str) -> bytes:
    """Helper to generate a valid PDF byte stream in memory for testing."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    # pypdf doesn't easily write text into blank pages without drawing annotations or page streams,
    # so we mock or test PDF text extraction using pypdf reader on a valid PDF structure.
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_base_parser_pdf_extraction_empty():
    """Verify BaseDocumentParser throws EmptyDocumentError on empty/blank PDF."""
    parser = BaseDocumentParser()
    pdf_bytes = create_sample_pdf_bytes("Blank")
    with pytest.raises(EmptyDocumentError):
        parser.extract_text_from_pdf(pdf_bytes)


def test_base_parser_invalid_pdf_bytes():
    """Verify BaseDocumentParser throws FileParsingError on corrupted PDF bytes."""
    parser = BaseDocumentParser()
    corrupt_bytes = b"NOT_A_PDF_STREAM_CORRUPT"
    with pytest.raises(FileParsingError):
        parser.extract_text_from_pdf(corrupt_bytes)


def test_resume_parser_sections():
    """Verify ResumeParser identifies standard resume section headings."""
    sample_resume = """
    Jane Doe
    jane.doe@example.com | San Francisco, CA

    Technical Skills
    - Languages: Python, JavaScript
    - Frameworks: FastAPI, React

    Professional Experience
    Senior Engineer at TechCorp (2020 - Present)
    - Developed backend microservices using FastAPI and PostgreSQL.

    Education
    B.S. in Computer Science — Stanford University (2016 - 2020)

    Projects
    - AI Resume Matcher: Semantic search backend using sentence-transformers.
    """

    parser = ResumeParser()
    doc = parser.parse(sample_resume, source=InputSource.TEXT)

    assert doc.doc_type == DocumentType.RESUME
    assert doc.source == InputSource.TEXT
    assert "skills" in doc.sections
    assert "experience" in doc.sections
    assert "education" in doc.sections
    assert "projects" in doc.sections
    assert "Python" in doc.sections["skills"].content
    assert "TechCorp" in doc.sections["experience"].content
    assert "Stanford" in doc.sections["education"].content


def test_resume_parser_fallback_general():
    """Verify ResumeParser falls back to 'general' section if no headings match."""
    unstructured_text = "Just a plain paragraph describing someone without any bold section headings."
    parser = ResumeParser()
    doc = parser.parse(unstructured_text, source=InputSource.TEXT)

    assert "general" in doc.sections
    assert doc.sections["general"].content == unstructured_text


def test_jd_parser_sections():
    """Verify JDParser identifies JD section headings."""
    sample_jd = """
    Senior Software Engineer — Backend

    Role Overview
    We are seeking a Senior Software Engineer to lead backend development.

    Requirements
    - 5+ years of experience in Python and distributed systems.
    - Experience with FastAPI, PostgreSQL, Docker, AWS.

    Preferred Qualifications
    - Master's degree in Computer Science or related field.
    - Experience with Kubernetes and Terraform.
    """

    parser = JDParser()
    doc = parser.parse(sample_jd, source=InputSource.TEXT)

    assert doc.doc_type == DocumentType.JOB_DESCRIPTION
    assert "responsibilities" in doc.sections or "required_skills" in doc.sections
    assert "preferred_skills" in doc.sections or "qualifications" in doc.sections


@pytest.mark.asyncio
async def test_entity_extraction_service():
    """Verify EntityExtractionService extracts candidate profile entities and JD requirements."""
    extractor = EntityExtractionService()
    resume_parser = ResumeParser()
    jd_parser = JDParser()

    sample_resume = """
    Alice Smith
    alice.smith@gmail.com | (555) 123-4567 | Seattle, WA
    GitHub: github.com/alicesmith | LinkedIn: linkedin.com/in/alicesmith

    Senior Backend Developer — Current Role
    5+ years of experience building Python web services.

    Work History
    Software Engineer (2019 - Present)
    Building microservices using FastAPI and AWS.

    Education
    Master's in Computer Science, University of Washington
    """

    sample_jd = """
    Healthcare RCM Senior Developer
    Requires minimum 3 years of experience in Healthcare RCM medical billing.
    Requires Bachelor's in Computer Science.
    """

    r_doc = resume_parser.parse(sample_resume, source=InputSource.TEXT)
    j_doc = jd_parser.parse(sample_jd, source=InputSource.TEXT)

    profile = await extractor.extract_candidate_profile(r_doc)
    jd_entity = await extractor.extract_jd_entity(j_doc)

    assert profile.name == "Alice Smith"
    assert profile.email == "alice.smith@gmail.com"
    assert profile.links.github is not None
    assert "github.com/alicesmith" in profile.links.github
    assert profile.total_years_experience == 5.0
    assert profile.highest_degree == "Master's"
    assert profile.degree_branch == "Computer Science"

    assert jd_entity.required_years_experience == 3.0
    assert jd_entity.domain_industry == "Healthcare RCM"
    assert jd_entity.required_degree == "Bachelor's"
