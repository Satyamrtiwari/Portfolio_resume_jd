"""
Enhanced Education Matcher.

Evaluates candidate degree tier (Ph.D. > Master's > Bachelor's > Diploma),
branch specialization match (STEM / CS / Business / Healthcare),
and section embedding similarity.
"""

from __future__ import annotations

import logging

import numpy as np

from app.matchers.base_matcher import BaseMatcher
from app.models.document import CandidateProfile, JDEntity, ParsedDocument
from app.schemas.response import EducationBreakdownSchema

logger = logging.getLogger(__name__)

_RESUME_EDUCATION_KEYS = {"education", "certifications"}
_JD_QUALIFICATION_KEYS = {"qualifications", "preferred_skills", "requirements"}

_DEGREE_TIERS: dict[str, int] = {
    "Ph.D.": 5,
    "Master's": 4,
    "Bachelor's": 3,
    "HSC / 10+2 Equivalent": 2,
    "SSC / 10th Standard": 1,
    "Associate / Diploma": 2,
}


class EducationMatcher(BaseMatcher):
    """
    Evaluates education tier eligibility, branch specialization alignment, and embeddings.
    """

    def score(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
        candidate_profile: CandidateProfile | None = None,
        jd_entity: JDEntity | None = None,
    ) -> float:
        """
        Compute education match score (0-100).
        """
        tier_score = self._compute_degree_tier_score(candidate_profile, jd_entity)
        branch_score = self._compute_branch_score(candidate_profile, jd_entity)
        semantic_edu_score = self._compute_semantic_score(resume_doc, jd_doc)

        overall = (0.50 * tier_score) + (0.30 * branch_score) + (0.20 * semantic_edu_score)
        final_score = min(max(overall, 0.0), 100.0)

        logger.debug(
            "Education Matcher Breakdown: Tier=%.1f, Branch=%.1f, Semantic=%.1f -> Final=%.1f",
            tier_score,
            branch_score,
            semantic_edu_score,
            final_score,
        )

        return round(final_score, 2)

    def generate_education_breakdown(
        self,
        profile: CandidateProfile | None,
        jd_entity: JDEntity | None,
    ) -> EducationBreakdownSchema:
        """
        Generate structured education evaluation breakdown.
        """
        highest = profile.highest_degree if profile and profile.highest_degree else "Bachelor's Degree / HSC"
        min_req = jd_entity.required_degree if jd_entity and jd_entity.required_degree else "Minimum HSC / Graduate Preferred"

        cand_tier = _DEGREE_TIERS.get(highest, 3)
        req_tier = _DEGREE_TIERS.get(min_req, 2)

        if cand_tier > req_tier:
            status = "Exceeds Requirement"
        elif cand_tier == req_tier:
            status = "Meets Requirement"
        else:
            status = "Below Requirement"

        return EducationBreakdownSchema(
            highest_qualification=highest,
            minimum_required=min_req,
            status=status,
        )

    def _compute_degree_tier_score(
        self,
        profile: CandidateProfile | None,
        jd_entity: JDEntity | None,
    ) -> float:
        if not profile or not profile.highest_degree:
            return 70.0

        cand_tier = _DEGREE_TIERS.get(profile.highest_degree, 2)
        req_degree = jd_entity.required_degree if jd_entity else None
        req_tier = _DEGREE_TIERS.get(req_degree, 2) if req_degree else 2

        if cand_tier >= req_tier:
            return 100.0
        elif cand_tier == req_tier - 1:
            return 70.0
        else:
            return 50.0

    def _compute_branch_score(
        self,
        profile: CandidateProfile | None,
        jd_entity: JDEntity | None,
    ) -> float:
        if not profile or not profile.degree_branch:
            return 75.0

        cand_branch = profile.degree_branch.lower()
        req_branch = (jd_entity.required_branch.lower() if jd_entity and jd_entity.required_branch else None)

        if req_branch and req_branch in cand_branch:
            return 100.0

        if any(stem in cand_branch for stem in ["computer science", "information technology", "healthcare", "medical", "rcm"]):
            return 95.0

        return 70.0

    def _compute_semantic_score(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
    ) -> float:
        resume_embeddings = self._get_section_embeddings(resume_doc, _RESUME_EDUCATION_KEYS)
        jd_embeddings = self._get_section_embeddings(jd_doc, _JD_QUALIFICATION_KEYS)

        if not resume_embeddings and resume_doc.embedding is not None:
            resume_embeddings = [resume_doc.embedding]
        if not jd_embeddings and jd_doc.embedding is not None:
            jd_embeddings = [jd_doc.embedding]

        if not resume_embeddings or not jd_embeddings:
            return 70.0

        similarities: list[float] = []
        for r_emb in resume_embeddings:
            for j_emb in jd_embeddings:
                sim = self.compute_cosine_similarity(r_emb, j_emb)
                similarities.append(max(0.0, sim))

        avg_sim = sum(similarities) / len(similarities)
        return min(avg_sim * 100.0, 100.0)

    @staticmethod
    def _get_section_embeddings(
        doc: ParsedDocument,
        section_keys: set[str],
    ) -> list[np.ndarray]:
        embeddings: list[np.ndarray] = []
        for key in section_keys:
            sec = doc.sections.get(key)
            if sec is not None and sec.embedding is not None:
                embeddings.append(sec.embedding)
        return embeddings
