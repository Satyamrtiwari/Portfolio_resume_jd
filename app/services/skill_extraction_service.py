"""
Skill extraction service.

Replaces KeyBERT with a curated taxonomy + pattern matching approach.
Zero additional model loads, sub-millisecond execution, and structured
categorized output.

Taxonomy JSON files are loaded once at initialization from:
    app/data/skills/{category}.json
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from app.config.settings import get_settings
from app.models.document import SkillSet

logger = logging.getLogger(__name__)

# ── Skill name aliases for normalization ────────────────────────────────

_SKILL_ALIASES: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "rb": "ruby",
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "tf": "terraform",
    "gcp": "google cloud platform",
    "aws": "amazon web services",
    "dl": "deep learning",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "cv": "computer vision",
    "react.js": "react",
    "reactjs": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "node.js": "node",
    "nodejs": "node",
    "next.js": "nextjs",
    "nest.js": "nestjs",
    "express.js": "express",
    "sklearn": "scikit-learn",
    "mssql": "sql server",
    "cpp": "c++",
    "csharp": "c#",
    "golang": "go",
}


class SkillExtractionService:
    """
    Extracts and categorizes technical skills from document text.

    Uses an externalized taxonomy of known skills loaded from JSON files.
    Skills are matched via word-boundary regex for accuracy.
    No additional ML model is loaded.

    Attributes:
        _taxonomy: Dictionary mapping category names to sets of skill patterns.
        _compiled_patterns: Pre-compiled regex patterns per category for performance.
    """

    def __init__(self) -> None:
        """Load the skill taxonomy from JSON files at initialization."""
        self._taxonomy: dict[str, set[str]] = {}
        self._compiled_patterns: dict[str, list[tuple[str, re.Pattern[str]]]] = {}
        self._load_taxonomy()

    def _load_taxonomy(self) -> None:
        """
        Load all skill taxonomy JSON files from the data directory.

        Each JSON file should be a flat list of skill strings.
        Files are named by category: languages.json, frameworks.json, etc.
        """
        settings = get_settings()
        skills_dir = settings.skills_data_dir

        if not skills_dir.exists():
            logger.error("Skills data directory not found: %s", skills_dir)
            return

        categories = [
            "languages",
            "frameworks",
            "tools",
            "cloud",
            "databases",
            "ai_ml",
        ]

        for category in categories:
            file_path = skills_dir / f"{category}.json"

            if not file_path.exists():
                logger.warning("Taxonomy file not found: %s", file_path)
                self._taxonomy[category] = set()
                self._compiled_patterns[category] = []
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    skills_list: list[str] = json.load(f)

                self._taxonomy[category] = {s.lower() for s in skills_list}

                sorted_skills = sorted(skills_list, key=len, reverse=True)
                compiled = []
                for skill in sorted_skills:
                    s_lower = skill.lower()
                    escaped = re.escape(s_lower)
                    # Handle word boundary: if skill ends with non-word char (e.g. c++, c#), use (?!\w)
                    right_boundary = r"(?!\w)" if not s_lower[-1].isalnum() else r"\b"
                    left_boundary = r"(?<!\w)" if not s_lower[0].isalnum() else r"\b"
                    pattern = re.compile(left_boundary + escaped + right_boundary, re.IGNORECASE)
                    compiled.append((s_lower, pattern))
                self._compiled_patterns[category] = compiled

                logger.info(
                    "Loaded %d skills for category '%s'.",
                    len(skills_list),
                    category,
                )

            except (json.JSONDecodeError, OSError) as exc:
                logger.error(
                    "Failed to load taxonomy file %s: %s",
                    file_path,
                    exc,
                )
                self._taxonomy[category] = set()
                self._compiled_patterns[category] = []

        total = sum(len(v) for v in self._taxonomy.values())
        logger.info("Skill taxonomy loaded: %d skills across %d categories.", total, len(categories))

    def extract_skills(self, text: str) -> SkillSet:
        """
        Extract categorized skills from document text.

        Scans the text for known skills using word-boundary regex matching.
        Deduplication is handled via sets.

        Args:
            text: Document text to scan (original casing OK, matching is case-insensitive).

        Returns:
            A SkillSet with categorized skill lists.
        """
        extracted: dict[str, list[str]] = {
            cat: [] for cat in self._compiled_patterns
        }

        for category, patterns in self._compiled_patterns.items():
            seen: set[str] = set()
            for skill_name, pattern in patterns:
                if skill_name not in seen and pattern.search(text):
                    normalized = self.normalize_skill(skill_name)
                    if normalized not in seen:
                        extracted[category].append(normalized)
                        seen.add(normalized)

        skill_set = SkillSet(
            languages=extracted.get("languages", []),
            frameworks=extracted.get("frameworks", []),
            tools=extracted.get("tools", []),
            cloud=extracted.get("cloud", []),
            databases=extracted.get("databases", []),
            ai_ml=extracted.get("ai_ml", []),
        )

        logger.debug(
            "Extracted %d total skills: %s",
            len(skill_set.all_skills()),
            skill_set.all_skills(),
        )
        return skill_set

    @staticmethod
    def normalize_skill(skill: str) -> str:
        """
        Normalize a skill name to its canonical form.

        Applies alias mapping and lowercasing.

        Args:
            skill: Raw skill name.

        Returns:
            Normalized skill name.
        """
        lower = skill.lower().strip()
        return _SKILL_ALIASES.get(lower, lower)

    @staticmethod
    def find_matched_skills(
        resume_skills: SkillSet,
        jd_skills: SkillSet,
    ) -> list[str]:
        """
        Find skills present in both resume and JD.

        Args:
            resume_skills: Skills extracted from the resume.
            jd_skills: Skills extracted from the JD.

        Returns:
            Sorted list of matched skill names.
        """
        matched = resume_skills.all_skills() & jd_skills.all_skills()
        return sorted(matched)

    @staticmethod
    def find_missing_skills(
        resume_skills: SkillSet,
        jd_skills: SkillSet,
    ) -> list[str]:
        """
        Find skills in the JD that are missing from the resume.

        Args:
            resume_skills: Skills extracted from the resume.
            jd_skills: Skills extracted from the JD.

        Returns:
            Sorted list of missing skill names.
        """
        missing = jd_skills.all_skills() - resume_skills.all_skills()
        return sorted(missing)
