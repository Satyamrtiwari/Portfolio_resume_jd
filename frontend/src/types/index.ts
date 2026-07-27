export type StrategyType = 'AUTO' | 'MANUAL' | 'PRESET';

export type PresetType =
  | 'ai_engineer'
  | 'backend_engineer'
  | 'frontend_engineer'
  | 'full_stack'
  | 'devops'
  | 'data_scientist'
  | 'healthcare_rcm'
  | 'finance'
  | 'sales'
  | 'hr'
  | 'general_software_engineer';

export interface CandidateLinksSchema {
  github: string | null;
  linkedin: string | null;
  portfolio: string | null;
}

export interface CandidateProfileSchema {
  name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  links: CandidateLinksSchema;
  total_years_experience: number;
  current_designation: string | null;
  highest_degree: string | null;
  degree_branch: string | null;
  company_names: string[];
}

export interface SkillsDetail {
  languages: string[];
  frameworks: string[];
  tools: string[];
  cloud: string[];
  databases: string[];
  ai_ml: string[];
}

export interface RecommendationSchema {
  decision: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  hiring_risk: string;
  interview_recommendation: string;
}

export interface RecruiterSummarySchema {
  strengths: string[];
  weaknesses: string[];
  critical_missing_skills: string[];
  overall_recommendation: string;
}

export interface WeightStrategyDetailSchema {
  strategy_used: string;
  preset_applied: string | null;
  weights: Record<string, number>;
  reasoning: Record<string, string>;
}

export interface ScoreBreakdown {
  overall_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  projects_score: number | null;
  semantic_score: number;
  experience_explainability: string[];
}

export interface EducationBreakdownSchema {
  highest_qualification: string;
  minimum_required: string;
  status: string;
}

export interface ATSAnalysisSchema {
  coverage_percentage: number | null;
  coverage_status: string;
  total_jd_keywords: number;
  matched_keywords: string[];
  missing_keywords: string[];
  critical_missing_skills: string[];
  optional_missing_skills: string[];
}

export interface Explainability {
  matched_skills: string[];
  missing_skills: string[];
  experience_alignment: string;
  education_alignment: string;
  recommendation: string;
  summary: string;
}

export interface SectionMatch {
  resume_section: string;
  jd_section: string;
  similarity: number;
}

export interface ConfidenceSchema {
  score: number;
  reasons: string[];
}

export interface MatchResponse {
  match_score: number;
  confidence: ConfidenceSchema;
  match_level: string;
  recommendation: RecommendationSchema;
  recruiter_summary: RecruiterSummarySchema;
  weight_strategy: WeightStrategyDetailSchema;
  scores: ScoreBreakdown;
  education_breakdown: EducationBreakdownSchema;
  ats_analysis: ATSAnalysisSchema;
  candidate_profile: CandidateProfileSchema;
  resume_skills: SkillsDetail;
  jd_skills: SkillsDetail;
  explainability: Explainability;
  top_matching_sections: SectionMatch[];
  resume_length: number;
  jd_length: number;
  processing_time: string;
}
