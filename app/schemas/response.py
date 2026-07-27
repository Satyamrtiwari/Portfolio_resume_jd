"""
Pydantic v2 response schemas.

Defines all structured response models returned by the API endpoints.
Reflects v3 ATS platform features: Strategy details, Candidate entities,
ATS coverage, Confidence score, Hiring recommendation, and Extended Health metrics.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Candidate & ATS Schema Components ───────────────────────────────────


class CandidateLinksSchema(BaseModel):
    """Extracted professional web links."""

    github: str | None = Field(None, description="GitHub profile URL.")
    linkedin: str | None = Field(None, description="LinkedIn profile URL.")
    portfolio: str | None = Field(None, description="Personal portfolio URL.")


class CandidateProfileSchema(BaseModel):
    """Structured entities extracted from the candidate's resume."""

    name: str | None = Field(None, description="Candidate full name.")
    email: str | None = Field(None, description="Candidate email address.")
    phone: str | None = Field(None, description="Candidate phone number.")
    location: str | None = Field(None, description="Candidate location/city.")
    links: CandidateLinksSchema = Field(default_factory=CandidateLinksSchema, description="Extracted web links.")
    total_years_experience: float = Field(0.0, description="Total years of work experience detected.")
    current_designation: str | None = Field(None, description="Current or most recent job title.")
    highest_degree: str | None = Field(None, description="Highest degree detected (e.g. Master's, Bachelor's).")
    degree_branch: str | None = Field(None, description="Field of study / specialization.")
    company_names: list[str] = Field(default_factory=list, description="Extracted company names worked at.")


class EducationBreakdownSchema(BaseModel):
    """Structured qualification evaluation breakdown."""

    highest_qualification: str = Field(..., description="Highest qualification detected in resume.")
    minimum_required: str = Field(..., description="Minimum degree required by JD.")
    status: str = Field(..., description="Exceeds Requirement, Meets Requirement, or Below Requirement.")


class ATSAnalysisSchema(BaseModel):
    """ATS Keyword and Critical Skill Coverage analysis."""

    coverage_percentage: float | None = Field(None, description="ATS keyword coverage ratio (0-100% or None for N/A).")
    coverage_status: str = Field("OK", description="Coverage status (e.g., 'OK' or 'N/A: Unable to extract structured keywords').")
    total_jd_keywords: int = Field(..., ge=0, description="Total keywords/skills required by JD.")
    matched_keywords: list[str] = Field(default_factory=list, description="Keywords present in resume.")
    missing_keywords: list[str] = Field(default_factory=list, description="Keywords missing from resume.")
    critical_missing_skills: list[str] = Field(default_factory=list, description="Mandatory Must-Have skills missing.")
    optional_missing_skills: list[str] = Field(default_factory=list, description="Nice-to-Have skills missing.")


class WeightStrategyDetailSchema(BaseModel):
    """Weight Strategy Engine execution details."""

    strategy_used: str = Field(..., description="AUTO, MANUAL, or PRESET.")
    preset_applied: str | None = Field(None, description="Preset name if strategy=PRESET.")
    weights: dict[str, float] = Field(..., description="Active weight percentage allocation per dimension.")
    reasoning: dict[str, str] = Field(default_factory=dict, description="Explanation for each dimension weight.")


class RecommendationSchema(BaseModel):
    """Hiring decision recommendation."""

    decision: str = Field(..., description="Highly Recommended, Recommended, Needs Review, Borderline, Reject.")
    summary: str = Field(..., description="Rationale for the recommendation decision.")
    strengths: list[str] = Field(default_factory=list, description="Key candidate strengths identified.")
    weaknesses: list[str] = Field(default_factory=list, description="Candidate risk factors and skill gaps.")
    hiring_risk: str = Field("Low", description="Hiring risk level: Low, Medium, or High.")
    interview_recommendation: str = Field("Schedule Screening Call", description="Recruiter action: Advance to Interview, Technical Screen, or Reject.")


class ConfidenceSchema(BaseModel):
    """Prediction confidence score with explanation."""

    score: float = Field(..., ge=0, le=100, description="Confidence percentage (0-100%).")
    reasons: list[str] = Field(default_factory=list, description="Itemized bullet reasons explaining confidence score.")


class SkillsDetail(BaseModel):
    """Categorized skills extracted from a document."""

    languages: list[str] = Field(default_factory=list, description="Programming languages detected.")
    frameworks: list[str] = Field(default_factory=list, description="Frameworks and libraries detected.")
    tools: list[str] = Field(default_factory=list, description="DevOps and development tools detected.")
    cloud: list[str] = Field(default_factory=list, description="Cloud platforms and services detected.")
    databases: list[str] = Field(default_factory=list, description="Database technologies detected.")
    ai_ml: list[str] = Field(default_factory=list, description="AI/ML frameworks and concepts detected.")


class ScoreBreakdown(BaseModel):
    """Individual dimension scores and weighted composite."""

    overall_score: float = Field(..., ge=0, le=100, description="Weighted composite score (0-100).")
    skill_score: float = Field(..., ge=0, le=100, description="Skill match score (0-100).")
    experience_score: float = Field(..., ge=0, le=100, description="Experience alignment score (0-100).")
    education_score: float = Field(..., ge=0, le=100, description="Education alignment score (0-100).")
    projects_score: float | None = Field(None, description="Projects alignment score (0-100 or None/N/A).")
    semantic_score: float = Field(..., ge=0, le=100, description="Full-document semantic similarity score (0-100).")
    experience_explainability: list[str] = Field(default_factory=list, description="Itemized experience requirement checks (✓/✗).")


class SectionMatch(BaseModel):
    """A single section-to-section similarity result."""

    resume_section: str = Field(..., description="Name of the resume section.")
    jd_section: str = Field(..., description="Name of the JD section.")
    similarity: float = Field(..., ge=0, le=1, description="Cosine similarity between sections (0-1).")


class Explainability(BaseModel):
    """Structured reasoning explaining the match score."""

    matched_skills: list[str] = Field(default_factory=list, description="Skills found in both resume and JD.")
    missing_skills: list[str] = Field(default_factory=list, description="JD skills not found in resume.")
    experience_alignment: str = Field(..., description="Experience alignment label: Strong, Good, Fair, or Weak.")
    education_alignment: str = Field(..., description="Education alignment label: Strong, Good, Fair, or Weak.")
    recommendation: str = Field(..., description="Overall fit recommendation.")
    summary: str = Field(..., description="Human-readable paragraph explaining the score.")


class RecruiterSummarySchema(BaseModel):
    """Executive recruiter summary."""

    strengths: list[str] = Field(default_factory=list, description="Key candidate strengths.")
    weaknesses: list[str] = Field(default_factory=list, description="Candidate gaps and concerns.")
    critical_missing_skills: list[str] = Field(default_factory=list, description="Mandatory Must-Have skills missing.")
    overall_recommendation: str = Field(..., description="Final executive hiring recommendation.")


# ── Main Response Models ────────────────────────────────────────────────


class MatchResponse(BaseModel):
    """Complete response from the /match endpoint."""

    match_score: float = Field(..., ge=0, le=100, description="Overall weighted match score (0-100).")
    confidence: ConfidenceSchema = Field(..., description="Prediction confidence score and explanation.")
    match_level: str = Field(..., description="Human-readable match level label.")
    recommendation: RecommendationSchema = Field(..., description="Actionable hiring decision recommendation.")
    recruiter_summary: RecruiterSummarySchema = Field(..., description="Executive recruiter summary.")
    weight_strategy: WeightStrategyDetailSchema = Field(..., description="Weight Strategy Engine details.")
    scores: ScoreBreakdown = Field(..., description="Per-dimension score breakdown.")
    education_breakdown: EducationBreakdownSchema = Field(..., description="Structured qualification evaluation breakdown.")
    ats_analysis: ATSAnalysisSchema = Field(..., description="ATS keyword coverage and critical skills.")
    candidate_profile: CandidateProfileSchema = Field(..., description="Structured candidate entities.")
    resume_skills: SkillsDetail = Field(..., description="Skills extracted from the resume.")
    jd_skills: SkillsDetail = Field(..., description="Skills extracted from the job description.")
    explainability: Explainability = Field(..., description="Structured reasoning for the match.")
    top_matching_sections: list[SectionMatch] = Field(
        default_factory=list,
        description="Top section-to-section similarity pairs.",
    )
    resume_length: int = Field(..., ge=0, description="Word count of the resume.")
    jd_length: int = Field(..., ge=0, description="Word count of the job description.")
    processing_time: str = Field(..., description="Total processing time (e.g., '0.18 sec').")

    # Backward compatibility property for confidence_score
    @property
    def confidence_score(self) -> float:
        return self.confidence.score


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""

    status: str = Field(..., description="Service health status.")
    model_loaded: bool = Field(..., description="Whether the embedding model is loaded.")
    model_name: str = Field(..., description="Name of the loaded embedding model.")
    embedding_dimension: int = Field(..., description="Dimension of the embedding vectors.")
    model_size: str = Field(..., description="Estimated size of the loaded model.")
    device: str = Field(..., description="Device the model is running on (cpu/cuda).")
    uptime: str = Field(..., description="Service uptime since startup.")
    version: str = Field(..., description="Application version.")
    memory_usage_mb: float = Field(..., description="RAM memory usage in MB.")
    cpu_percent: float = Field(..., description="Current CPU utilization percentage.")
    cache_status: str = Field(..., description="Status of skill taxonomy and model cache.")


class ModelInfoResponse(BaseModel):
    """Response from the /model endpoint."""

    model_name: str = Field(..., description="Name of the embedding model.")
    embedding_dimension: int = Field(..., description="Dimension of the embedding vectors.")
    device: str = Field(..., description="Device the model is running on.")
    load_time: str = Field(..., description="Time taken to load the model.")


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str = Field(..., description="Human-readable error message.")
    request_id: str | None = Field(None, description="Request ID for traceability.")
