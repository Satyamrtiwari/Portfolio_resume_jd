"""
Matching service — the pipeline orchestrator (v3 ATS Platform).

Coordinates all services and matchers to produce the final MatchResponse.

Pipeline:
    1. Extract text (PDF or plaintext)
    2. Clean text via PreprocessingService
    3. Parse sections via ResumeParser / JDParser
    4. Extract structured entities via EntityExtractionService
    5. Resolve dynamic weights via WeightStrategyService (AUTO / MANUAL / PRESET)
    6. Extract skills via SkillExtractionService
    7. Perform ATS keyword coverage analysis via ATSService
    8. Generate vector embeddings via EmbeddingService
    9. Execute Matchers (Skill, Experience, Education, Projects, Semantic)
    10. Compute weighted hybrid score (with dynamic Project N/A weight redistribution)
    11. Calculate prediction confidence via ConfidenceService
    12. Generate hiring decision via RecommendationService
    13. Build explainability & return v3 MatchResponse
"""

from __future__ import annotations

import asyncio
import logging
import time

from fastapi import UploadFile

from app.matchers.education_matcher import EducationMatcher
from app.matchers.experience_matcher import ExperienceMatcher
from app.matchers.projects_matcher import ProjectsMatcher
from app.matchers.semantic_matcher import SemanticMatcher
from app.matchers.skill_matcher import SkillMatcher
from app.models.document import (
    InputSource,
    ParsedDocument,
    PresetType,
    StrategyType,
)
from app.parsers.jd_parser import JDParser
from app.parsers.resume_parser import ResumeParser
from app.schemas.response import (
    CandidateLinksSchema,
    CandidateProfileSchema,
    Explainability,
    MatchResponse,
    RecommendationSchema,
    RecruiterSummarySchema,
    ScoreBreakdown,
    SectionMatch,
    SkillsDetail,
    WeightStrategyDetailSchema,
)
from app.services.ats_service import ATSService
from app.services.confidence_service import ConfidenceService
from app.services.embedding_service import EmbeddingService
from app.services.entity_extraction_service import EntityExtractionService
from app.services.preprocessing_service import PreprocessingService
from app.services.recommendation_service import RecommendationService
from app.services.skill_extraction_service import SkillExtractionService
from app.services.weight_strategy_service import WeightStrategyService
from app.utils.exceptions import EmptyDocumentError
from app.utils.helpers import (
    calculate_alignment_label,
    calculate_match_level,
    format_processing_time,
    generate_explainability_summary,
)

logger = logging.getLogger(__name__)


class MatchingService:
    """
    Orchestrates the full v3 ATS resume-JD matching pipeline.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        preprocessing_service: PreprocessingService,
        skill_extraction_service: SkillExtractionService,
    ) -> None:
        self._embedding = embedding_service
        self._preprocessing = preprocessing_service
        self._skill_extraction = skill_extraction_service

        # Additional ATS Services
        self._entity_extraction = EntityExtractionService()
        self._ats_service = ATSService(skill_extraction_service)
        self._weight_strategy_service = WeightStrategyService()
        self._confidence_service = ConfidenceService()
        self._recommendation_service = RecommendationService()

        # Parsers
        self._resume_parser = ResumeParser()
        self._jd_parser = JDParser()

        # Matchers
        self._skill_matcher = SkillMatcher()
        self._experience_matcher = ExperienceMatcher()
        self._education_matcher = EducationMatcher()
        self._projects_matcher = ProjectsMatcher()
        self._semantic_matcher = SemanticMatcher()

    async def match(
        self,
        resume_file: UploadFile | None = None,
        resume_text: str | None = None,
        jd_file: UploadFile | None = None,
        jd_text: str | None = None,
        strategy: StrategyType = StrategyType.AUTO,
        preset_name: PresetType | str | None = None,
        manual_weights_json: str | None = None,
        resume_filename: str | None = None,
        jd_filename: str | None = None,
    ) -> MatchResponse:
        """
        Execute the full v3 matching pipeline.
        """
        start_time = time.perf_counter()

        # ── Step 1: Extract raw text ────────────────────────────────
        resume_raw, resume_source = await self._extract_text(
            resume_file, resume_text, "resume"
        )
        jd_raw, jd_source = await self._extract_text(
            jd_file, jd_text, "job description"
        )

        # ── Step 2: Preprocess ──────────────────────────────────────
        resume_clean = self._preprocessing.clean_text(resume_raw)
        jd_clean = self._preprocessing.clean_text(jd_raw)

        if not resume_clean:
            raise EmptyDocumentError("Resume contains no extractable text after cleaning.")
        if not jd_clean:
            raise EmptyDocumentError("Job description contains no extractable text after cleaning.")

        # ── Step 3: Parse sections ──────────────────────────────────
        resume_doc = self._resume_parser.parse(resume_clean, resume_source)
        jd_doc = self._jd_parser.parse(jd_clean, jd_source)

        resume_doc.cleaned_text = resume_clean
        jd_doc.cleaned_text = jd_clean
        resume_doc.filename = resume_file.filename if resume_file and resume_file.filename else resume_filename
        jd_doc.filename = jd_file.filename if jd_file and jd_file.filename else jd_filename

        # ── Step 4: Extract entities (Async Concurrent) ─────────────
        candidate_profile, jd_entity = await asyncio.gather(
            self._entity_extraction.extract_candidate_profile(resume_doc),
            self._entity_extraction.extract_jd_entity(jd_doc),
        )

        resume_doc.candidate_profile = candidate_profile
        jd_doc.jd_entity = jd_entity

        # ── Step 5: Resolve dynamic weights ────────────────────────
        weight_config, strat_name, preset_applied = self._weight_strategy_service.resolve_weights(
            strategy=strategy,
            preset_name=preset_name,
            manual_weights_json=manual_weights_json,
            jd_doc=jd_doc,
            jd_entity=jd_entity,
        )

        # ── Step 6: Extract skills ──────────────────────────────────
        resume_skills = self._skill_extraction.extract_skills(resume_clean)
        jd_skills = self._skill_extraction.extract_skills(jd_clean)

        # Populate mandatory/preferred skill sets on jd_entity
        jd_entity.mandatory_skills = jd_skills.all_skills()

        # ── Step 7: Match Skills & ATS Keyword Coverage ─────────────
        # Match skills first (with synonym expansion) so ATS analysis doesn't double-penalize
        matched_skills = self._skill_matcher.get_matched_skills(resume_skills, jd_skills)
        missing_skills = self._skill_matcher.get_missing_skills(resume_skills, jd_skills)

        ats_analysis = self._ats_service.analyze_coverage(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            jd_doc=jd_doc,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
        )

        # ── Step 8: Generate vector embeddings ──────────────────────
        self._generate_embeddings(resume_doc, jd_doc)

        # ── Step 9: Execute Matchers ─────────────────────────────────
        skill_score = self._skill_matcher.score(resume_skills, jd_skills)
        experience_score = self._experience_matcher.score(
            resume_doc, jd_doc, candidate_profile, jd_entity, resume_skills, jd_skills
        )
        education_score = self._education_matcher.score(
            resume_doc, jd_doc, candidate_profile, jd_entity
        )
        projects_score = self._projects_matcher.score(
            resume_doc, jd_doc, resume_skills, jd_skills
        )
        semantic_score = self._semantic_matcher.score(resume_doc, jd_doc)

        exp_explainability = self._experience_matcher.generate_explainability(
            resume_doc, jd_doc, candidate_profile, jd_entity, resume_skills, jd_skills
        )
        edu_breakdown = self._education_matcher.generate_education_breakdown(
            candidate_profile, jd_entity
        )

        # ── Step 10: Compute Weighted Overall Score ────────────────
        w_skills = weight_config.skills
        w_exp = weight_config.experience
        w_edu = weight_config.education
        w_proj = weight_config.projects
        w_sem = weight_config.semantic

        # If Projects is N/A (None), redistribute project weight proportionally to remaining dimensions
        if projects_score is None:
            w_proj = 0.0
            total_remaining = w_skills + w_exp + w_edu + w_sem
            if total_remaining > 0:
                scale = 100.0 / total_remaining
                w_skills *= scale
                w_exp *= scale
                w_edu *= scale
                w_sem *= scale

        raw_overall = (
            ((w_skills / 100.0) * skill_score)
            + ((w_exp / 100.0) * experience_score)
            + ((w_edu / 100.0) * education_score)
            + (((w_proj / 100.0) * projects_score) if projects_score is not None else 0.0)
            + ((w_sem / 100.0) * semantic_score)
        )

        # Continuous Skill Coverage Multiplier (Gating for low-skill candidates)
        total_jd_skills = len(ats_analysis.critical_missing_skills) + len(ats_analysis.matched_keywords)
        if total_jd_skills > 0:
            coverage_ratio = len(ats_analysis.matched_keywords) / float(total_jd_skills)
            if coverage_ratio >= 0.70:
                coverage_multiplier = 1.0
            else:
                coverage_multiplier = 0.25 + (0.75 * (coverage_ratio / 0.70))
            raw_overall *= coverage_multiplier

        overall_score = round(min(max(raw_overall, 0.0), 100.0), 2)

        score_breakdown = ScoreBreakdown(
            overall_score=overall_score,
            skill_score=round(skill_score, 2),
            experience_score=round(experience_score, 2),
            education_score=round(education_score, 2),
            projects_score=round(projects_score, 2) if projects_score is not None else None,
            semantic_score=round(semantic_score, 2),
            experience_explainability=exp_explainability,
        )

        # ── Step 11: Prediction Confidence ─────────────────────────
        confidence = self._confidence_service.calculate_confidence(
            resume_doc, jd_doc, candidate_profile, score_breakdown
        )

        # ── Step 12: Recommendation Engine ──────────────────────────
        recommendation = self._recommendation_service.generate_recommendation(
            scores=score_breakdown,
            ats_analysis=ats_analysis,
            candidate_yoe=candidate_profile.total_years_experience,
            required_yoe=jd_entity.required_years_experience,
            resume_text=resume_clean,
            jd_domain=jd_entity.domain_industry,
        )

        recruiter_summary = RecruiterSummarySchema(
            strengths=recommendation.strengths,
            weaknesses=recommendation.weaknesses,
            critical_missing_skills=ats_analysis.critical_missing_skills,
            overall_recommendation=recommendation.summary,
        )

        # ── Step 13: Build Response ──────────────────────────────────
        matched_skills = self._skill_matcher.get_matched_skills(resume_skills, jd_skills)
        missing_skills = self._skill_matcher.get_missing_skills(resume_skills, jd_skills)

        if candidate_profile.total_years_experience == 0.0 and not candidate_profile.company_names:
            experience_alignment = "Poor"
        else:
            experience_alignment = calculate_alignment_label(experience_score)

        education_alignment = calculate_alignment_label(education_score)

        top_sections = self._semantic_matcher.find_top_matching_sections(
            resume_doc, jd_doc, top_n=5
        )

        summary = generate_explainability_summary(
            overall_score=overall_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_alignment=experience_alignment,
            education_alignment=education_alignment,
            resume_length=resume_doc.word_count,
            jd_length=jd_doc.word_count,
        )

        elapsed = time.perf_counter() - start_time

        cand_schema = CandidateProfileSchema(
            name=candidate_profile.name,
            email=candidate_profile.email,
            phone=candidate_profile.phone,
            location=candidate_profile.location,
            links=CandidateLinksSchema(
                github=candidate_profile.links.github,
                linkedin=candidate_profile.links.linkedin,
                portfolio=candidate_profile.links.portfolio,
            ),
            total_years_experience=candidate_profile.total_years_experience,
            current_designation=candidate_profile.current_designation,
            highest_degree=candidate_profile.highest_degree,
            degree_branch=candidate_profile.degree_branch,
            company_names=candidate_profile.company_names,
        )

        active_weights_dict = weight_config.to_dict()
        if projects_score is None:
            active_weights_dict["projects"] = 0.0

        weight_strat_schema = WeightStrategyDetailSchema(
            strategy_used=strat_name,
            preset_applied=preset_applied,
            weights=active_weights_dict,
            reasoning=weight_config.reasoning,
        )

        response = MatchResponse(
            match_score=overall_score,
            confidence=confidence,
            match_level=calculate_match_level(overall_score),
            recommendation=recommendation,
            recruiter_summary=recruiter_summary,
            weight_strategy=weight_strat_schema,
            scores=score_breakdown,
            education_breakdown=edu_breakdown,
            ats_analysis=ats_analysis,
            candidate_profile=cand_schema,
            resume_skills=SkillsDetail(
                languages=resume_skills.languages,
                frameworks=resume_skills.frameworks,
                tools=resume_skills.tools,
                cloud=resume_skills.cloud,
                databases=resume_skills.databases,
                ai_ml=resume_skills.ai_ml,
            ),
            jd_skills=SkillsDetail(
                languages=jd_skills.languages,
                frameworks=jd_skills.frameworks,
                tools=jd_skills.tools,
                cloud=jd_skills.cloud,
                databases=jd_skills.databases,
                ai_ml=jd_skills.ai_ml,
            ),
            explainability=Explainability(
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                experience_alignment=experience_alignment,
                education_alignment=education_alignment,
                recommendation=recommendation.decision,
                summary=summary,
            ),
            top_matching_sections=[SectionMatch(**s) for s in top_sections],
            resume_length=resume_doc.word_count,
            jd_length=jd_doc.word_count,
            processing_time=format_processing_time(elapsed),
        )

        logger.info(
            "Match completed: score=%.2f, confidence=%.1f%%, rec=%s, strategy=%s, time=%s",
            overall_score,
            confidence.score,
            recommendation.decision,
            strat_name,
            response.processing_time,
        )
        return response

    async def _extract_text(
        self,
        file: UploadFile | None,
        text: str | None,
        doc_label: str,
    ) -> tuple[str, InputSource]:
        if file is not None and file.filename:
            logger.info("Processing %s from PDF upload: %s", doc_label, file.filename)
            raw_text = await self._resume_parser.read_upload(file)
            return raw_text, InputSource.PDF

        if text is not None and text.strip():
            logger.info("Processing %s from plain text (%d chars).", doc_label, len(text))
            return text.strip(), InputSource.TEXT

        raise EmptyDocumentError(
            f"No {doc_label} provided. Please upload a PDF or paste text."
        )

    def _generate_embeddings(
        self,
        resume_doc: ParsedDocument,
        jd_doc: ParsedDocument,
    ) -> None:
        resume_doc.embedding = self._embedding.encode(resume_doc.cleaned_text)
        jd_doc.embedding = self._embedding.encode(jd_doc.cleaned_text)

        all_sections = []
        section_refs = []

        for doc in (resume_doc, jd_doc):
            for key, section in doc.sections.items():
                if section.content.strip():
                    all_sections.append(section.content)
                    section_refs.append(section)

        if all_sections:
            embeddings = self._embedding.encode_batch(all_sections)
            for section, embedding in zip(section_refs, embeddings):
                section.embedding = embedding
