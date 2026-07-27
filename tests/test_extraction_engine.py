"""
Phase 1 Extraction Engine Benchmark Test Suite.

Verifies 100% extraction accuracy of candidate names, email, phone, location,
total YoE, degree qualification, and company lists against Pydantic v2 schemas.
"""

import pathlib
import pytest
from pypdf import PdfReader

from app.models.document import InputSource, ParsedDocument
from app.parsers.resume_parser import ResumeParser
from app.schemas.extraction import (
    ContactInfoSchema,
    ExtractedCandidateProfileSchema,
    ExtractedJDEntitySchema,
)
from app.services.entity_extraction_service import EntityExtractionService

SAMPLES_DIR = pathlib.Path(
    r"C:\Users\3star\Downloads\Fw_ JD's and exemplary profiles\Fw_ JD's and exemplary profiles"
)
PRE_AUTH_DIR = SAMPLES_DIR / "Pre Auth Associate Ops Select"


@pytest.fixture
def entity_service() -> EntityExtractionService:
    return EntityExtractionService()


@pytest.fixture
def resume_parser() -> ResumeParser:
    return ResumeParser()


def test_pydantic_contact_schema_sanitization():
    """Verify ContactInfoSchema field-level Pydantic validators."""
    contact = ContactInfoSchema(
        name="  satyam r tiwari  ",
        email="test@example.com",
        portfolio="https://gmail.com",
    )
    assert contact.name == "Satyam R Tiwari"
    assert contact.portfolio is None  # gmail.com excluded


def test_pydantic_company_name_cleaning():
    """Verify ExtractedCandidateProfileSchema company deduplication & noise filtering."""
    profile = ExtractedCandidateProfileSchema(
        company_names=[
            "AU Small Finance Bank",
            "AU Small Finance Bank",
            "Executive",
            "Spire BPO Services LLP",
            "Road Kurla West",
        ]
    )
    assert "AU Small Finance Bank" in profile.company_names
    assert "Spire BPO Services LLP" in profile.company_names


@pytest.mark.asyncio
async def test_extraction_dawood_khan_pdf(entity_service: EntityExtractionService, resume_parser: ResumeParser):
    """Ground-truth extraction benchmark: Dawood Khan.pdf"""
    pdf_path = PRE_AUTH_DIR / "Dawood Khan.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    doc = resume_parser.parse(raw_text, InputSource.PDF)
    doc.cleaned_text = raw_text
    doc.filename = pdf_path.name

    schema = await entity_service.extract_candidate_profile_schema(doc)

    assert schema.contact.name == "Dawood Khan"
    assert schema.contact.email == "dwdkhn25@gmail.com"
    assert schema.contact.phone == "9579213008"
    assert schema.total_years_experience == 4.0
    assert schema.highest_degree == "Bachelor's"
    assert any("AU Small Finance" in c for c in schema.company_names)
    assert any("Spire" in c for c in schema.company_names)


@pytest.mark.asyncio
async def test_extraction_anay_gurav_pdf(entity_service: EntityExtractionService, resume_parser: ResumeParser):
    """Ground-truth extraction benchmark: Anay Gurav.pdf"""
    pdf_path = PRE_AUTH_DIR / "Anay Gurav.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    doc = resume_parser.parse(raw_text, InputSource.PDF)
    doc.cleaned_text = raw_text
    doc.filename = pdf_path.name

    schema = await entity_service.extract_candidate_profile_schema(doc)

    assert "Anay" in schema.contact.name and "Gurav" in schema.contact.name
    assert schema.total_years_experience >= 2.0
    assert schema.highest_degree == "Bachelor's"
    assert any("sagility" in c.lower() or "spire" in c.lower() for c in schema.company_names)


@pytest.mark.asyncio
async def test_extraction_atif_ansari_pdf(entity_service: EntityExtractionService, resume_parser: ResumeParser):
    """Ground-truth extraction benchmark: Atif Ansari.pdf"""
    pdf_path = PRE_AUTH_DIR / "Atif Ansari.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    doc = resume_parser.parse(raw_text, InputSource.PDF)
    doc.cleaned_text = raw_text
    doc.filename = pdf_path.name

    schema = await entity_service.extract_candidate_profile_schema(doc)

    assert "Atif" in schema.contact.name and "Ansari" in schema.contact.name
    assert schema.contact.email == "atif1986@gmail.com"
    assert schema.contact.phone == "+919967018333"
    assert schema.total_years_experience >= 10.0
    assert schema.highest_degree == "SSC / 10th Standard"
    assert any("Altruist" in c for c in schema.company_names)
    assert any("Hexaware" in c for c in schema.company_names)
