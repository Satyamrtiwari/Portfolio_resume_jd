"""
Projects Matcher.

Evaluates candidate personal/professional projects section against
job responsibilities and tech stack requirements.
Returns None (N/A) if no projects section exists in the resume.
"""

from __future__ import annotations

import logging

from app.matchers.base_matcher import BaseMatcher
from app.models.document import ParsedDocument, SkillSet

logger = logging.getLogger(__name__)

_PROJECTS_KEYS = {"projects", "key_projects", "portfolio", "personal_projects"}


class ProjectsMatcher(BaseMatcher):
    """
    Evaluates practical project relevance using section embeddings and skill presence.
    Returns None if no projects section is present.
    """

    def score(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
        resume_skills: SkillSet | None = None,
        jd_skills: SkillSet | None = None,
    ) -> float | None:
        """
        Compute projects match score (0-100 or None if N/A).
        """
        proj_section = None
        for key in _PROJECTS_KEYS:
            if key in resume_doc.sections:
                proj_section = resume_doc.sections[key]
                break

        # If resume contains NO projects, return None (N/A)
        if not proj_section or not proj_section.content.strip() or len(proj_section.content.strip()) < 15:
            logger.info("No distinct projects section found; returning None (N/A).")
            return None

        # Section embedding cosine similarity
        sim_score = 70.0
        if proj_section.embedding is not None and jd_doc.embedding is not None:
            sim = self.compute_cosine_similarity(proj_section.embedding, jd_doc.embedding)
            sim_score = min(max(sim * 100.0, 0.0), 100.0)

        # Skill overlap within project section
        tech_score = 75.0
        if jd_skills and not jd_skills.is_empty():
            proj_text = proj_section.content.lower()
            jd_all = jd_skills.all_skills()
            matched = sum(1 for s in jd_all if s in proj_text)
            tech_score = min((matched / len(jd_all)) * 120.0, 100.0) if len(jd_all) > 0 else 75.0

        final_score = (0.6 * sim_score) + (0.4 * tech_score)
        return round(final_score, 2)
