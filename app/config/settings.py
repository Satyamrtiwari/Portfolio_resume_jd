"""
Application settings loaded from environment variables.

Uses Pydantic v2 BaseSettings for type-safe configuration with .env file support.
All settings are validated at startup — fail fast on misconfiguration.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from .env file and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── AI Model & LLM ──────────────────────────────────────────────────
    MODEL_NAME: str = "BAAI/bge-large-en-v1.5"
    OPENROUTER_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    LLM_MODEL: str = "google/gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.0

    # ── Application ─────────────────────────────────────────────────────
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # ── File Upload ─────────────────────────────────────────────────────
    MAX_FILE_SIZE: int = 10_485_760  # 10 MB
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx"}

    # ── Scoring Weights (must sum to 1.0) ───────────────────────────────
    SKILL_WEIGHT: float = 0.40
    EXPERIENCE_WEIGHT: float = 0.30
    SEMANTIC_WEIGHT: float = 0.20
    EDUCATION_WEIGHT: float = 0.10

    # ── Paths ───────────────────────────────────────────────────────────
    @property
    def skills_data_dir(self) -> Path:
        """Path to the externalized skill taxonomy JSON files."""
        return Path(__file__).resolve().parent.parent / "data" / "skills"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton Settings instance.

    Using lru_cache ensures the .env file is read only once
    and the same Settings object is reused across the application.
    """
    return Settings()
