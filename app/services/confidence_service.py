"""
Confidence Calculation Service.

Computes prediction confidence percentage (0-100%) and itemized confidence reasons
based on document completeness, entity extraction fidelity, and score consistency.
"""

from __future__ import annotations

import logging
import statistics

from app.models.document import CandidateProfile, ParsedDocument
from app.schemas.response import ConfidenceSchema, ScoreBreakdown

logger = logging.getLogger(__name__)


class ConfidenceService:
    """
    Evaluates reliability and statistical confidence of the matching engine prediction.
    """

    def calculate_confidence(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
        candidate_profile: CandidateProfile,
        scores: ScoreBreakdown,
    ) -> ConfidenceSchema:
        """
        Compute prediction confidence score (0-100%) and itemized bullet explanations.
        """
        reasons: list[str] = []

        # 1. Length & Completeness Factor (Max 40 pts)
        length_pts = 0.0
        if resume_doc.word_count >= 300:
            length_pts += 20.0
            reasons.append(f"Resume length adequate ({resume_doc.word_count} words)")
        elif resume_doc.word_count >= 150:
            length_pts += 10.0
            reasons.append(f"Resume concise ({resume_doc.word_count} words)")
        else:
            reasons.append("Resume word count low")

        if jd_doc.word_count >= 150:
            length_pts += 20.0
        elif jd_doc.word_count >= 75:
            length_pts += 10.0

        # 2. Entity Extraction Fidelity (Max 30 pts)
        entity_pts = 0.0
        extracted_cnt = 0
        if candidate_profile.name:
            entity_pts += 10.0
            extracted_cnt += 1
        if candidate_profile.email:
            entity_pts += 5.0
            extracted_cnt += 1
        if candidate_profile.total_years_experience > 0:
            entity_pts += 10.0
            extracted_cnt += 1
        if candidate_profile.highest_degree:
            entity_pts += 5.0
            extracted_cnt += 1

        if extracted_cnt >= 3:
            reasons.append(f"High entity extraction fidelity ({extracted_cnt} key profile fields detected)")
        else:
            reasons.append("Partial entity extraction (few profile fields detected)")

        # 3. Project Section Presence
        if scores.projects_score is None:
            reasons.append("Missing dedicated personal/professional projects section in resume")

        # 4. Semantic Similarity Context
        if scores.semantic_score >= 70.0:
            reasons.append(f"Strong semantic text alignment ({scores.semantic_score:.1f}%)")
        else:
            reasons.append(f"Semantic text similarity score moderate ({scores.semantic_score:.1f}%)")

        # 5. Score Variance / Consistency (Max 30 pts)
        dimension_scores = [
            scores.skill_score,
            scores.experience_score,
            scores.education_score,
            scores.semantic_score,
        ]

        stdev = statistics.stdev(dimension_scores) if len(dimension_scores) > 1 else 10.0
        variance_pts = max(30.0 - (stdev * 0.8), 5.0)

        total_confidence = length_pts + entity_pts + variance_pts
        confidence = min(max(total_confidence, 40.0), 99.0)

        logger.debug(
            "Confidence Calculation: Length=%.1f, Entity=%.1f, Variance=%.1f -> Confidence=%.1f%%",
            length_pts,
            entity_pts,
            variance_pts,
            confidence,
        )

        return ConfidenceSchema(
            score=round(confidence, 1),
            reasons=reasons,
        )
