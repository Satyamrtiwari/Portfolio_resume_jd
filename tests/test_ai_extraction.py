"""
AI Structured Extraction Test Suite.

Verifies OpenRouter / Groq / OpenAI Pydantic AI Extraction Service
and local fallback mechanism.
"""

import pytest
from app.models.document import DocumentType, InputSource, ParsedDocument
from app.parsers.resume_parser import ResumeParser
from app.schemas.extraction import ExtractedCandidateProfileSchema, ExtractedJDEntitySchema
from app.services.ai_extraction_service import AIExtractionService
from app.services.entity_extraction_service import EntityExtractionService


@pytest.fixture
def ai_service() -> AIExtractionService:
    return AIExtractionService()


@pytest.fixture
def entity_service() -> EntityExtractionService:
    return EntityExtractionService()


def test_ai_extraction_service_availability(ai_service: AIExtractionService):
    """Verify AI extraction service availability check."""
    # is_available should return a boolean
    assert isinstance(ai_service.is_available, bool)


def test_ai_extraction_clean_json_str():
    """Verify markdown code block removal from LLM response strings."""
    raw_response = "```json\n{\"contact\": {\"name\": \"Rayyan Anwar Shaikh\"}}\n```"
    cleaned = AIExtractionService._clean_json_str(raw_response)
    assert cleaned == '{"contact": {"name": "Rayyan Anwar Shaikh"}}'


@pytest.mark.asyncio
async def test_ai_extraction_resume_text(ai_service: AIExtractionService):
    """Test AI structured extraction on Rayyan Anwar Shaikh resume text."""
    if not ai_service.is_available:
        pytest.skip("No AI API key configured in .env")

    resume_text = """
    RESUME
    Rayyan Anwar Shaikh
    Shaikhrayyan7021@gmail.com
    Contact No.7021816041
    CAREER OBJECTIVES
    seeking a responsible position enabling me to my talent, skill and experience.
    EDUCATIONAL QUALIFICATIOM
    SSC (Maharashtra State Board)
    HSC (Maharashtra State Board)
    Other Qualification: Basic Computer Knowledge, Ms-Word
    """
    schema = await ai_service.extract_candidate_profile(resume_text)
    assert schema is not None
    assert isinstance(schema, ExtractedCandidateProfileSchema)
    assert "Rayyan" in schema.contact.name
    assert schema.contact.email == "Shaikhrayyan7021@gmail.com"


@pytest.mark.asyncio
async def test_hybrid_fallback_mechanism(entity_service: EntityExtractionService):
    """Verify local fallback mechanism works when doc text is processed."""
    doc = ParsedDocument(
        doc_type=DocumentType.RESUME,
        source=InputSource.PDF,
        raw_text="Rayyan Anwar Shaikh\nShaikhrayyan7021@gmail.com\n7021816041",
        cleaned_text="Rayyan Anwar Shaikh\nShaikhrayyan7021@gmail.com\n7021816041",
        filename="Rayyan Resum 2.pdf",
    )
    schema = await entity_service.extract_candidate_profile_schema(doc)
    assert schema is not None
    assert "Rayyan" in schema.contact.name
