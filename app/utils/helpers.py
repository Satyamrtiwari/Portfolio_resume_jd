"""
Helper functions used across the application.

Pure utility functions with no side effects — scoring labels,
time formatting, alignment labels, and explainability generation.
"""


def format_processing_time(seconds: float) -> str:
    """
    Format processing time as a human-readable string.

    Args:
        seconds: Elapsed time in seconds.

    Returns:
        Formatted string like ``"1.23 sec"`` or ``"0.05 sec"``.
    """
    return f"{seconds:.2f} sec"


def calculate_match_level(score: float) -> str:
    """
    Map a numeric score (0-100) to a human-readable match level.

    Args:
        score: Overall match score between 0 and 100.

    Returns:
        One of: Excellent Match, Strong Match, Good Match, Fair Match, Weak Match.
    """
    if score >= 90:
        return "Excellent Match"
    if score >= 75:
        return "Strong Match"
    if score >= 60:
        return "Good Match"
    if score >= 40:
        return "Fair Match"
    return "Weak Match"


def calculate_alignment_label(score: float) -> str:
    """
    Map a numeric score (0-100) to an alignment label.

    Used for experience and education alignment in explainability.

    Args:
        score: Section match score between 0 and 100.

    Returns:
        One of: Strong, Good, Fair, Weak.
    """
    if score >= 75:
        return "Strong"
    if score >= 55:
        return "Good"
    if score >= 35:
        return "Fair"
    return "Weak"


def generate_recommendation(overall_score: float) -> str:
    """
    Generate a fit recommendation based on overall score.

    Args:
        overall_score: Weighted composite score between 0 and 100.

    Returns:
        One of: Excellent Fit, Strong Fit, Good Fit, Fair Fit, Weak Fit.
    """
    if overall_score >= 90:
        return "Excellent Fit"
    if overall_score >= 75:
        return "Strong Fit"
    if overall_score >= 60:
        return "Good Fit"
    if overall_score >= 40:
        return "Fair Fit"
    return "Weak Fit"


def generate_explainability_summary(
    overall_score: float,
    matched_skills: list[str],
    missing_skills: list[str],
    experience_alignment: str,
    education_alignment: str,
    resume_length: int,
    jd_length: int,
) -> str:
    """
    Generate a human-readable explainability paragraph.

    Describes why the model produced the given score, referencing
    matched/missing skills, section alignments, and document lengths.

    Args:
        overall_score: Weighted composite score (0-100).
        matched_skills: List of skills found in both resume and JD.
        missing_skills: List of JD skills not found in resume.
        experience_alignment: Label for experience section alignment.
        education_alignment: Label for education section alignment.
        resume_length: Word count of the resume.
        jd_length: Word count of the JD.

    Returns:
        A multi-sentence summary string.
    """
    total_required = len(matched_skills) + len(missing_skills)
    matched_count = len(matched_skills)
    missing_count = len(missing_skills)

    parts: list[str] = []

    # Skill coverage
    if total_required > 0:
        pct = (matched_count / total_required) * 100
        parts.append(
            f"The candidate matches {matched_count} of {total_required} "
            f"required skills ({pct:.0f}% coverage)."
        )
    else:
        parts.append("No specific skills were identified in the job description.")

    # Experience alignment
    parts.append(
        f"Experience sections show {experience_alignment.lower()} relevance "
        f"to the role responsibilities."
    )

    # Missing skills
    if missing_count > 0:
        top_missing = ", ".join(missing_skills[:5])
        parts.append(f"Key gaps include: {top_missing}.")

    # Education
    parts.append(f"Education alignment is {education_alignment.lower()}.")

    # Document size note
    if resume_length < 100:
        parts.append(
            "Note: The resume is very short, which may affect scoring accuracy."
        )
    if jd_length < 50:
        parts.append(
            "Note: The job description is very short, which may affect scoring accuracy."
        )

    return " ".join(parts)
