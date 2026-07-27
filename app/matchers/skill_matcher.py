"""
Skill matcher.

Compares categorized skill sets between resume and JD using exact matching
and domain-specific synonym taxonomy mapping.
"""

from __future__ import annotations

import logging

from app.matchers.base_matcher import BaseMatcher
from app.models.document import SkillSet

logger = logging.getLogger(__name__)

# Domain Synonym Mapping for Healthcare RCM, Tech, and Operations
_SYNONYM_GROUPS: list[set[str]] = [
    {"medical billing", "ar process", "claims auditing", "insurance verification", "revenue cycle management", "rcm", "pre-authorization", "pre-auth"},
    {"accounts receivable", "ar process", "ar associate", "claims management"},
    {"insurance verification", "pre-authorization", "pre-auth", "eligibility verification", "prior authorization"},
    {"healthcare", "medical", "hospital", "clinical"},
    {"fastapi", "rest api", "python api", "web api"},
    {"kubernetes", "k8s", "container orchestration"},
    {"aws", "amazon web services", "cloud infrastructure"},
    {"gcp", "google cloud platform"},
    {"react", "react.js", "reactjs", "frontend"},
]


class SkillMatcher(BaseMatcher):
    """
    Computes skill match score between resume and JD skill sets using exact + synonym matching.
    """

    def _expand_synonyms(self, skill: str) -> set[str]:
        skill_lower = skill.lower()
        expanded = {skill_lower}
        for group in _SYNONYM_GROUPS:
            if skill_lower in group:
                expanded.update(group)
        return expanded

    def score(
        self,
        resume_skills: SkillSet,
        jd_skills: SkillSet,
    ) -> float:
        """
        Compute skill match score (0-100) using exact and synonym matching.
        """
        jd_all = jd_skills.all_skills()
        resume_all = resume_skills.all_skills()

        if not jd_all:
            logger.info("JD has no extractable skills; returning neutral score 50.")
            return 50.0

        # Expand resume skills with domain synonyms
        resume_expanded = set()
        for s in resume_all:
            resume_expanded.update(self._expand_synonyms(s))

        matched_count = 0
        for jd_skill in jd_all:
            jd_expanded = self._expand_synonyms(jd_skill)
            if jd_expanded & resume_expanded:
                matched_count += 1

        match_ratio = matched_count / len(jd_all)
        score = min(match_ratio * 100, 100.0)

        logger.debug(
            "Skill score: %.2f (%d matched / %d required)",
            score,
            matched_count,
            len(jd_all),
        )
        return round(score, 2)

    def get_matched_skills(
        self,
        resume_skills: SkillSet,
        jd_skills: SkillSet,
    ) -> list[str]:
        """Return sorted list of matched skills (including synonym matches)."""
        jd_all = jd_skills.all_skills()
        resume_all = resume_skills.all_skills()

        resume_expanded = set()
        for s in resume_all:
            resume_expanded.update(self._expand_synonyms(s))

        matched = set()
        for jd_skill in jd_all:
            jd_expanded = self._expand_synonyms(jd_skill)
            if jd_expanded & resume_expanded:
                matched.add(jd_skill)

        return sorted(matched)

    def get_missing_skills(
        self,
        resume_skills: SkillSet,
        jd_skills: SkillSet,
    ) -> list[str]:
        """Return sorted list of missing skills."""
        matched = set(self.get_matched_skills(resume_skills, jd_skills))
        return sorted(jd_skills.all_skills() - matched)
