"""
ATS Keyword Coverage Service.

Computes keyword coverage ratio, tracks matched vs missing skills,
and categorizes missing skills into Critical (Must-Have) vs Optional (Nice-to-Have).
"""

from __future__ import annotations

import logging

from app.models.document import ParsedDocument, SkillSet
from app.schemas.response import ATSAnalysisSchema
from app.services.skill_extraction_service import SkillExtractionService

logger = logging.getLogger(__name__)


class ATSService:
    """
    Analyzes ATS keyword alignment and categorizes missing skill gaps.
    """

    def __init__(self, skill_extraction_service: SkillExtractionService) -> None:
        self._skill_extraction = skill_extraction_service

    def analyze_coverage(
        self,
        resume_skills: SkillSet,
        jd_skills: SkillSet,
        jd_doc: ParsedDocument,
        matched_skills: list[str] | None = None,
        missing_skills: list[str] | None = None,
    ) -> ATSAnalysisSchema:
        """
        Compute ATS keyword coverage percentage and critical skill gaps.

        If matched_skills and missing_skills are provided (from SkillMatcher),
        they include synonym expansion matches. Otherwise, exact set intersection is used.
        """
        jd_all = jd_skills.all_skills()
        
        if matched_skills is not None:
            matched = sorted(set(matched_skills))
        else:
            resume_all = resume_skills.all_skills()
            matched = sorted(resume_all & jd_all)

        if missing_skills is not None:
            missing = sorted(set(missing_skills))
        else:
            resume_all = resume_skills.all_skills()
            missing = sorted(jd_all - resume_all)

        total_jd_keywords = len(jd_all)

        if total_jd_keywords == 0:
            coverage_pct = None
            coverage_status = "N/A: Unable to extract structured keywords"
        else:
            coverage_pct = round((len(matched) / total_jd_keywords) * 100.0, 1)
            coverage_status = "OK"

        # Identify mandatory/required skills from JD sections if available
        required_section_text = ""
        for sec_name, sec_obj in jd_doc.sections.items():
            if sec_name in ("required_skills", "requirements", "must_have"):
                required_section_text += " " + sec_obj.content

        critical_missing: list[str] = []
        optional_missing: list[str] = []

        if required_section_text:
            req_skills = self._skill_extraction.extract_skills(required_section_text).all_skills()
            for skill in missing:
                if skill in req_skills:
                    critical_missing.append(skill)
                else:
                    optional_missing.append(skill)
        else:
            # If no clear section split, treat top 50% missing as critical
            critical_missing = missing[: len(missing) // 2 + 1] if missing else []
            optional_missing = missing[len(missing) // 2 + 1 :] if missing else []

        logger.debug(
            "ATS Coverage: %s (%d matched / %d total), Critical Missing: %s",
            f"{coverage_pct:.1f}%" if coverage_pct is not None else "N/A",
            len(matched),
            total_jd_keywords,
            critical_missing,
        )

        return ATSAnalysisSchema(
            coverage_percentage=coverage_pct,
            coverage_status=coverage_status,
            total_jd_keywords=total_jd_keywords,
            matched_keywords=matched,
            missing_keywords=missing,
            critical_missing_skills=sorted(critical_missing),
            optional_missing_skills=sorted(optional_missing),
        )
