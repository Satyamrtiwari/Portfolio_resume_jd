import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertOctagon, XCircle, FileCode, Check, AlertTriangle } from 'lucide-react';
import type { ATSAnalysisSchema } from '../types';

interface ATSCardProps {
  ats: ATSAnalysisSchema;
}

export const ATSCard: React.FC<ATSCardProps> = ({ ats }) => {
  const coverage = ats.coverage_percentage;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 mb-8"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400">
            <FileCode className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-xl text-gray-900 dark:text-white">ATS Keyword Coverage & Skill Gap Analysis</h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Evaluates candidate skill overlap against total required Job Description keywords ({ats.total_jd_keywords} total)
            </p>
          </div>
        </div>

        {/* Coverage Percentage Badge */}
        <div className="flex items-center space-x-3 bg-rose-50/50 dark:bg-white/5 px-4 py-2 rounded-xl border border-rose-200 dark:border-white/10">
          <span className="text-xs text-gray-600 dark:text-gray-400 font-mono uppercase">ATS Coverage:</span>
          {coverage !== null ? (
            <span
              className={`font-mono font-bold text-lg ${
                coverage >= 70
                  ? 'text-emerald-700 dark:text-emerald-400'
                  : coverage >= 40
                  ? 'text-amber-700 dark:text-yellow-400'
                  : 'text-rose-700 dark:text-red-400'
              }`}
            >
              {coverage}%
            </span>
          ) : (
            <span className="text-xs text-yellow-600 dark:text-yellow-400 font-mono">Unstructured JD</span>
          )}
        </div>
      </div>

      {/* Coverage Progress Bar */}
      {coverage !== null && (
        <div className="mb-8">
          <div className="w-full h-3 bg-gray-200 dark:bg-white/10 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-1000 ${
                coverage >= 70
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                  : coverage >= 40
                  ? 'bg-gradient-to-r from-amber-500 to-yellow-400'
                  : 'bg-gradient-to-r from-rose-500 to-red-400'
              }`}
              style={{ width: `${coverage}%` }}
            />
          </div>
        </div>
      )}

      {/* Badges Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Matched Skills (Green) */}
        <div className="p-5 rounded-xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-300 dark:border-emerald-500/30 shadow-sm">
          <div className="flex items-center space-x-2 mb-4">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h4 className="font-heading font-bold text-sm text-emerald-900 dark:text-emerald-300">
              Matched Skills ({ats.matched_keywords.length})
            </h4>
          </div>

          {ats.matched_keywords.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {ats.matched_keywords.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-emerald-100 dark:bg-emerald-500/15 border border-emerald-300 dark:border-emerald-500/30 text-xs font-mono font-bold text-emerald-950 dark:text-emerald-200"
                >
                  <Check className="w-3 h-3 text-emerald-700 dark:text-emerald-400" />
                  <span>{skill}</span>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-500 italic">No direct skill matches found.</p>
          )}
        </div>

        {/* Critical Missing Skills (Orange Warning) */}
        <div className="p-5 rounded-xl bg-amber-50 dark:bg-amber-950/20 border border-amber-300 dark:border-amber-500/30 shadow-sm">
          <div className="flex items-center space-x-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400" />
            <h4 className="font-heading font-bold text-sm text-amber-950 dark:text-amber-300">
              Critical Missing Skills ({ats.critical_missing_skills.length})
            </h4>
          </div>

          {ats.critical_missing_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {ats.critical_missing_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-amber-100 dark:bg-amber-500/15 border border-amber-300 dark:border-amber-500/30 text-xs font-mono font-bold text-amber-950 dark:text-amber-200"
                >
                  <AlertOctagon className="w-3 h-3 text-amber-700 dark:text-amber-400" />
                  <span>{skill}</span>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-500 italic">No critical mandatory skill gaps detected.</p>
          )}
        </div>

        {/* Optional Missing Skills (Red/Gray) */}
        <div className="p-5 rounded-xl bg-rose-50 dark:bg-red-950/20 border border-rose-300 dark:border-red-500/30 shadow-sm">
          <div className="flex items-center space-x-2 mb-4">
            <XCircle className="w-5 h-5 text-rose-600 dark:text-red-400" />
            <h4 className="font-heading font-bold text-sm text-rose-950 dark:text-red-300">
              Optional / Secondary Gaps ({ats.optional_missing_skills.length})
            </h4>
          </div>

          {ats.optional_missing_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {ats.optional_missing_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-rose-100 dark:bg-red-500/10 border border-rose-300 dark:border-red-500/20 text-xs font-mono font-bold text-rose-950 dark:text-red-300"
                >
                  <span>{skill}</span>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-500 italic">No secondary skill gaps.</p>
          )}
        </div>
      </div>
    </motion.div>
  );
};
