"""
Entity extraction service.

Uses regex patterns, heuristics, and rule-based NLP to extract structured entities
from candidate resumes and job descriptions without requiring heavy LLM dependencies.

Extracted Resume Entities:
    - Candidate Name, Email, Phone, Location
    - Professional Web Links (GitHub, LinkedIn, Portfolio)
    - Total Years of Experience (YoE)
    - Company Names & Current/Most Recent Designation
    - Highest Degree & Degree Branch

Extracted JD Entities:
    - Required Years of Experience
    - Required Degree & Branch
    - Industry Domain (Healthcare RCM, Finance, AI/ML, Cloud Infrastructure, etc.)
    - Mandatory vs Preferred Skills
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from app.models.document import (
    CandidateLinks,
    CandidateProfile,
    JDEntity,
    ParsedDocument,
)
from app.schemas.extraction import (
    ContactInfoSchema,
    ExtractedCandidateProfileSchema,
    ExtractedJDEntitySchema,
)

logger = logging.getLogger(__name__)

# ── Regex Patterns ──────────────────────────────────────────────────────

_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+\s*@\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{10}\b"
)

_GITHUB_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_.-]+", re.IGNORECASE)
_LINKEDIN_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_.-]+", re.IGNORECASE)
_PORTFOLIO_PATTERN = re.compile(r"(?:https?://|www\.)[a-zA-Z0-9_.-]+\.[a-zA-Z]{2,}(?:/[a-zA-Z0-9_.-]*)*|\b[a-zA-Z0-9_-]+\.(?:dev|io|me|site|app|tech|portfolio|pages\.dev|github\.io)\b", re.IGNORECASE)

_YOE_PATTERNS = [
    re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)(?:['’`\s]+)?(?:of\s+)?(?:experience|exp)?\s+(?:in|at|with)?\s*([A-Za-z0-9\s]+)?", re.IGNORECASE),
    re.compile(r"(?:experience|exp)\s*:\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"over\s+(\d+(?:\.\d+)?)\s+(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"(\d+(?:\.\d+)?)\s*\+\s*years", re.IGNORECASE),
]

_DATE_RANGE_PATTERN = re.compile(
    r"\b(20\d{2}|19\d{2})\s*[-–—\s\t]+(?:to\s+)?(present|current|now|20\d{2}|19\d{2})\b",
    re.IGNORECASE,
)

_DEGREE_PATTERNS = [
    ("Ph.D.", re.compile(r"\b(?:phd|ph\.d|doctorate)\b", re.IGNORECASE)),
    ("Master's", re.compile(r"\b(?:master'?s?|m\.s|m\.tech|mca|msc|mba)\b", re.IGNORECASE)),
    ("Bachelor's", re.compile(r"\b(?:bachelor'?s?|b\.s|b\.tech|be|bca|bsc|b\.com|graduation|graduate)\b", re.IGNORECASE)),
    ("HSC / 10+2 Equivalent", re.compile(r"\b(?:hsc|12th|10\+2|intermediate|higher\s+secondary)\b", re.IGNORECASE)),
    ("SSC / 10th Standard", re.compile(r"\b(?:ssc|10th|matriculation)\b", re.IGNORECASE)),
    ("Associate / Diploma", re.compile(r"\b(?:diploma|associate'?s?)\b", re.IGNORECASE)),
]

_BRANCH_PATTERNS = [
    ("Computer Science", re.compile(r"\b(?:computer\s+science|cs|cse)\b", re.IGNORECASE)),
    ("Information Technology", re.compile(r"\b(?:information\s+technology|it)\b", re.IGNORECASE)),
    ("Software Engineering", re.compile(r"\bsoftware\s+engineering\b", re.IGNORECASE)),
    ("Data Science / AI", re.compile(r"\b(?:data\s+science|artificial\s+intelligence|ai|machine\s+learning)\b", re.IGNORECASE)),
    ("Electrical / Electronics", re.compile(r"\b(?:electrical|electronics|ece|eee)\b", re.IGNORECASE)),
    ("Business / Finance", re.compile(r"\b(?:business|finance|accounting|commerce|management|mba)\b", re.IGNORECASE)),
    ("Healthcare / Medical", re.compile(r"\b(?:healthcare|medical|nursing|rcm|revenue\s+cycle|billing|pre-auth|ar\s+process)\b", re.IGNORECASE)),
]

_DESIGNATION_PATTERNS = re.compile(
    r"\b(?:senior|jr|sr|lead|principal|staff|head|vp|director|manager|architect|associate|trainee)?\s*"
    r"(?:process\s+associate|sr\s+process\s+associate|software\s+engineer|backend\s+engineer|frontend\s+engineer|"
    r"full\s*stack\s+engineer|data\s+scientist|data\s+engineer|devops\s+engineer|cloud\s+engineer|ai\s+engineer|"
    r"ml\s+engineer|qa\s+engineer|system\s+administrator|product\s+manager|"
    r"rcm\s+specialist|billing\s+specialist|financial\s+analyst|pre-auth\s+associate|ar\s+associate|"
    r"video\s+banker|vkyc\s+(?:associate|executive|officer)|kyc\s+(?:associate|executive|officer|analyst)|"
    r"relationship\s+(?:manager|officer)|customer\s+(?:service|support)\s+(?:executive|officer|associate)|"
    r"process\s+executive|team\s+lead|operations\s+(?:executive|manager|associate)|"
    r"medical\s+coder|medical\s+biller|billing\s+executive|ar\s+(?:caller|executive|analyst)|"
    r"claims\s+(?:analyst|processor|examiner)|pre-?auth\s+(?:specialist|executive|coordinator)|"
    r"verification\s+(?:specialist|executive|officer))\b",
    re.IGNORECASE,
)

_DOMAIN_PATTERNS = [
    ("Healthcare RCM", re.compile(r"\b(?:healthcare|rcm|revenue\s+cycle|hipaa|medical\s+billing|ehr|emr|claim|pre-auth|pre\s+auth|ar\s+process)\b", re.IGNORECASE)),
    ("Finance & FinTech", re.compile(r"\b(?:finance|fintech|banking|trading|payment|accounting|stripe|plaid)\b", re.IGNORECASE)),
    ("Artificial Intelligence & ML", re.compile(r"\b(?:ai|ml|deep\s+learning|llm|nlp|computer\s+vision|rag|transformer)\b", re.IGNORECASE)),
    ("Cloud Infrastructure & DevOps", re.compile(r"\b(?:cloud|devops|kubernetes|terraform|aws|gcp|azure|sre)\b", re.IGNORECASE)),
    ("Backend Engineering", re.compile(r"\b(?:backend|api|microservices|distributed\s+systems|database)\b", re.IGNORECASE)),
    ("Frontend Engineering", re.compile(r"\b(?:frontend|ui/ux|react|nextjs|web\s+applications)\b", re.IGNORECASE)),
]

_HEADER_BLOCKLIST = {
    "CAREER OBJECTIVE", "OBJECTIVE", "SUMMARY", "PROFESSIONAL SUMMARY", "PROFILE",
    "RESUME", "CURRICULUM VITAE", "CONTACT", "CONTACT DETAILS", "EXPERIENCE",
    "WORK EXPERIENCE", "EMPLOYMENT HISTORY", "EDUCATION", "ACADEMIC BACKGROUND",
    "SKILLS", "TECHNICAL SKILLS", "STRENGTHS", "HOBBIES", "PERSONAL DETAILS",
    "DECLARATION", "PROJECTS", "CERTIFICATIONS", "LANGUAGES", "PASSPORT DETAILS",
    "MARITAL STATUS", "SINGLE", "MARRIED", "GENDER", "MALE", "FEMALE", "NATIONALITY",
    "INDIAN", "DATE OF BIRTH", "ADDRESS", "NAV MUMBAI", "MAHARASHTRA"
}

_COMPANY_PATTERNS = re.compile(
    r"\b([A-Z][A-Za-z0-9 \t.,&'-]+?(?:Ltd|Inc|LLC|Corp|Corporation|Company|Services|Technologies|Health|Healthcare|Solutions|Systems|Bank|Finance|NBFC|Pvt|Private\s+Limited|Limited|BPS|BPO|Group|Consultancy|Insurance|Enterprises|Industries|Capital|Fintech|Hospital|Clinic|Pharma|Logistics|Infra))\b",
    re.IGNORECASE,
)

# Positional company extraction: lines containing date ranges in experience section
_DATE_COMPANY_LINE = re.compile(
    r"^([A-Za-z][A-Za-z0-9\s.,&'()–—-]+?)\s+(?:\d{1,2}\s)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}",
    re.IGNORECASE,
)
_STANDALONE_COMPANY_LINE = re.compile(
    r"^([A-Z][A-Za-z0-9\s.,&'()-]{3,50})$",
)


class EntityExtractionService:
    """
    Extracts structured entities from candidates and job descriptions.
    Uses AI Structured Extraction (OpenRouter/Groq/OpenAI) with instant local fallback.
    """

    def __init__(self) -> None:
        from app.services.ai_extraction_service import AIExtractionService
        self.ai_extractor = AIExtractionService()

    async def extract_candidate_profile_schema(self, doc: ParsedDocument) -> ExtractedCandidateProfileSchema:
        """Extract validated candidate profile as a Pydantic v2 schema."""
        # 1. Try AI Structured Extractor if configured
        if self.ai_extractor.is_available:
            ai_schema = await self.ai_extractor.extract_candidate_profile(doc.cleaned_text)
            if ai_schema and ai_schema.contact and ai_schema.contact.name:
                logger.info("Using AI Extracted candidate profile for %s", ai_schema.contact.name)
                return ai_schema

        # 2. Local deterministic fallback
        return self._extract_candidate_profile_schema_local(doc)

    def _extract_candidate_profile_schema_local(self, doc: ParsedDocument) -> ExtractedCandidateProfileSchema:
        text = doc.cleaned_text
        lines = [l.strip() for l in doc.raw_text.split("\n") if l.strip()]

        email = self._extract_regex_first(_EMAIL_PATTERN, text)
        phone = self._extract_regex_first(_PHONE_PATTERN, text)
        name = self._extract_name(lines, email, doc.filename)

        # Fallback to filename ONLY if no candidate name extracted from text
        if not name and doc.filename:
            fn_stem = Path(doc.filename).stem
            fn_clean = re.sub(r"[_\-\.]", " ", fn_stem).strip()
            fn_clean = re.sub(r"\b(?:resume|cv|jd|profile|\d+)\b", "", fn_clean, flags=re.IGNORECASE).strip()
            if fn_clean and len(fn_clean.split()) >= 2:
                name = fn_clean.title()

        location = self._extract_location(text)
        github = self._extract_regex_first(_GITHUB_PATTERN, text)
        linkedin = self._extract_regex_first(_LINKEDIN_PATTERN, text)
        portfolio = self._extract_portfolio(text, github, linkedin)

        total_yoe = self._extract_years_of_experience(text)
        designation = self._extract_designation(lines, text)
        companies = self._extract_company_names(text)
        if name:
            name_words = {w.lower() for w in name.split() if len(w) > 2}
            companies = [c for c in companies if not any(w in c.lower() for w in name_words)]
        highest_degree = self._extract_degree(text)
        degree_branch = self._extract_branch(text)

        contact = ContactInfoSchema(
            name=name,
            email=email,
            phone=phone,
            location=location,
            github=github,
            linkedin=linkedin,
            portfolio=portfolio,
        )

        schema = ExtractedCandidateProfileSchema(
            contact=contact,
            total_years_experience=total_yoe,
            current_designation=designation,
            highest_degree=highest_degree,
            degree_branch=degree_branch,
            company_names=companies,
        )

        logger.debug("Extracted candidate profile Pydantic schema: %s, YoE=%.1f", schema.contact.name or "Unknown", total_yoe)
        return schema

    async def extract_candidate_profile(self, doc: ParsedDocument) -> CandidateProfile:
        """Extract candidate profile domain model."""
        schema = await self.extract_candidate_profile_schema(doc)

        links = CandidateLinks(
            github=schema.contact.github,
            linkedin=schema.contact.linkedin,
            portfolio=schema.contact.portfolio,
        )

        return CandidateProfile(
            name=schema.contact.name,
            email=schema.contact.email,
            phone=schema.contact.phone,
            location=schema.contact.location,
            links=links,
            total_years_experience=schema.total_years_experience,
            current_designation=schema.current_designation,
            highest_degree=schema.highest_degree,
            degree_branch=schema.degree_branch,
            company_names=schema.company_names,
        )

    async def extract_jd_entity_schema(self, doc: ParsedDocument) -> ExtractedJDEntitySchema:
        """Extract job description requirements as a Pydantic v2 schema."""
        if self.ai_extractor.is_available:
            ai_schema = await self.ai_extractor.extract_jd_entity(doc.cleaned_text)
            if ai_schema and (ai_schema.required_years_experience > 0 or ai_schema.domain_industry):
                logger.info("Using AI Extracted JD entity requirements: YoE=%.1f", ai_schema.required_years_experience)
                return ai_schema

        return self._extract_jd_entity_schema_local(doc)

    def _extract_jd_entity_schema_local(self, doc: ParsedDocument) -> ExtractedJDEntitySchema:
        text = doc.cleaned_text
        req_yoe = self._extract_years_of_experience(text)
        req_degree = self._extract_jd_required_degree(text)
        req_branch = self._extract_branch(text)
        domain = self._extract_domain(text)

        schema = ExtractedJDEntitySchema(
            required_years_experience=req_yoe,
            required_degree=req_degree,
            required_branch=req_branch,
            domain_industry=domain,
        )

        logger.debug("Extracted JD Pydantic schema: YoE=%.1f, Domain=%s", req_yoe, domain or "General")
        return schema

    async def extract_jd_entity(self, doc: ParsedDocument) -> JDEntity:
        """Extract job description requirements domain model."""
        schema = await self.extract_jd_entity_schema(doc)

        return JDEntity(
            required_years_experience=schema.required_years_experience,
            required_degree=schema.required_degree,
            required_branch=schema.required_branch,
            domain_industry=schema.domain_industry,
        )

    # ── Private Extraction Helpers ──────────────────────────────────────

    @staticmethod
    def _extract_regex_first(pattern: re.Pattern[str], text: str) -> str | None:
        match = pattern.search(text)
        return match.group(0) if match else None

    def _extract_name(self, lines: list[str], email: str | None, filename: str | None = None) -> str | None:
        """
        Extract candidate name using positional detection, contact proximity,
        filename matching, declaration signatures, and header exclusion blocklists.
        """
        # Strategy 0: Check if clean filename stem (without numbers or noise words) matches candidate name in text
        if filename:
            fn_stem = Path(filename).stem
            fn_clean = re.sub(r"[_\-\.\d+]", " ", fn_stem).strip()
            fn_clean = re.sub(r"\b(?:resume|resum|cv|jd|profile|select|copy|final|updated|new)\b", "", fn_clean, flags=re.IGNORECASE).strip()
            words = [w for w in fn_clean.split() if len(w) >= 2]
            if len(words) >= 2 and all(w.isalpha() for w in words):
                full_fn = " ".join(words).title()
                # Confirm all name words appear in document text
                doc_sample = "\n".join(lines[:30]).lower()
                if all(w.lower() in doc_sample for w in words):
                    return full_fn

        # Strategy A: Check lines near email address
        if email:
            for idx, line in enumerate(lines[:25]):
                if email in line:
                    # Check line right above email
                    if idx > 0:
                        candidate = self._clean_name_candidate(lines[idx - 1])
                        if candidate:
                            return candidate
                    # Check line right below email
                    if idx < len(lines) - 1:
                        candidate = self._clean_name_candidate(lines[idx + 1])
                        if candidate:
                            return candidate

        # Strategy B: Check top 25 lines for title-cased or uppercase name line
        for line in lines[:25]:
            candidate = self._clean_name_candidate(line)
            if candidate:
                return candidate

        # Strategy C: Check declaration signature line at end of resume
        for line in reversed(lines[-10:]):
            candidate = self._clean_name_candidate(line)
            if candidate:
                return candidate

        # Strategy D: Check Father's Name pattern (e.g., "Fathers Name : Sahadev Jayram Khot")
        for line in lines:
            if "father" in line.lower() and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    fname_cand = self._clean_name_candidate(parts[1].strip())
                    if fname_cand:
                        return fname_cand

        return None

    @staticmethod
    def _clean_name_candidate(line: str) -> str | None:
        clean = line.strip()
        upper = clean.upper()
        lower = clean.lower()

        # Reject any line containing blocklisted headers or section titles
        if any(hb in upper for hb in _HEADER_BLOCKLIST):
            return None

        if "@" in clean or "http" in clean or "phone" in lower or len(clean) > 40:
            return None

        # Exclude personal metadata lines, job designations, & broken section titles
        non_name_keywords = [
            "status", "single", "married", "gender", "male", "female",
            "nationality", "birth", "date", "address", "career", "experience",
            "education", "skills", "university", "college", "school", "mumbai",
            "contact", "summary", "profile", "objective", "declaration", "father",
            "curriculum", "vitae", "resume", "professi", "experi", "profi", "ski",
            "lls", "ence", "onal", "customer", "service", "executive", "manager",
            "associate", "developer", "engineer", "analyst", "specialist", "lead",
            "officer", "representative", "consultant"
        ]
        if any(kw in lower for kw in non_name_keywords):
            return None

        # Exclude lines starting with digits or numbers
        if re.search(r"\d", clean):
            return None

        words = clean.split()
        if 2 <= len(words) <= 4:
            # Check title casing or standard name structure (at least first word is capitalized)
            if words[0][0].isupper() and all(w.isalpha() or w.startswith(".") for w in words):
                return clean.title()

        return None

    @staticmethod
    def _extract_location(text: str) -> str | None:
        # Pattern 1: "City, State" or "City, ST" format
        pattern1 = re.compile(
            r"\b([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z\s]+))\b"
        )
        match = pattern1.search(text[:1000])
        if match:
            loc = match.group(1).strip()
            # Clean up trailing education / date fragments like "Bhiwandi PASSED IN MARCH"
            loc = re.sub(r"\s+\b(?:PASSED|MARCH|JANUARY|FEBRUARY|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|EDUCATION|HSC|SSC|DEGREE|\d{4})\b.*$", "", loc, flags=re.IGNORECASE).strip()
            if len(loc) > 3:
                return loc

        # Pattern 2: Indian-style "City (E/W/N/S)" or standalone city in header
        pattern2 = re.compile(
            r"\b((?:Mumbai|Delhi|Bangalore|Bengaluru|Hyderabad|Chennai|Kolkata|Pune|Ahmedabad|"
            r"Navi Mumbai|Thane|Ambernath|Kalyan|Dombivli|Vasai|Virar|Panvel|Bhiwandi|Nashik|Nagpur|"
            r"Lucknow|Jaipur|Chandigarh|Indore|Bhopal|Patna|Gurgaon|Gurugram|Noida|Ghaziabad|"
            r"Faridabad|Kochi|Coimbatore|Mysore|Vadodara|Surat|Rajkot|Trivandrum)"
            r"(?:\s*\([EWNS]\))?)\b",
            re.IGNORECASE,
        )
        match = pattern2.search(text[:1000])
        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def _extract_portfolio(text: str, github: str | None, linkedin: str | None) -> str | None:
        matches = _PORTFOLIO_PATTERN.findall(text)
        blocklist = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "protonmail.com", "aol.com",
            "b.com", "m.com", "b.sc", "m.sc", "time.com", "google.com", "example.com", "schema.org"
        }
        for m in matches:
            m_str = m if m.startswith("http") else f"https://{m}"
            if (not github or m_str not in github) and (not linkedin or m_str not in linkedin):
                m_domain = m_str.replace("https://", "").replace("http://", "").split("/")[0].lower()
                if m_domain not in blocklist and not any(sub in m_domain for sub in ["github.com", "linkedin.com", "google.com", "schema.org"]):
                    return m_str
        return None

    def _extract_years_of_experience(self, text: str) -> float:
        """
        Extract total years of experience, handling unicode quotes (e.g. 2 years’ experience)
        and company duration date ranges.
        """
        norm_text = re.sub(r"[’'`]", "'", text)

        # Check explicit patterns
        for pattern in _YOE_PATTERNS:
            match = pattern.search(norm_text)
            if match:
                try:
                    val = float(match.group(1))
                    if 0 < val <= 40:
                        return val
                except ValueError:
                    pass

        # Estimate from date ranges (e.g. 2018 - 2023)
        matches = _DATE_RANGE_PATTERN.findall(norm_text)
        total_months = 0
        for start_year_str, end_year_str in matches:
            try:
                start_y = int(start_year_str)
                end_y = 2026 if end_year_str.lower() in ("present", "current", "now") else int(end_year_str)
                if end_y >= start_y and (end_y - start_y) <= 35:
                    total_months += (end_y - start_y) * 12
            except ValueError:
                continue

        if total_months > 0:
            return round(total_months / 12.0, 1)

        return 0.0

    @staticmethod
    def _extract_company_names(text: str) -> list[str]:
        companies: set[str] = set()

        # Strategy 1: Regex suffix matching (Ltd, Bank, Services, etc.)
        matches = _COMPANY_PATTERNS.findall(text)
        for m in matches:
            clean = m.strip().rstrip(".-,")
            if len(clean) > 3 and not any(hb in clean.upper() for hb in _HEADER_BLOCKLIST):
                if len(clean.split()) <= 8:
                    companies.add(clean)

        # Strategy 2: Positional — lines with date ranges in experience section
        lines = text.split("\n")
        in_experience = False
        for line in lines:
            line_stripped = line.strip()
            upper = line_stripped.upper()
            no_space_upper = re.sub(r"\s+", "", upper)

            # Detect experience section start (immune to space-broken text like "PROFESSI ONAL EXPERI ENCE")
            if any(h in no_space_upper for h in ["WORKEXPERIENCE", "EMPLOYMENTHISTORY", "PROFESSIONALEXPERIENCE", "EXPERIENCE"]):
                in_experience = True
                continue
            # Detect next section (exit experience)
            if in_experience and any(h in no_space_upper for h in ["EDUCATION", "SKILLS", "CERTIFICATIONS", "PROJECTS", "PERSONALDETAILS", "PERSONALPROFILE", "HOBBIES", "INTERESTS"]):
                in_experience = False
                continue

            if in_experience and line_stripped:
                match = _DATE_COMPANY_LINE.match(line_stripped)
                if match:
                    company = match.group(1).strip().rstrip(".-,")
                    # If line is "Role – Company", split on dash to extract company name
                    if any(d in company for d in ["–", "—", " - "]):
                        parts = re.split(r"[-–—]", company)
                        company = parts[-1].strip()
                    if len(company) > 2 and len(company.split()) <= 8:
                        companies.add(company)

                # Strategy 2b: Check for parenthetical company references like
                # "Fullerton India Credit Company (NBFC)"
                paren_match = re.search(
                    r"([A-Z][A-Za-z\s&'-]+(?:Company|Ltd|Bank|Services|Corp|Finance|Insurance|NBFC|LLP))\s*\(",
                    line_stripped,
                )
                if paren_match:
                    companies.add(paren_match.group(1).strip())

                # Strategy 2c: Check for company names followed by date in parentheses or dot
                # e.g., "Altruist Private limited (july 2021 to Present)", "Hexaware BPS.(2018 - 2019)"
                date_paren_match = re.search(
                    r"^([A-Z][A-Za-z0-9\s.,&'-]{3,50})\s*[\(\.]\s*(?:july|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4})",
                    line_stripped,
                    re.IGNORECASE,
                )
                if date_paren_match:
                    companies.add(date_paren_match.group(1).strip())

                # Strategy 2d: Check for role-dash-company pattern (e.g. "AI Engineer Intern – Infinx Jun 2026 – Present")
                dash_company_match = re.search(
                    r"(?:intern|engineer|developer|associate|manager|lead|executive|analyst)\s*[-–—\s]+\s*([A-Z][A-Za-z0-9\s.,&'-]{2,30})\s*(?:[-–—\s\.\d]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present)",
                    line_stripped,
                    re.IGNORECASE,
                )
                if dash_company_match:
                    comp = dash_company_match.group(1).strip()
                    if len(comp) > 2 and comp.lower() not in {"present", "current"}:
                        companies.add(comp)

                # Strategy 2e: Check for "Role at Company" pattern (e.g. "Accounts Receivable at IKS HEALTH")
                at_company_match = re.search(
                    r"\b(?:at|in|with)\s+([A-Z][A-Za-z0-9\s.,&'-]{2,35})\b",
                    line_stripped,
                    re.IGNORECASE,
                )
                if at_company_match:
                    comp = at_company_match.group(1).strip().rstrip(".-,")
                    if len(comp) > 2 and comp.lower() not in {"present", "current"}:
                        companies.add(comp)

                # Also check standalone company name lines (capitalized, no dates)
                elif _STANDALONE_COMPANY_LINE.match(line_stripped) and not line_stripped.startswith("?"):
                    if not any(hb in upper for hb in _HEADER_BLOCKLIST) and len(line_stripped.split()) <= 6:
                        companies.add(line_stripped)

        # Post-processing: clean up extracted company names
        cleaned = set()
        noise_words = {
            "savings account", "credit card", "personal loan", "worked as",
            "handle", "conduct", "assist", "provide", "experience in",
            "executive", "manager", "officer", "associate", "representative", "specialist", "analyst", "developer", "engineer", "lead", "intern",
            "road", "street", "wadi", "marg", "nagar", "manzil", "building", "apartment", "floor", "flat", "district", "pipe", "kurla", "mumbai",
            "backend &", "frontend &", "tools &", "programming", "ai &", "frameworks"
        }
        action_verbs = {"understanding", "offering", "providing", "managing", "resolving", "collaborating", "establishing", "assisting", "handling", "responding", "maintaining", "collecting", "building", "nurturing", "keeping", "contributing", "developing"}

        for c in companies:
            # Strip trailing dot sequences (from "Bank ............")
            c = re.sub(r"\s*\.{2,}.*$", "", c).strip()
            # Strip trailing date fragments (e.g. ". 03 October 2022" or "Jun 2026")
            c = re.sub(r"\s*\.?\s*(?:\d{1,2}\s+)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*(?:\s+\d{4})?.*$", "", c, flags=re.IGNORECASE).strip()
            # Strip trailing year patterns
            c = re.sub(r"\s*\.\s*\d{4}.*$", "", c).strip()
            c = c.rstrip(".-,· ")

            c_lower = c.lower()
            first_word = c_lower.split()[0] if c_lower.split() else ""
            if len(c) > 2 and first_word not in action_verbs and not any(nw in c_lower for nw in noise_words):
                # Ensure it doesn't match known designation patterns or skill category headers
                if not _DESIGNATION_PATTERNS.search(c) and not any(sc in c_lower for sc in ["systems &", "backend &", "tools &"]):
                    cleaned.add(c)

        return sorted(cleaned)[:5]

    @staticmethod
    def _extract_designation(lines: list[str], text: str) -> str | None:
        # Strategy 1: Match known designation patterns in top lines
        for line in lines[:10]:
            match = _DESIGNATION_PATTERNS.search(line)
            if match:
                return match.group(0).strip().title()

        # Strategy 2: Positional — look for role text in the WORK EXPERIENCE section
        # Typically the designation appears as "Working as a <ROLE>" or the bullet after company name
        in_experience = False
        for line in lines:
            upper = line.upper().strip()
            if any(h in upper for h in ["WORK EXPERIENCE", "EMPLOYMENT HISTORY", "PROFESSIONAL EXPERIENCE"]):
                in_experience = True
                continue
            if in_experience and any(h in upper for h in ["EDUCATION", "SKILLS", "CERTIFICATIONS", "PERSONAL DETAILS"]):
                break
            if in_experience:
                # Check for "Working as a <role>" or "Worked as <role>"
                role_match = re.search(
                    r"(?:working|worked|serving|employed)\s+as\s+(?:a\s+|an\s+)?(.+?)(?:\s+(?:in|at|for|since|from|\d))",
                    line,
                    re.IGNORECASE,
                )
                if role_match:
                    return role_match.group(1).strip().title()

                # Also check for formal pattern in full text
                match = _DESIGNATION_PATTERNS.search(line)
                if match:
                    return match.group(0).strip().title()

        # Strategy 3: Fallback to searching full text
        match = _DESIGNATION_PATTERNS.search(text)
        return match.group(0).strip().title() if match else None

    @staticmethod
    def _extract_degree(text: str) -> str | None:
        for degree_name, pattern in _DEGREE_PATTERNS:
            if pattern.search(text):
                return degree_name
        return None

    @staticmethod
    def _extract_jd_required_degree(text: str) -> str | None:
        """
        JD-specific degree extraction that respects 'Minimum' qualifiers.

        Handles patterns like:
            - 'Minimum HSC / 10+2 Equivalent (Any Graduate Preferred)'
            - 'Qualification: Minimum 10+2 or equivalent'
            - 'HSC required; Graduation preferred'
        """
        lower = text.lower()

        # Pattern 1: "Minimum <degree>" — explicit minimum qualifier
        min_patterns = [
            (r"minimum\s+(?:qualification[s]?\s*[:;]?\s*)?(?:hsc|12th|10\+2|higher\s+secondary)", "HSC / 10+2 Equivalent"),
            (r"minimum\s+(?:qualification[s]?\s*[:;]?\s*)?(?:ssc|10th|matriculation)", "SSC / 10th Standard"),
            (r"minimum\s+(?:qualification[s]?\s*[:;]?\s*)?(?:bachelor|b\.?s|b\.?tech|bca|bsc|b\.?com|graduation|graduate)", "Bachelor's"),
            (r"minimum\s+(?:qualification[s]?\s*[:;]?\s*)?(?:master|m\.?s|m\.?tech|mca|msc|mba)", "Master's"),
            (r"minimum\s+(?:qualification[s]?\s*[:;]?\s*)?(?:diploma|associate)", "Associate / Diploma"),
        ]

        for pattern_str, degree_name in min_patterns:
            if re.search(pattern_str, lower):
                return degree_name

        # Pattern 2: "Qualification: HSC" without "minimum" but in a qualification context
        qual_match = re.search(
            r"qualification[s]?\s*[:;]\s*(.{5,80}?)(?:\.|$|\n)",
            lower,
        )
        if qual_match:
            qual_text = qual_match.group(1)
            # Check from lowest to find the actual minimum requirement
            if any(w in qual_text for w in ["hsc", "12th", "10+2", "higher secondary"]):
                return "HSC / 10+2 Equivalent"
            if any(w in qual_text for w in ["ssc", "10th", "matriculation"]):
                return "SSC / 10th Standard"
            if any(w in qual_text for w in ["diploma", "associate"]):
                return "Associate / Diploma"

        # Fallback: use the general degree extractor
        for degree_name, pattern in _DEGREE_PATTERNS:
            if pattern.search(text):
                return degree_name
        return None

    @staticmethod
    def _extract_branch(text: str) -> str | None:
        for branch_name, pattern in _BRANCH_PATTERNS:
            if pattern.search(text):
                return branch_name
        return None

    @staticmethod
    def _extract_domain(text: str) -> str | None:
        for domain_name, pattern in _DOMAIN_PATTERNS:
            if pattern.search(text):
                return domain_name
        return None
