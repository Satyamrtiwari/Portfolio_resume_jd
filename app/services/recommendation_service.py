"""
Recommendation Service.

Translates overall scores, ATS coverage, and critical skill checks into
recruiter-style actionable hiring decision recommendations.

Possible Decisions:
    - Highly Recommended (Score >= 85, no critical missing skills)
    - Recommended (Score 70-84, max 1 critical missing skill)
    - Needs Review (Score 55-69)
    - Borderline (Score 40-54)
    - Reject (Score < 40 or severe experience deficit)
"""

from __future__ import annotations

import logging

from app.schemas.response import ATSAnalysisSchema, RecommendationSchema, ScoreBreakdown

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Evaluates applicant suitability and returns recruiter-style hiring recommendations.
    """

    def generate_recommendation(
        self,
        scores: ScoreBreakdown,
        ats_analysis: ATSAnalysisSchema,
        candidate_yoe: float = 0.0,
        required_yoe: float = 0.0,
        resume_text: str = "",
        jd_domain: str | None = None,
    ) -> RecommendationSchema:
        """
        Generate hiring decision, recruiter summary, strengths, weaknesses, hiring risk, and interview advice.
        """
        overall = scores.overall_score
        num_critical_missing = len(ats_analysis.critical_missing_skills)
        yoe_deficit = required_yoe - candidate_yoe if required_yoe > 0 else 0.0

        decision = "Needs Review"
        summary_parts: list[str] = []
        strengths: list[str] = []
        weaknesses: list[str] = []
        hiring_risk = "Medium"
        interview_rec = "Schedule Recruiter Screening Call"

        # Check domain relevance before labeling strengths
        is_domain_relevant = True
        resume_lower = resume_text.lower() if resume_text else ""
        domain_keywords_map = {
            "healthcare rcm": ["healthcare", "medical", "billing", "claims", "pre-auth",
                               "ar process", "rcm", "revenue cycle", "insurance verification",
                               "hipaa", "patient", "denial", "ehr", "emr"],
            "finance": ["finance", "fintech", "trading", "investment", "accounting",
                        "mutual fund", "equity", "portfolio"],
            "artificial intelligence": ["ai", "machine learning", "deep learning", "nlp",
                                        "llm", "neural", "transformer"],
        }

        if jd_domain:
            domain_lower = jd_domain.lower()
            for domain_key, keywords in domain_keywords_map.items():
                if domain_key in domain_lower:
                    domain_hits = sum(1 for kw in keywords if kw in resume_lower)
                    if domain_hits == 0:
                        is_domain_relevant = False
                    break

        # Determine Strengths (domain-validated)
        if scores.skill_score >= 75.0:
            strengths.append("Strong technical & domain skill match")
        if scores.experience_score >= 70.0 and is_domain_relevant:
            strengths.append(f"Relevant domain experience detected ({candidate_yoe:.1f} years)")
        elif candidate_yoe > 0 and not is_domain_relevant:
            strengths.append(f"Has {candidate_yoe:.1f} years total work experience (different domain)")
        elif scores.experience_score >= 70.0:
            strengths.append(f"Relevant experience detected ({candidate_yoe:.1f} years)")
        if ats_analysis.coverage_percentage and ats_analysis.coverage_percentage >= 80.0:
            strengths.append(f"High ATS keyword coverage ({ats_analysis.coverage_percentage:.1f}%)")
        if not strengths:
            strengths.append("Basic candidate eligibility criteria met")

        # Determine Weaknesses & Risk
        if not is_domain_relevant and jd_domain:
            weaknesses.append(f"Domain mismatch: candidate background does not align with {jd_domain} domain")
        if num_critical_missing > 0:
            missing_str = ", ".join(ats_analysis.critical_missing_skills[:3])
            weaknesses.append(f"Missing mandatory skills: {missing_str}")
        if yoe_deficit > 1.5:
            weaknesses.append(f"Experience deficit ({candidate_yoe:.1f} yrs vs {required_yoe:.1f} yrs required)")
        if scores.projects_score is None:
            weaknesses.append("No personal or professional projects section detected in resume")
        if not weaknesses:
            weaknesses.append("Minor score variance across secondary sections")

        # Decision Matrix
        if overall >= 85.0 and num_critical_missing == 0 and yoe_deficit <= 1.0:
            decision = "Highly Recommended"
            hiring_risk = "Low"
            interview_rec = "Advance to Hiring Manager / Final Interview"
            summary_parts.append(
                f"Candidate achieves exceptional match score ({overall:.1f}%) "
                f"and satisfies mandatory domain requirements."
            )
        elif overall >= 70.0 and num_critical_missing <= 1:
            decision = "Recommended"
            hiring_risk = "Low"
            interview_rec = "Schedule Technical Screening Interview"
            summary_parts.append(
                f"Candidate demonstrates strong alignment ({overall:.1f}%) "
                f"with solid skill and experience overlap."
            )
        elif overall >= 55.0:
            decision = "Needs Review"
            hiring_risk = "Medium"
            interview_rec = "Recruiter Phone Screen to Verify Specific Experience Gaps"
            summary_parts.append(
                f"Candidate meets baseline qualification criteria ({overall:.1f}%). "
                f"Recruiter review recommended to verify domain alignment."
            )
        elif overall >= 40.0:
            decision = "Borderline"
            hiring_risk = "High"
            interview_rec = "Hold for Pipeline Review (Potential Backfill)"
            summary_parts.append(
                f"Candidate shows borderline fit ({overall:.1f}%). "
                f"Several required skill or experience thresholds are unmet."
            )
        else:
            decision = "Reject"
            hiring_risk = "High"
            interview_rec = "Do Not Advance (Does Not Meet Qualifications)"
            summary_parts.append(
                f"Candidate score ({overall:.1f}%) falls below baseline qualification criteria."
            )

        summary = " ".join(summary_parts)
        logger.debug("Hiring Recommendation: Decision=%s, Risk=%s", decision, hiring_risk)

        return RecommendationSchema(
            decision=decision,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            hiring_risk=hiring_risk,
            interview_recommendation=interview_rec,
        )
