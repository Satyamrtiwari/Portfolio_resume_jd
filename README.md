# 🧠 FatPai — AI Resume–JD Semantic Matching & ATS Engine (v3)

Production-grade FastAPI backend for **ATS keyword analysis**, **entity extraction**, **section-wise semantic matching**, **intelligent dynamic weight strategy engine**, and **structured explainability** using **BAAI/bge-large-en-v1.5** embeddings.

---

## ✨ Enterprise ATS Features

| Feature | Description |
|---|---|
| **Intelligent Weight Strategy** | Supports `AUTO` (dynamic JD requirements analysis), `MANUAL` (custom recruiter override), and `PRESET` modes |
| **Industry Role Presets** | Built-in presets for AI Engineer, Backend, Frontend, Data Science, Healthcare RCM, Finance, Sales, HR |
| **Weight Explainability** | Machine-generated reasoning for every assigned dimension weight percentage |
| **Advanced Entity Extraction** | Candidate Name, Email, Phone, Location, GitHub/LinkedIn/Portfolio links, Total YoE, Highest Degree, Branch, Title |
| **ATS Keyword & Critical Skills** | Coverage ratio %, matched keywords, missing keywords, and Critical (Must-Have) vs Optional (Nice-to-Have) skill gaps |
| **Multi-Dimension Matchers** | Independent matchers for Skills (40%), Experience (YoE delta, tech/domain overlap), Education (Tier & Branch), Projects, and Semantic similarity |
| **Confidence Engine** | Statistical prediction confidence score (0-100%) based on document completeness, entity fidelity, and matcher score variance |
| **Actionable Hiring Decisions** | Executive recommendations (`Highly Recommended`, `Recommended`, `Needs Review`, `Borderline`, `Reject`) with detailed rationale |
| **Production Ready** | CORS, request ID tracing (`X-Request-ID`), processing time headers (`X-Process-Time`), CPU/Memory health metrics, and global error handling |

---

## 🏗️ Architecture & Component Design

```
app/
├── api/
│   ├── dependencies.py           # Dependency Injection singletons
│   └── v1/router.py              # Versioned API routes (/api/v1/match, /api/v1/health)
├── config/
│   ├── settings.py               # Pydantic BaseSettings with .env validation
│   └── logging_config.py         # Structured logging configuration
├── core/
│   ├── exception_handlers.py     # Global error handling (AppException, ValidationError, 500)
│   └── middleware.py             # UUID Request ID & Process Timing headers
├── data/
│   ├── presets/presets.json      # Role weight presets & reasoning
│   └── skills/                   # Externalized skill taxonomy (6 categories, 362+ skills)
├── matchers/                     # Multi-dimensional matching engines
│   ├── base_matcher.py           # Cosine similarity utilities
│   ├── skill_matcher.py          # Categorized skill set intersection
│   ├── experience_matcher.py     # YoE delta, domain alignment & tech overlap
│   ├── education_matcher.py      # Degree tier & branch specialization
│   ├── projects_matcher.py       # Practical portfolio & project alignment
│   └── semantic_matcher.py       # Vector embeddings cosine similarity
├── models/document.py            # Domain dataclasses (CandidateProfile, JDEntity, ParsedDocument)
├── parsers/                      # Section-aware document parsers
│   ├── base_parser.py            # PDF extraction via pypdf
│   ├── resume_parser.py          # Resume heading detection
│   └── jd_parser.py              # JD heading detection
├── schemas/                      # Pydantic v2 schemas
│   ├── request.py                # Input validation
│   └── response.py               # MatchResponse, ATS, Candidate, Health schemas
├── services/                     # Business logic services
│   ├── embedding_service.py      # BAAI/bge-large-en-v1.5 model (loaded ONCE)
│   ├── entity_extraction_service.py # NLP entity & contact extraction
│   ├── ats_service.py            # ATS coverage & critical skills
│   ├── weight_strategy_service.py# Dynamic weight strategy engine
│   ├── confidence_service.py    # Prediction confidence engine
│   ├── recommendation_service.py# Hiring decision recommendation engine
│   ├── preprocessing_service.py  # Casing-preserved cleaning
│   ├── skill_extraction_service.py # Taxonomy regex extraction
│   └── matching_service.py       # Pipeline orchestrator
└── utils/                        # Custom exceptions & formatters
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Installation & Execution

```bash
# Clone the repository
git clone https://github.com/your-username/fatpai-resume-jd.git
cd fatpai-resume-jd

# Install dependencies
uv sync

# Run the backend server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> ⚠️ **First startup** will download the `BAAI/bge-large-en-v1.5` model weights (~1.3 GB). Subsequent startups load from cache in ~3-5 seconds.

### Verify Health Endpoint

```bash
curl http://localhost:8000/api/v1/health
```

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "BAAI/bge-large-en-v1.5",
  "embedding_dimension": 1024,
  "model_size": "1.34 GB",
  "device": "cpu",
  "uptime": "0h 5m 12s",
  "version": "1.0.0",
  "memory_usage_mb": 427.92,
  "cpu_percent": 17.0,
  "cache_status": "active - 362 taxonomy skills & model cached"
}
```

---

## 📡 API Reference

### `POST /api/v1/match`

**Multipart Form Parameters**:
- `resume_file` *(file, optional)*: Resume PDF document
- `resume_text` *(string, optional)*: Resume plain text
- `jd_file` *(file, optional)*: Job description PDF document
- `jd_text` *(string, optional)*: Job description plain text
- `strategy` *(string, default="AUTO")*: Weight strategy: `AUTO`, `MANUAL`, or `PRESET`
- `preset_name` *(string, optional)*: Preset role name (`ai_engineer`, `backend_engineer`, `frontend_engineer`, `data_scientist`, `healthcare_rcm`, `finance`, `sales`, `hr`)
- `manual_weights` *(string, optional)*: JSON string for manual weights (e.g. `'{"skills": 40, "experience": 30, "semantic": 15, "education": 10, "projects": 5}'`)

**Sample Request**:

```bash
curl -X POST http://localhost:8000/api/v1/match \
  -F 'resume_text=Jane Doe\njane@example.com\nSenior Backend Engineer with 5 years experience in Python, FastAPI, Docker, AWS, PostgreSQL, Redis.' \
  -F 'jd_text=Looking for Senior Backend Engineer with 3+ years experience in Python, FastAPI, Docker, Kubernetes, AWS, PostgreSQL.' \
  -F 'strategy=AUTO'
```

**Sample Response**:

```json
{
  "match_score": 77.53,
  "confidence_score": 53.5,
  "match_level": "Strong Match",
  "recommendation": {
    "decision": "Needs Review",
    "summary": "Candidate meets moderate qualification thresholds (77.5%). Further manual evaluation recommended. Missing mandatory skills: google cloud platform, kubernetes."
  },
  "weight_strategy": {
    "strategy_used": "AUTO",
    "preset_applied": null,
    "weights": {
      "skills": 35.0,
      "experience": 35.0,
      "semantic": 15.0,
      "education": 10.0,
      "projects": 5.0
    },
    "reasoning": {
      "skills": "Technical skills drive major evaluation criteria.",
      "experience": "Senior role explicitly requires 5.0+ years of experience.",
      "semantic": "General role domain context match.",
      "education": "Minimum eligibility qualification.",
      "projects": "Projects show practical implementation capability."
    }
  },
  "scores": {
    "overall_score": 77.53,
    "skill_score": 77.8,
    "experience_score": 85.0,
    "education_score": 95.0,
    "projects_score": 70.0,
    "semantic_score": 68.2
  },
  "ats_analysis": {
    "coverage_percentage": 77.8,
    "total_jd_keywords": 9,
    "matched_keywords": ["amazon web services", "django", "docker", "fastapi", "postgresql", "python", "redis"],
    "missing_keywords": ["google cloud platform", "kubernetes"],
    "critical_missing_skills": ["google cloud platform", "kubernetes"],
    "optional_missing_skills": []
  },
  "candidate_profile": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": null,
    "location": null,
    "links": { "github": null, "linkedin": null, "portfolio": null },
    "total_years_experience": 5.0,
    "current_designation": "Senior Backend Engineer",
    "highest_degree": null,
    "degree_branch": null
  },
  "resume_skills": {
    "languages": ["python"],
    "frameworks": ["fastapi", "django"],
    "tools": ["docker"],
    "cloud": ["amazon web services"],
    "databases": ["postgresql", "redis"],
    "ai_ml": []
  },
  "jd_skills": {
    "languages": ["python"],
    "frameworks": ["fastapi"],
    "tools": ["docker", "kubernetes"],
    "cloud": ["amazon web services", "google cloud platform"],
    "databases": ["postgresql", "redis"],
    "ai_ml": []
  },
  "explainability": {
    "matched_skills": ["amazon web services", "django", "docker", "fastapi", "postgresql", "python", "redis"],
    "missing_skills": ["google cloud platform", "kubernetes"],
    "experience_alignment": "Strong",
    "education_alignment": "Strong",
    "recommendation": "Needs Review",
    "summary": "The candidate matches 7 of 9 required skills (78% coverage). Experience sections show strong relevance to the role responsibilities. Key gaps include: google cloud platform, kubernetes. Education alignment is strong."
  },
  "top_matching_sections": [],
  "resume_length": 21,
  "jd_length": 18,
  "processing_time": "3.44 sec"
}
```

---

## 🐳 Docker Deployment

```bash
# Build the production Docker image
docker build -t fatpai-resume-jd .

# Run container exposing port 8000
docker run -p 8000:8000 fatpai-resume-jd
```

---

## ☁️ Deploy to Render

1. Push your repository to GitHub.
2. Log in to [Render](https://render.com) and create a **Web Service**.
3. Point to `render.yaml` or use Blueprint. Render automatically uses the build & start commands configured in `render.yaml`.

---

## 📄 License

MIT License
