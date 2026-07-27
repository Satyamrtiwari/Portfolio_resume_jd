"""
Extraction Schemas (Pydantic v2).

Defines strict, validated Pydantic schemas for candidate resume entity extraction
and job description requirement extraction.

Schemas:
    - ContactInfoSchema
    - WorkExperienceItemSchema
    - EducationItemSchema
    - ExtractedCandidateProfileSchema
    - ExtractedJDEntitySchema
"""

from __future__ import annotations

import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContactInfoSchema(BaseModel):
    """Candidate contact details with strict URL and email sanitization."""

    model_config = ConfigDict(frozen=True)

    name: str | None = Field(default=None, description="Full candidate name")
    email: str | None = Field(default=None, description="Validated candidate email address")
    phone: str | None = Field(default=None, description="Candidate contact phone number")
    location: str | None = Field(default=None, description="Candidate location (City, State)")
    github: str | None = Field(default=None, description="Candidate GitHub profile URL")
    linkedin: str | None = Field(default=None, description="Candidate LinkedIn profile URL")
    portfolio: str | None = Field(default=None, description="Personal website or portfolio URL")

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v: str | None) -> str | None:
        if not v or not isinstance(v, str):
            return None
        cleaned = v.strip().title()
        # Reject blocklisted section titles
        blocklist = {
            "SUMMARY", "PROFILE", "EXPERIENCE", "EDUCATION", "SKILLS",
            "PROJECTS", "CURRICULUM VITAE", "RESUME", "DECLARATION", "OBJECTIVE",
            "PERSONAL DETAILS", "CONTACT"
        }
        if cleaned.upper() in blocklist or len(cleaned) < 2:
            return None
        return cleaned

    @field_validator("portfolio", mode="before")
    @classmethod
    def sanitize_portfolio(cls, v: str | None) -> str | None:
        if not v or not isinstance(v, str):
            return None
        email_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "protonmail.com", "aol.com"}
        clean_url = v.lower().strip()
        domain = clean_url.replace("https://", "").replace("http://", "").split("/")[0]
        if domain in email_domains:
            return None
        return v


class WorkExperienceItemSchema(BaseModel):
    """Structured work experience item."""

    model_config = ConfigDict(frozen=True)

    company_name: str = Field(..., description="Employer company name")
    designation: str | None = Field(default=None, description="Job title / role held")
    start_date: str | None = Field(default=None, description="Employment start date")
    end_date: str | None = Field(default=None, description="Employment end date")
    duration_years: float = Field(default=0.0, description="Calculated duration in years")
    responsibilities: list[str] = Field(default_factory=list, description="Key work responsibilities")


class EducationItemSchema(BaseModel):
    """Structured education history item."""

    model_config = ConfigDict(frozen=True)

    degree: str = Field(..., description="Standardized degree tier (Ph.D., Master's, Bachelor's, HSC, SSC, Diploma)")
    branch: str | None = Field(default=None, description="Degree branch or major specialization")
    institution: str | None = Field(default=None, description="University, college, or board name")
    passing_year: int | None = Field(default=None, description="Graduation or passing year")


class ExtractedCandidateProfileSchema(BaseModel):
    """Full Pydantic profile schema for candidate resumes."""

    model_config = ConfigDict(frozen=True)

    contact: ContactInfoSchema = Field(default_factory=ContactInfoSchema)
    total_years_experience: float = Field(default=0.0, ge=0.0, description="Total verified years of experience")
    current_designation: str | None = Field(default=None, description="Current or most recent job title")
    highest_degree: str | None = Field(default=None, description="Highest degree qualification")
    degree_branch: str | None = Field(default=None, description="Branch specialization of highest degree")
    company_names: list[str] = Field(default_factory=list, description="List of companies worked at")
    work_history: list[WorkExperienceItemSchema] = Field(default_factory=list)
    education_history: list[EducationItemSchema] = Field(default_factory=list)

    @field_validator("company_names", mode="before")
    @classmethod
    def clean_company_names(cls, v: list[str] | None) -> list[str]:
        if not v or not isinstance(v, list):
            return []
        cleaned = []
        noise_words = {
            "savings account", "credit card", "personal loan", "worked as",
            "handle", "conduct", "assist", "provide", "experience in",
            "executive", "manager", "officer", "associate", "representative", "specialist", "analyst", "developer", "engineer", "lead", "intern",
            "road", "street", "wadi", "marg", "nagar", "manzil", "building", "apartment", "floor", "flat", "district", "pipe", "kurla", "mumbai",
            "backend &", "frontend &", "tools &", "programming", "ai &", "frameworks",
            "insurance company", "billing)", "banking)", "company)", "the same", "the position", "same", "opportunity"
        }
        seen_stems = set()
        acronyms = {"au": "AU", "bpo": "BPO", "llp": "LLP", "nbfc": "NBFC", "it": "IT", "rcm": "RCM", "bps": "BPS", "hsc": "HSC", "ssc": "SSC"}

        action_verbs = {
            "understanding", "offering", "providing", "managing", "resolving", "collaborating", "establishing", "assisting",
            "handling", "responding", "maintaining", "collecting", "building", "nurturing", "keeping", "contributing", "developing",
            "followed", "handled", "created", "built", "executed", "and", "or"
        }

        for name in v:
            if isinstance(name, str):
                c = name.strip().strip("()")
                # Strip trailing conjunctions like ", with", ", currently", ", having"
                c = re.sub(r"[\,\s]+\b(?:with|currently|having|where|and|or|for)\b.*$", "", c, flags=re.IGNORECASE).strip()
                c = re.sub(r"[\)\.,\s]+$", "", c).strip()
                c_lower = c.lower()

                first_word = c_lower.split()[0] if c_lower.split() else ""

                if len(c) > 2 and first_word not in action_verbs and not any(nw in c_lower for nw in noise_words):
                    stem = re.sub(r"\b(?:ltd|inc|llc|corp|corporation|company|pvt|private|limited)\b", "", c_lower, flags=re.IGNORECASE).strip()
                    if stem and stem not in seen_stems:
                        seen_stems.add(stem)
                        words = c.split()
                        fixed_words = [acronyms.get(w.lower(), w) for w in words]
                        cleaned.append(" ".join(fixed_words))

        return cleaned[:5]


class ExtractedJDEntitySchema(BaseModel):
    """Full Pydantic requirement schema for job descriptions."""

    model_config = ConfigDict(frozen=True)

    role_title: str | None = Field(default=None, description="Target job designation / role title")
    department: str | None = Field(default=None, description="Department name (e.g. Pre-Authorization, RCM, Engineering)")
    shift: str | None = Field(default=None, description="Work shift requirements (e.g. Night Shift, Rotational)")
    required_years_experience: float = Field(default=0.0, ge=0.0, description="Minimum required years of experience")
    required_degree: str | None = Field(default=None, description="Minimum required degree qualification")
    required_branch: str | None = Field(default=None, description="Required branch or field of study")
    domain_industry: str | None = Field(default=None, description="Target industry domain (Healthcare RCM, Finance, AI/ML, Cloud)")
    mandatory_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
