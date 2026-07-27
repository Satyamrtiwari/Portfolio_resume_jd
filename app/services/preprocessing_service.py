"""
Text preprocessing service.

Cleans and normalizes document text while preserving original casing.
Lowercasing is done only internally for skill matching comparisons.

Pipeline:
    Raw Text → Normalize whitespace → Normalize bullets →
    Remove repeated punctuation → Strip non-printable → Cleaned Text
"""

from __future__ import annotations

import logging
import re
import unicodedata

logger = logging.getLogger(__name__)


class PreprocessingService:
    """
    Service for cleaning and normalizing document text.

    Does NOT lowercase the document — casing is preserved for display.
    Provides a separate ``normalize_for_comparison()`` method when
    case-insensitive matching is needed internally.
    """

    # ── Bullet characters to normalize ──────────────────────────────────
    _BULLET_PATTERN = re.compile(r"[•▪►▸▹▶◆◇○●■□★☆➤➜→⮞⁃‣⦿⦾]")

    # ── Repeated punctuation ────────────────────────────────────────────
    _REPEATED_PUNCT = re.compile(r"([!?.]){2,}")

    # ── Multiple whitespace / blank lines ───────────────────────────────
    _MULTI_SPACES = re.compile(r"[ \t]+")
    _MULTI_NEWLINES = re.compile(r"\n{3,}")

    # ── Non-printable characters ────────────────────────────────────────
    _NON_PRINTABLE = re.compile(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]"
    )

    def clean_text(self, text: str) -> str:
        """
        Run the full preprocessing pipeline on raw text.

        Steps:
            1. Strip non-printable characters
            2. Normalize Unicode (NFC form)
            3. Normalize bullet characters to dashes
            4. Collapse repeated punctuation
            5. Normalize whitespace (spaces and newlines)
            6. Strip leading/trailing whitespace

        Args:
            text: Raw document text.

        Returns:
            Cleaned text with original casing preserved.
        """
        if not text or not text.strip():
            return ""

        result = text

        # Step 1: Remove non-printable characters
        result = self._NON_PRINTABLE.sub("", result)

        # Step 2: Unicode normalization (NFC)
        result = unicodedata.normalize("NFC", result)

        # Step 3: Normalize bullet characters to dashes
        result = self._BULLET_PATTERN.sub("- ", result)

        # Step 4: Collapse repeated punctuation (e.g., !!! → !)
        result = self._REPEATED_PUNCT.sub(r"\1", result)

        # Step 5: Normalize whitespace
        result = self._MULTI_SPACES.sub(" ", result)
        result = self._MULTI_NEWLINES.sub("\n\n", result)

        # Step 6: Strip
        result = result.strip()

        logger.debug(
            "Preprocessed text: %d → %d characters.",
            len(text),
            len(result),
        )
        return result

    @staticmethod
    def normalize_for_comparison(text: str) -> str:
        """
        Return a lowercased version of text for case-insensitive matching.

        Used internally by skill extraction and matching services.
        NOT applied to the display text.

        Args:
            text: Text to normalize.

        Returns:
            Lowercased text.
        """
        return text.lower().strip()
