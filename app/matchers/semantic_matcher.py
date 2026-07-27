"""
Semantic matcher.

Computes full-document cosine similarity and per-section similarities
to identify top matching section pairs between resume and JD.
"""

from __future__ import annotations

import logging

import numpy as np

from app.matchers.base_matcher import BaseMatcher
from app.models.document import ParsedDocument

logger = logging.getLogger(__name__)


class SemanticMatcher(BaseMatcher):
    """
    Computes semantic similarity between resume and JD.

    Uses the full-document embeddings for the overall score,
    and per-section embeddings for top matching section pairs.
    """

    def score(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
    ) -> float:
        """
        Compute semantic similarity score (0-100).

        Uses full-document embeddings.

        Args:
            resume_doc: Parsed resume with embedding populated.
            jd_doc: Parsed JD with embedding populated.

        Returns:
            Semantic similarity score between 0 and 100.
        """
        if resume_doc.embedding is None or jd_doc.embedding is None:
            logger.warning("Missing document embeddings; returning 0.")
            return 0.0

        similarity = self.compute_cosine_similarity(
            resume_doc.embedding,
            jd_doc.embedding,
        )

        # Clamp to [0, 1] (cosine sim can be slightly negative)
        similarity = max(0.0, min(1.0, similarity))
        score = similarity * 100

        logger.debug("Semantic score: %.2f (similarity: %.4f)", score, similarity)
        return round(score, 2)

    def find_top_matching_sections(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
        top_n: int = 5,
    ) -> list[dict]:
        """
        Find the top-N most similar section pairs between resume and JD.

        Compares every resume section against every JD section and
        returns the highest-scoring pairs.

        Args:
            resume_doc: Parsed resume with section embeddings.
            jd_doc: Parsed JD with section embeddings.
            top_n: Maximum number of section pairs to return.

        Returns:
            List of dicts with resume_section, jd_section, and similarity.
        """
        pairs: list[dict] = []

        for r_key, r_section in resume_doc.sections.items():
            if r_section.embedding is None:
                continue
            for j_key, j_section in jd_doc.sections.items():
                if j_section.embedding is None:
                    continue

                sim = self.compute_cosine_similarity(
                    r_section.embedding,
                    j_section.embedding,
                )
                sim = max(0.0, min(1.0, sim))

                pairs.append({
                    "resume_section": r_section.name,
                    "jd_section": j_section.name,
                    "similarity": round(sim, 4),
                })

        # Sort by similarity descending and return top N
        pairs.sort(key=lambda p: p["similarity"], reverse=True)
        return pairs[:top_n]
