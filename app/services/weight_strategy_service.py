"""
Intelligent Weight Strategy Engine.

Supports AUTO (dynamic JD analysis), MANUAL (recruiter override with validation),
and PRESET (industry role presets).

Generates machine-readable reasoning explaining why each weight percentage
was assigned.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.config.settings import get_settings
from app.models.document import (
    JDEntity,
    ParsedDocument,
    PresetType,
    StrategyType,
    WeightConfiguration,
)
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)


class WeightStrategyService:
    """
    Service for determining dynamic weight strategy and dimension allocations.
    """

    def __init__(self) -> None:
        self._presets: dict[str, dict] = {}
        self._load_presets()

    def _load_presets(self) -> None:
        settings = get_settings()
        preset_file = Path(settings.skills_data_dir).parent / "presets" / "presets.json"

        if preset_file.exists():
            try:
                with open(preset_file, encoding="utf-8") as f:
                    self._presets = json.load(f)
                logger.info("Loaded %d preset configurations.", len(self._presets))
            except Exception as exc:
                logger.error("Failed to load presets file: %s", exc)

    def resolve_weights(
        self,
        strategy: StrategyType = StrategyType.AUTO,
        preset_name: PresetType | str | None = None,
        manual_weights_json: str | None = None,
        jd_doc: ParsedDocument | None = None,
        jd_entity: JDEntity | None = None,
    ) -> tuple[WeightConfiguration, str, str | None]:
        """
        Resolve the active weight configuration.

        Args:
            strategy: StrategyType (AUTO, MANUAL, PRESET)
            preset_name: Role preset name if PRESET
            manual_weights_json: JSON string if MANUAL
            jd_doc: Parsed JD document if AUTO
            jd_entity: Extracted JD entities if AUTO

        Returns:
            Tuple of (WeightConfiguration, strategy_used_name, preset_applied_name)
        """
        if strategy == StrategyType.MANUAL and manual_weights_json:
            weights = self._validate_and_build_manual(manual_weights_json)
            return weights, StrategyType.MANUAL.value, None

        if strategy == StrategyType.PRESET and preset_name:
            preset_str = preset_name.value if isinstance(preset_name, PresetType) else str(preset_name)
            weights = self._get_preset(preset_str)
            return weights, StrategyType.PRESET.value, preset_str

        # Default to AUTO analysis
        if jd_doc is not None:
            weights = self._auto_analyze_jd(jd_doc, jd_entity)
            return weights, StrategyType.AUTO.value, None

        # Ultimate fallback to standard settings
        settings = get_settings()
        weights = WeightConfiguration(
            skills=settings.SKILL_WEIGHT * 100.0,
            experience=settings.EXPERIENCE_WEIGHT * 100.0,
            semantic=settings.SEMANTIC_WEIGHT * 100.0,
            education=settings.EDUCATION_WEIGHT * 100.0,
            projects=5.0,
            reasoning={
                "skills": "Default allocation based on platform baseline settings.",
                "experience": "Default allocation based on platform baseline settings.",
                "semantic": "Default allocation based on platform baseline settings.",
                "education": "Default allocation based on platform baseline settings.",
                "projects": "Default allocation for project portfolio.",
            },
        )
        return weights, StrategyType.AUTO.value, None

    def _auto_analyze_jd(
        self,
        jd_doc: ParsedDocument,
        jd_entity: JDEntity | None,
    ) -> WeightConfiguration:
        """
        Dynamically calculate optimal weights by inspecting JD requirements.
        """
        text = jd_doc.cleaned_text.lower()

        w_skills = 40.0
        w_exp = 30.0
        w_sem = 15.0
        w_edu = 10.0
        w_proj = 5.0

        r_skills = "Technical skills drive major evaluation criteria."
        r_exp = "Standard experience requirements."
        r_sem = "General role domain context match."
        r_edu = "Minimum eligibility qualification."
        r_proj = "Projects show practical implementation capability."

        # 1. Experience Check
        yoe = jd_entity.required_years_experience if jd_entity else 0.0
        if yoe >= 5.0:
            w_exp += 10.0
            w_skills -= 5.0
            w_sem -= 5.0
            r_exp = f"Senior role explicitly requires {yoe}+ years of experience."
        elif yoe >= 2.0:
            w_exp += 5.0
            w_skills -= 5.0
            r_exp = f"Role requires {yoe}+ years of prior experience."

        # 2. Domain / Industry Check
        domain = jd_entity.domain_industry if jd_entity else None
        if domain == "Healthcare RCM":
            w_skills = 45.0
            w_exp = 35.0
            w_sem = 15.0
            w_edu = 5.0
            w_proj = 0.0
            r_skills = "Healthcare RCM requires strict domain medical billing & coding skills."
            r_exp = "RCM domain experience is critical for compliance and billing accuracy."
            r_edu = "Education acts only as baseline administrative eligibility."
        elif domain == "Artificial Intelligence & ML":
            w_skills = 40.0
            w_exp = 25.0
            w_sem = 15.0
            w_edu = 10.0
            w_proj = 10.0
            r_skills = "AI/ML role relies heavily on PyTorch/LLM framework mastery."
            r_proj = "Practical AI/ML personal and open-source projects are strongly emphasized."

        # 3. Education Check
        if "phd" in text or "doctorate" in text or "master" in text:
            w_edu = 15.0
            w_sem = max(5.0, w_sem - 5.0)
            r_edu = "Role explicitly specifies advanced degree (Master's/Ph.D.) qualifications."

        # Normalize to ensure sum == 100.0
        total = w_skills + w_exp + w_sem + w_edu + w_proj
        if total > 0:
            w_skills = (w_skills / total) * 100.0
            w_exp = (w_exp / total) * 100.0
            w_sem = (w_sem / total) * 100.0
            w_edu = (w_edu / total) * 100.0
            w_proj = (w_proj / total) * 100.0

        reasoning = {
            "skills": r_skills,
            "experience": r_exp,
            "semantic": r_sem,
            "education": r_edu,
            "projects": r_proj,
        }

        return WeightConfiguration(
            skills=round(w_skills, 2),
            experience=round(w_exp, 2),
            semantic=round(w_sem, 2),
            education=round(w_edu, 2),
            projects=round(w_proj, 2),
            reasoning=reasoning,
        )

    def _get_preset(self, preset_name: str) -> WeightConfiguration:
        preset_key = preset_name.lower().strip()
        data = self._presets.get(preset_key)

        if not data:
            # Fallback to general software engineer preset
            data = self._presets.get("general_software_engineer", {
                "skills": 40.0, "experience": 30.0, "semantic": 20.0, "education": 10.0, "projects": 0.0,
                "reasoning": {"skills": "Standard preset."}
            })

        return WeightConfiguration(
            skills=data["skills"],
            experience=data["experience"],
            semantic=data["semantic"],
            education=data["education"],
            projects=data.get("projects", 0.0),
            reasoning=data.get("reasoning", {}),
        )

    def _validate_and_build_manual(self, manual_json: str) -> WeightConfiguration:
        try:
            parsed = json.loads(manual_json)
        except Exception as exc:
            raise AppException(f"Invalid JSON format for manual_weights: {exc}", status_code=400) from exc

        skills = float(parsed.get("skills", 0))
        experience = float(parsed.get("experience", 0))
        semantic = float(parsed.get("semantic", 0))
        education = float(parsed.get("education", 0))
        projects = float(parsed.get("projects", 0))

        if any(w < 0 for w in [skills, experience, semantic, education, projects]):
            raise AppException("Manual weights must all be non-negative (>= 0).", status_code=400)

        total = skills + experience + semantic + education + projects

        # Handle 0-1.0 scale vs 0-100 scale
        if total <= 1.05 and total >= 0.95:
            skills *= 100.0
            experience *= 100.0
            semantic *= 100.0
            education *= 100.0
            projects *= 100.0
            total = 100.0

        if abs(total - 100.0) > 1.0:
            raise AppException(f"Manual weights must sum to 100% (or 1.0). Current sum: {total:.1f}%", status_code=400)

        reasoning = {
            "skills": "Recruiter manual weight override.",
            "experience": "Recruiter manual weight override.",
            "semantic": "Recruiter manual weight override.",
            "education": "Recruiter manual weight override.",
            "projects": "Recruiter manual weight override.",
        }

        return WeightConfiguration(
            skills=round(skills, 2),
            experience=round(experience, 2),
            semantic=round(semantic, 2),
            education=round(education, 2),
            projects=round(projects, 2),
            reasoning=reasoning,
        )
