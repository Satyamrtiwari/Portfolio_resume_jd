"""
Resume parser.

Detects resume-specific sections (Skills, Experience, Projects,
Education, Certifications) from raw text using heading pattern matching.
Returns a structured ParsedDocument with named sections.
"""

from __future__ import annotations

import logging
import re

from app.models.document import (
    DocumentSection,
    DocumentType,
    InputSource,
    ParsedDocument,
)
from app.parsers.base_parser import BaseDocumentParser

logger = logging.getLogger(__name__)

# ── Section heading patterns (case-insensitive) ─────────────────────────

_RESUME_SECTION_PATTERNS: dict[str, re.Pattern[str]] = {
    "skills": re.compile(
        r"^(?:technical\s+)?skills|core\s+competencies|"
        r"technical\s+proficiency|areas?\s+of\s+expertise|"
        r"competencies|proficiencies",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^(?:work\s+)?experience|professional\s+experience|"
        r"employment\s+history|work\s+history|career\s+history",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"^projects?|key\s+projects?|personal\s+projects?|"
        r"selected\s+projects?|notable\s+projects?",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"^education|academic\s+background|academic\s+qualifications|"
        r"educational\s+background|degrees?",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"^certifications?|licenses?\s*(?:&|and)?\s*certifications?|"
        r"professional\s+certifications?|accreditations?",
        re.IGNORECASE,
    ),
}


class ResumeParser(BaseDocumentParser):
    """
    Parser specialized for resume documents.

    Detects common resume section headings and splits the document
    into structured sections for downstream matching.
    """

    def parse(
        self,
        text: str,
        source: InputSource,
    ) -> ParsedDocument:
        """
        Parse raw resume text into a structured document.

        Args:
            text: Raw text content of the resume.
            source: How the text was provided (PDF or plaintext).

        Returns:
            A ParsedDocument with detected sections.
        """
        sections = self._detect_sections(text)

        if not sections:
            logger.info("No section headings detected; using full document as 'general'.")
            sections["general"] = DocumentSection(
                name="General",
                content=text.strip(),
            )

        word_count = len(text.split())

        doc = ParsedDocument(
            doc_type=DocumentType.RESUME,
            source=source,
            raw_text=text,
            cleaned_text=text,  # Preprocessing will update this
            sections=sections,
            word_count=word_count,
        )

        logger.info(
            "Parsed resume: %d sections detected, %d words.",
            len(sections),
            word_count,
        )
        return doc

    def _detect_sections(self, text: str) -> dict[str, DocumentSection]:
        """
        Detect and extract sections from resume text.

        Scans each line for known heading patterns. Content between
        consecutive headings belongs to the preceding section.

        Args:
            text: Full resume text.

        Returns:
            Dictionary mapping section keys to DocumentSection objects.
        """
        lines = text.split("\n")
        sections: dict[str, DocumentSection] = {}
        current_key: str | None = None
        current_name: str | None = None
        current_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_key is not None:
                    current_lines.append("")
                continue

            matched_key = self._match_heading(stripped)

            if matched_key is not None:
                # Save previous section
                if current_key is not None and current_lines:
                    content = "\n".join(current_lines).strip()
                    if content:
                        sections[current_key] = DocumentSection(
                            name=current_name or current_key.title(),
                            content=content,
                        )
                # Start new section
                current_key = matched_key
                current_name = stripped
                current_lines = []
            else:
                if current_key is not None:
                    current_lines.append(stripped)

        # Save last section
        if current_key is not None and current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                sections[current_key] = DocumentSection(
                    name=current_name or current_key.title(),
                    content=content,
                )

        return sections

    @staticmethod
    def _match_heading(line: str) -> str | None:
        """
        Check if a line matches any known resume section heading.

        A line is considered a heading if:
        - It matches a known pattern
        - It is relatively short (≤ 80 characters, typical of headings)

        Args:
            line: A single stripped line of text.

        Returns:
            The section key if matched, otherwise None.
        """
        if len(line) > 80:
            return None

        # Remove common decorators: dashes, colons, equals
        cleaned = re.sub(r"[-=:_|#*]+$", "", line).strip()

        for key, pattern in _RESUME_SECTION_PATTERNS.items():
            if pattern.search(cleaned):
                return key

        return None
