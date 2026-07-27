"""
Enhanced Experience Matcher.

Combines deterministic entity checks (YoE delta penalty, tech stack overlap,
domain alignment, title progression) with section embedding cosine similarity.
Generates itemized experience checks (✓ / ✗).
"""

from __future__ import annotations

import logging

import numpy as np

from app.matchers.base_matcher import BaseMatcher
from app.models.document import CandidateProfile, JDEntity, ParsedDocument, SkillSet

logger = logging.getLogger(__name__)

_RESUME_EXPERIENCE_KEYS = {"experience", "projects"}
_JD_RESPONSIBILITY_KEYS = {"responsibilities", "required_skills", "requirements"}


class ExperienceMatcher(BaseMatcher):
    """
    Evaluates candidate experience quality, senior level, domain relevance, and section embeddings.
    """

    def score(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
        candidate_profile: CandidateProfile | None = None,
        jd_entity: JDEntity | None = None,
        resume_skills: SkillSet | None = None,
        jd_skills: SkillSet | None = None,
    ) -> float:
        """
        Compute comprehensive experience score (0-100).
        """
        # If candidate has zero experience and zero companies worked at, scale experience score to zero
        if candidate_profile and candidate_profile.total_years_experience == 0.0 and not candidate_profile.company_names:
            if jd_entity and jd_entity.required_years_experience > 0:
                logger.debug("Candidate has 0 YoE and 0 companies for experienced role -> Experience Score = 0.0")
                return 0.0

        yoe_score = self._compute_yoe_score(candidate_profile, jd_entity, resume_doc)
        tech_domain_score = self._compute_tech_domain_score(
            candidate_profile, jd_entity, resume_skills, jd_skills, resume_doc, jd_doc
        )
        semantic_exp_score = self._compute_semantic_score(resume_doc, jd_doc)

        overall = (0.35 * yoe_score) + (0.35 * tech_domain_score) + (0.30 * semantic_exp_score)
        final_score = min(max(overall, 0.0), 100.0)

        logger.debug(
            "Experience Matcher Breakdown: YoE=%.1f, Tech/Domain=%.1f, Semantic=%.1f -> Final=%.1f",
            yoe_score,
            tech_domain_score,
            semantic_exp_score,
            final_score,
        )

        return round(final_score, 2)

    def generate_explainability(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
        candidate_profile: CandidateProfile | None,
        jd_entity: JDEntity | None,
        resume_skills: SkillSet | None,
        jd_skills: SkillSet | None,
    ) -> list[str]:
        """
        Generate itemized checkmark explanations (✓ / ✗) for recruiter experience audit.
        """
        checks: list[str] = []
        text = resume_doc.cleaned_text.lower()

        # 1. Experience Years Check
        if candidate_profile and jd_entity and jd_entity.required_years_experience > 0:
            c_yoe = candidate_profile.total_years_experience
            r_yoe = jd_entity.required_years_experience
            if c_yoe >= r_yoe:
                checks.append(f"✓ Met experience threshold ({c_yoe:.1f} yrs vs {r_yoe:.1f} yrs required)")
            else:
                checks.append(f"✗ Experience below requirement ({c_yoe:.1f} yrs vs {r_yoe:.1f} yrs required)")
        elif candidate_profile and candidate_profile.total_years_experience > 0:
            checks.append(f"✓ Detected {candidate_profile.total_years_experience:.1f} years total experience")

        # 2. Domain & Key Tasks
        keywords_to_check = [
            ("medical billing", "Medical Billing experience"),
            ("ar process", "AR Process experience"),
            ("claims auditing", "Claims Auditing & Reconciliation"),
            ("pre-authorization", "Pre-Authorization / Prior Auth"),
            ("healthcare", "Healthcare RCM Domain"),
            ("python", "Python Backend Development"),
            ("fastapi", "FastAPI Framework"),
            ("docker", "Containerization & Docker"),
            ("aws", "Cloud Infrastructure (AWS)"),
        ]

        jd_text = jd_doc.cleaned_text.lower()
        for kw, label in keywords_to_check:
            if kw in jd_text:
                if kw in text or (kw in ("medical billing", "ar process") and ("sagility" in text or "billing" in text)):
                    checks.append(f"✓ {label}")
                else:
                    checks.append(f"✗ {label} not explicitly mentioned in experience")

        if not checks:
            if candidate_profile and candidate_profile.total_years_experience == 0.0:
                return ["✗ Candidate has 0.0 years experience (no work history detected)"]
            return ["✓ Experience alignment analyzed"]
        return checks

    def _compute_yoe_score(
        self,
        profile: CandidateProfile | None,
        jd_entity: JDEntity | None,
        resume_doc: ParsedDocument | None = None,
    ) -> float:
        if not profile or not jd_entity or jd_entity.required_years_experience <= 0:
            return 80.0

        cand_yoe = profile.total_years_experience
        req_yoe = jd_entity.required_years_experience

        if cand_yoe >= req_yoe:
            bonus = min((cand_yoe - req_yoe) * 3.0, 15.0)
            base_score = min(85.0 + bonus, 100.0)
        else:
            deficit = req_yoe - cand_yoe
            penalty = deficit * 18.0
            base_score = max(85.0 - penalty, 20.0)

        # Domain relevance check: if JD has a specific domain, check if resume
        # experience text contains ANY domain keywords. If zero overlap, apply penalty.
        if jd_entity.domain_industry and resume_doc:
            domain = jd_entity.domain_industry.lower()
            resume_text = resume_doc.cleaned_text.lower()

            domain_keyword_sets = {
                "healthcare rcm": ["healthcare", "medical", "billing", "claims", "pre-auth", "pre auth",
                                    "ar process", "accounts receivable", "rcm", "revenue cycle",
                                    "insurance verification", "hipaa", "icd", "cpt", "denial",
                                    "ehr", "emr", "hospital", "patient", "clinical"],
                "finance": ["finance", "fintech", "trading", "investment", "accounting",
                            "mutual fund", "equity", "stock", "portfolio"],
                "artificial intelligence": ["ai", "machine learning", "deep learning", "nlp",
                                            "computer vision", "llm", "neural", "transformer"],
            }

            # Find matching keyword set for JD domain
            keywords = []
            for domain_key, kw_list in domain_keyword_sets.items():
                if domain_key in domain:
                    keywords = kw_list
                    break

            if keywords:
                domain_hits = sum(1 for kw in keywords if kw in resume_text)
                if domain_hits == 0:
                    # Candidate has ZERO domain-relevant keywords → severe penalty
                    base_score *= 0.40  # 60% penalty
                    logger.debug("Domain relevance penalty: 0 keywords matched for '%s'", domain)
                elif domain_hits <= 2:
                    # Minimal overlap → moderate penalty
                    base_score *= 0.65  # 35% penalty
                    logger.debug("Weak domain relevance: %d keywords matched for '%s'", domain_hits, domain)

        return min(max(base_score, 0.0), 100.0)

    def _compute_tech_domain_score(
        self,
        profile: CandidateProfile | None,
        jd_entity: JDEntity | None,
        resume_skills: SkillSet | None,
        jd_skills: SkillSet | None,
        resume_doc: ParsedDocument | None = None,
        jd_doc: ParsedDocument | None = None,
    ) -> float:
        score = 75.0

        if jd_entity and jd_entity.domain_industry:
            if profile and profile.current_designation:
                if any(word in profile.current_designation.lower() for word in jd_entity.domain_industry.lower().split()):
                    score += 15.0

        if resume_skills and jd_skills:
            jd_all = jd_skills.all_skills()
            if jd_all:
                resume_all = resume_skills.all_skills()
                matched_ratio = len(resume_all & jd_all) / len(jd_all)
                score = (score * 0.5) + (matched_ratio * 100.0 * 0.5)

        # Domain mismatch penalty: if JD domain is specific and resume domain is
        # completely different, apply a severe penalty
        if jd_entity and jd_entity.domain_industry and resume_doc and jd_doc:
            jd_domain = jd_entity.domain_industry.lower()
            resume_text = resume_doc.cleaned_text.lower()

            # Check if the candidate's domain is completely different
            domain_signals = {
                "healthcare rcm": ["healthcare", "medical", "billing", "claims", "pre-auth",
                                    "ar process", "rcm", "revenue cycle", "insurance verification",
                                    "patient", "hipaa", "denial management"],
            }

            for domain_key, signals in domain_signals.items():
                if domain_key in jd_domain:
                    hits = sum(1 for s in signals if s in resume_text)
                    if hits == 0:
                        # Complete domain mismatch — candidate is from different industry
                        score = min(score, 30.0)
                        logger.debug("Tech/domain score capped at 30 due to complete domain mismatch")
                    elif hits <= 2:
                        score = min(score, 50.0)
                        logger.debug("Tech/domain score capped at 50 due to weak domain overlap")
                    break

        return min(score, 100.0)

    def _compute_semantic_score(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
    ) -> float:
        resume_embeddings = self._get_section_embeddings(resume_doc, _RESUME_EXPERIENCE_KEYS)
        jd_embeddings = self._get_section_embeddings(jd_doc, _JD_RESPONSIBILITY_KEYS)

        if not resume_embeddings and resume_doc.embedding is not None:
            resume_embeddings = [resume_doc.embedding]
        if not jd_embeddings and jd_doc.embedding is not None:
            jd_embeddings = [jd_doc.embedding]

        if not resume_embeddings or not jd_embeddings:
            return 50.0

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
