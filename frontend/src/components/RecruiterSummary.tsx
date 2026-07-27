import React from 'react';
import { motion } from 'framer-motion';
import { Award, CheckCircle2, AlertOctagon, HelpCircle, ArrowRight, UserCheck } from 'lucide-react';
import type { RecruiterSummarySchema, RecommendationSchema } from '../types';

interface RecruiterSummaryProps {
  summary: RecruiterSummarySchema;
  recommendation: RecommendationSchema;
}

export const RecruiterSummary: React.FC<RecruiterSummaryProps> = ({ summary, recommendation }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 mb-8"
    >
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-white/10">
        <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
          <Award className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-heading font-bold text-xl text-white">Recruiter Executive Brief & Action Plan</h3>
          <p className="text-xs text-gray-400">Actionable hiring decision recommendation and risk evaluation</p>
        </div>
      </div>

      {/* Main Executive Summary Banner */}
      <div className="p-5 rounded-xl bg-indigo-950/30 border border-indigo-500/30 mb-8 flex items-start space-x-4">
        <UserCheck className="w-6 h-6 text-indigo-400 mt-1 shrink-0" />
        <div>
          <h4 className="font-heading font-bold text-sm text-indigo-200 mb-1">Executive Summary</h4>
          <p className="text-xs sm:text-sm text-gray-300 leading-relaxed font-normal">
            {summary.overall_recommendation}
          </p>
        </div>
      </div>

      {/* Grid: Strengths vs Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Candidate Strengths */}
        <div className="p-5 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
          <h4 className="font-heading font-bold text-sm text-emerald-300 mb-4 flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Candidate Strengths ({summary.strengths.length})</span>
          </h4>
          <ul className="space-y-2 text-xs text-gray-200">
            {summary.strengths.map((str, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-emerald-400 font-bold">•</span>
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Candidate Weaknesses */}
        <div className="p-5 rounded-xl bg-red-950/20 border border-red-500/30">
          <h4 className="font-heading font-bold text-sm text-red-300 mb-4 flex items-center space-x-2">
            <AlertOctagon className="w-4 h-4 text-red-400" />
            <span>Qualification Gaps / Weaknesses ({summary.weaknesses.length})</span>
          </h4>
          <ul className="space-y-2 text-xs text-gray-200">
            {summary.weaknesses.map((weak, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-red-400 font-bold">•</span>
                <span>{weak}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Interview Actionable Recommendation */}
      <div className="p-5 rounded-xl bg-white/[0.02] border border-white/10 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <HelpCircle className="w-5 h-5 text-indigo-400" />
          <div>
            <span className="text-xs text-gray-400 block">Recommended Recruiter Next Step:</span>
            <span className="font-heading font-bold text-sm text-white">{recommendation.interview_recommendation}</span>
          </div>
        </div>
        <ArrowRight className="w-5 h-5 text-gray-500" />
      </div>
    </motion.div>
  );
};
