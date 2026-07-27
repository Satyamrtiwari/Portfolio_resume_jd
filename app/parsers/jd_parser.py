"""
Job Description parser.

Detects JD-specific sections (Required Skills, Preferred Skills,
Responsibilities, Qualifications) from raw text using heading
pattern matching. Returns a structured ParsedDocument.
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

_JD_SECTION_PATTERNS: dict[str, re.Pattern[str]] = {
    "required_skills": re.compile(
        r"^(?:required|must\s+have|essential)\s+(?:skills|qualifications|experience)|"
        r"requirements|what\s+(?:we|you)\s+(?:need|require)|"
        r"minimum\s+qualifications",
        re.IGNORECASE,
    ),
    "preferred_skills": re.compile(
        r"^(?:preferred|nice\s+to\s+have|desired|bonus)\s*(?:skills|qualifications|experience)?|"
        r"plus\s+points?|additional\s+skills|"
        r"preferred\s+qualifications",
        re.IGNORECASE,
    ),
    "responsibilities": re.compile(
        r"^responsibilities|what\s+you(?:'ll|\s+will)\s+do|"
        r"role\s+(?:description|overview)|key\s+responsibilities|"
        r"duties|job\s+description|the\s+role|"
        r"about\s+the\s+(?:role|position|job)",
        re.IGNORECASE,
    ),
    "qualifications": re.compile(
        r"^qualifications|about\s+you|who\s+you\s+are|"
        r"what\s+we(?:'re|\s+are)\s+looking\s+for|"
        r"candidate\s+profile|ideal\s+candidate|"
        r"education\s*(?:&|and)?\s*experience",
        re.IGNORECASE,
    ),
}


class JDParser(BaseDocumentParser):
    """
    Parser specialized for job description documents.

    Detects common JD section headings and splits the document
    into structured sections for downstream matching.
    """

    def parse(
        self,
        text: str,
        source: InputSource,
    ) -> ParsedDocument:
        """
        Parse raw JD text into a structured document.

        Args:
            text: Raw text content of the job description.
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
            doc_type=DocumentType.JOB_DESCRIPTION,
            source=source,
            raw_text=text,
            cleaned_text=text,  # Preprocessing will update this
            sections=sections,
            word_count=word_count,
        )

        logger.info(
            "Parsed JD: %d sections detected, %d words.",
            len(sections),
            word_count,
        )
        return doc

    def _detect_sections(self, text: str) -> dict[str, DocumentSection]:
        """
        Detect and extract sections from JD text.

        Scans each line for known heading patterns. Content between
        consecutive headings belongs to the preceding section.

        Args:
            text: Full JD text.

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
        Check if a line matches any known JD section heading.

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

        for key, pattern in _JD_SECTION_PATTERNS.items():
            if pattern.search(cleaned):
                return key

        return None
