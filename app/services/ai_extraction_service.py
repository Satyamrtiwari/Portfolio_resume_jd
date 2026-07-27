"""
AI Extraction Service.

Provides production-grade AI structured entity extraction for candidate resumes
and job descriptions using OpenRouter, Groq, or OpenAI API gateways with strict
Pydantic v2 schema validation.

Production Features:
    - Fully async (non-blocking event loop)
    - Retry with exponential backoff (3 attempts)
    - 12,000 character input limit (supports 3-page senior resumes)
    - max_tokens=2000 for complex JSON responses
"""

from __future__ import annotations

import asyncio
import json
import logging
import re

import httpx
from pydantic import ValidationError

from app.config.settings import get_settings
from app.schemas.extraction import (
    ExtractedCandidateProfileSchema,
    ExtractedJDEntitySchema,
)

logger = logging.getLogger(__name__)

# Maximum characters sent to the LLM (covers ~3 page resumes)
_MAX_INPUT_CHARS = 12_000

# Retry configuration
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds

_RESUME_EXTRACTION_PROMPT = """You are an expert AI Resume Parser for an Enterprise ATS system.
Extract structured candidate profile information from the resume text below.

Return ONLY a valid JSON object following this EXACT schema structure:
{{
  "contact": {{
    "name": "Candidate Full Name (or null if not found)",
    "email": "Candidate Email (or null)",
    "phone": "Candidate Phone (or null)",
    "location": "City, State, Country (or null)",
    "github": "GitHub URL (or null)",
    "linkedin": "LinkedIn URL (or null)",
    "portfolio": "Personal website/portfolio URL (or null, exclude email providers like gmail.com)"
  }},
  "total_years_experience": 0.0,
  "current_designation": "Current or most recent job designation (or null)",
  "highest_degree": "Highest degree (e.g. Master's, Bachelor's, HSC / 10+2 Equivalent, SSC / 10th Standard, Associate / Diploma, or null)",
  "degree_branch": "Branch specialization (e.g. Computer Science, Business / Finance, Information Technology, or null)",
  "company_names": ["List of employer company names worked at (exclude generic phrases like 'the same' or 'experience in')"]
}}

RESUME TEXT:
{text}
"""

_JD_EXTRACTION_PROMPT = """You are an expert AI Job Description Parser for an Enterprise ATS system.
Extract structured job requirement details from the job description text below.

Return ONLY a valid JSON object following this EXACT schema structure:
{{
  "role_title": "Job Title (or null)",
  "department": "Department (or null)",
  "shift": "Shift requirements (or null)",
  "required_years_experience": 0.0,
  "required_degree": "Minimum required degree (e.g. Bachelor's, HSC / 10+2 Equivalent, Master's, or null)",
  "required_branch": "Required branch specialization (or null)",
  "domain_industry": "Target industry domain (e.g. Healthcare RCM, Finance & FinTech, Artificial Intelligence & ML, Cloud Infrastructure & DevOps, or null)"
}}

JOB DESCRIPTION TEXT:
{text}
"""


class AIExtractionService:
    """Enterprise AI Structured Entity Extractor using OpenRouter / Groq / OpenAI."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_key, self.api_url, self.headers, self.default_model = self._configure_gateway()

    def _configure_gateway(self) -> tuple[str | None, str, dict[str, str], str]:
        """Detect available API key and return endpoint configuration."""
        if self.settings.OPENROUTER_API_KEY:
            key = self.settings.OPENROUTER_API_KEY
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {key}",
                "HTTP-Referer": "https://localhost",
                "X-Title": "ATS Resume Matcher",
                "Content-Type": "application/json",
            }
            model = self.settings.LLM_MODEL
            if not model or model.endswith(":free") or "llama-3.3-70b" in model:
                model = "google/gemini-2.5-flash"
            return key, url, headers, model

        if self.settings.GROQ_API_KEY:
            key = self.settings.GROQ_API_KEY
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            }
            model = "llama-3.3-70b-versatile"
            return key, url, headers, model

        if self.settings.OPENAI_API_KEY:
            key = self.settings.OPENAI_API_KEY
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            }
            model = "gpt-4o-mini"
            return key, url, headers, model

        return None, "", {}, ""

    @property
    def is_available(self) -> bool:
        """Returns True if a valid API key is configured."""
        return self.api_key is not None and len(self.api_key.strip()) > 5

    async def _call_llm_with_retry(self, payload: dict) -> dict | None:
        """
        Make an async LLM API call with exponential backoff retry.

        Retries up to _MAX_RETRIES times on transient errors (timeouts, 429, 500+).
        Returns the parsed JSON response dict, or None on permanent failure.
        """
        last_error: Exception | None = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(self.api_url, headers=self.headers, json=payload)
                    resp.raise_for_status()
                    return resp.json()

            except httpx.HTTPStatusError as err:
                last_error = err
                status_code = err.response.status_code
                # Retry on rate limit (429) or server errors (500+)
                if status_code in (429, 500, 502, 503, 504) and attempt < _MAX_RETRIES:
                    delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        "LLM API returned %d (attempt %d/%d). Retrying in %.1fs...",
                        status_code, attempt, _MAX_RETRIES, delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                # Non-retryable HTTP error (401, 402, 404, etc.)
                logger.warning("LLM API returned %d (non-retryable): %s", status_code, err)
                return None

            except (httpx.TimeoutException, httpx.ConnectError) as err:
                last_error = err
                if attempt < _MAX_RETRIES:
                    delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        "LLM API timeout/connection error (attempt %d/%d). Retrying in %.1fs...",
                        attempt, _MAX_RETRIES, delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                logger.warning("LLM API failed after %d attempts: %s", _MAX_RETRIES, err)
                return None

            except Exception as err:
                logger.warning("LLM API unexpected error: %s", err)
                return None

        logger.warning("LLM API exhausted all %d retries. Last error: %s", _MAX_RETRIES, last_error)
        return None

    async def extract_candidate_profile(self, text: str) -> ExtractedCandidateProfileSchema | None:
        """Extract candidate profile using async AI structured parsing with retry."""
        if not self.is_available:
            return None

        prompt = _RESUME_EXTRACTION_PROMPT.format(text=text[:_MAX_INPUT_CHARS])
        payload = {
            "model": self.default_model,
            "messages": [
                {"role": "system", "content": "You are a precise JSON extraction engine. Respond ONLY with raw JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"},
        }

        try:
            data = await self._call_llm_with_retry(payload)
            if data is None:
                return None

            content = data["choices"][0]["message"]["content"]
            clean_json = self._clean_json_str(content)
            json_dict = json.loads(clean_json)
            schema = ExtractedCandidateProfileSchema.model_validate(json_dict)
            logger.info("AI Candidate Extraction successful for model=%s", self.default_model)
            return schema
        except (json.JSONDecodeError, ValidationError, KeyError, IndexError) as err:
            logger.warning("AI Candidate Extraction parse error: %s. Using local fallback.", err)
            return None
        except Exception as err:
            logger.warning("AI Candidate Extraction failed: %s. Using local fallback.", err)
            return None

    async def extract_jd_entity(self, text: str) -> ExtractedJDEntitySchema | None:
        """Extract job description requirements using async AI structured parsing with retry."""
        if not self.is_available:
            return None

        prompt = _JD_EXTRACTION_PROMPT.format(text=text[:_MAX_INPUT_CHARS])
        payload = {
            "model": self.default_model,
            "messages": [
                {"role": "system", "content": "You are a precise JSON extraction engine. Respond ONLY with raw JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"},
        }

        try:
            data = await self._call_llm_with_retry(payload)
            if data is None:
                return None

            content = data["choices"][0]["message"]["content"]
            clean_json = self._clean_json_str(content)
            json_dict = json.loads(clean_json)
            schema = ExtractedJDEntitySchema.model_validate(json_dict)
            logger.info("AI JD Extraction successful for model=%s", self.default_model)
            return schema
        except (json.JSONDecodeError, ValidationError, KeyError, IndexError) as err:
            logger.warning("AI JD Extraction parse error: %s. Using local fallback.", err)
            return None
        except Exception as err:
            logger.warning("AI JD Extraction failed: %s. Using local fallback.", err)
            return None

    @staticmethod
    def _clean_json_str(content: str) -> str:
        """Strips markdown code fence wrappers from LLM responses."""
        c = content.strip()
        if c.startswith("```"):
            c = re.sub(r"^```(?:json)?\s*", "", c)
            c = re.sub(r"\s*```$", "", c)
        return c.strip()
