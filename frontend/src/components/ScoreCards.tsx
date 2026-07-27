import React from 'react';
import { motion } from 'framer-motion';
import { Award, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import type { MatchResponse } from '../types';

interface ScoreCardsProps {
  data: MatchResponse;
}

export const ScoreCards: React.FC<ScoreCardsProps> = ({ data }) => {
  const score = data.match_score;
  const confidence = data.confidence.score;
  const decision = data.recommendation.decision;
  const hiringRisk = data.recommendation.hiring_risk;

  // Decision badge colors
  const getDecisionBadge = () => {
    switch (decision) {
      case 'Highly Recommended':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'Recommended':
        return 'bg-teal-500/20 text-teal-300 border-teal-500/40';
      case 'Needs Review':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40';
      case 'Borderline':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      default:
        return 'bg-red-500/20 text-red-300 border-red-500/40';
    }
  };

  // Circular progress calculations
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="space-y-8 mb-12">
      {/* ── Top Level Overview Grid ────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: Circular Match Score */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 flex flex-col items-center justify-center relative overflow-hidden text-center"
        >
          <div className="absolute top-4 left-4 flex items-center space-x-2 text-xs font-mono text-gray-400">
            <Award className="w-4 h-4 text-indigo-400" />
            <span>Overall Match Score</span>
          </div>

          {/* SVG Circular Gauge */}
          <div className="relative w-40 h-40 mt-4 mb-2 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="80"
                cy="80"
                r={radius}
                className="text-white/10"
                strokeWidth="12"
                stroke="currentColor"
                fill="transparent"
              />
              <motion.circle
                cx="80"
                cy="80"
                r={radius}
                className="text-indigo-500"
                strokeWidth="12"
                strokeDasharray={circumference}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset }}
                transition={{ duration: 1.2, ease: 'easeOut' }}
                strokeLinecap="round"
                stroke="url(#scoreGradient)"
                fill="transparent"
              />
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#818cf8" />
                  <stop offset="50%" stopColor="#c084fc" />
                  <stop offset="100%" stopColor="#f43f5e" />
                </linearGradient>
              </defs>
            </svg>

            <div className="absolute flex flex-col items-center justify-center">
              <span className="font-heading font-black text-4xl text-white tracking-tight">{score}%</span>
              <span className="text-[10px] uppercase font-mono text-indigo-300 tracking-wider">
                {data.match_level}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Card 2: Recommendation & Risk */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">Hiring Recommendation</span>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getDecisionBadge()}`}>
                {decision}
              </span>
            </div>

            <p className="text-sm text-gray-300 leading-relaxed mb-6 font-normal">
              {data.recommendation.summary}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
            <div>
              <span className="text-xs text-gray-400 block mb-1">Hiring Risk Level</span>
              <div className="flex items-center space-x-1.5 font-bold text-sm">
                {hiringRisk === 'Low' ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-emerald-400">Low Risk</span>
                  </>
                ) : hiringRisk === 'Medium' ? (
                  <>
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <span className="text-yellow-400">Medium Risk</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4 text-red-400" />
                    <span className="text-red-400">High Risk</span>
                  </>
                )}
              </div>
            </div>

            <div>
              <span className="text-xs text-gray-400 block mb-1">Interview Action</span>
              <span className="text-xs font-medium text-indigo-300 line-clamp-2">
                {data.recommendation.interview_recommendation}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Card 3: Confidence Score & Fidelity */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">Prediction Confidence</span>
              <span className="text-sm font-mono font-bold text-purple-400">{confidence}%</span>
            </div>

            {/* Confidence Progress Bar */}
            <div className="w-full h-2.5 bg-white/10 rounded-full overflow-hidden mb-6">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all duration-1000"
                style={{ width: `${confidence}%` }}
              />
            </div>

            <span className="text-xs text-gray-400 font-semibold uppercase tracking-wider block mb-2">Fidelity Reasons:</span>
            <ul className="space-y-1.5 text-xs text-gray-300">
              {data.confidence.reasons.map((reason, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-purple-400 font-bold">•</span>
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        </motion.div>
      </div>

      {/* ── Dimension Score Breakdown Cards ───────────────────── */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10">
        <h3 className="font-heading font-bold text-lg text-white mb-6 flex items-center space-x-2">
          <Award className="w-5 h-5 text-indigo-400" />
          <span>Dimension Score Breakdown & Active Weights</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Skills Score */}
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-300">Skills Score</span>
              <span className="text-xs font-mono text-indigo-400">Weight: {data.weight_strategy.weights.skills}%</span>
            </div>
            <div className="text-2xl font-black font-heading text-white mb-2">{data.scores.skill_score}%</div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500" style={{ width: `${data.scores.skill_score}%` }} />
            </div>
          </div>

          {/* Experience Score */}
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-300">Experience Score</span>
              <span className="text-xs font-mono text-purple-400">Weight: {data.weight_strategy.weights.experience}%</span>
            </div>
            <div className="text-2xl font-black font-heading text-white mb-2">{data.scores.experience_score}%</div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-purple-500" style={{ width: `${data.scores.experience_score}%` }} />
            </div>
          </div>

          {/* Semantic Score */}
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-300">Semantic Match</span>
              <span className="text-xs font-mono text-pink-400">Weight: {data.weight_strategy.weights.semantic}%</span>
            </div>
            <div className="text-2xl font-black font-heading text-white mb-2">{data.scores.semantic_score}%</div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-pink-500" style={{ width: `${data.scores.semantic_score}%` }} />
            </div>
          </div>

          {/* Education Score */}
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-300">Education Score</span>
              <span className="text-xs font-mono text-teal-400">Weight: {data.weight_strategy.weights.education}%</span>
            </div>
            <div className="text-2xl font-black font-heading text-white mb-2">{data.scores.education_score}%</div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-teal-500" style={{ width: `${data.scores.education_score}%` }} />
            </div>
          </div>

          {/* Projects Score */}
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-300">Projects Portfolio</span>
              <span className="text-xs font-mono text-yellow-400">
                Weight: {data.scores.projects_score !== null ? `${data.weight_strategy.weights.projects}%` : 'N/A'}
              </span>
            </div>
            <div className="text-2xl font-black font-heading text-white mb-2">
              {data.scores.projects_score !== null ? `${data.scores.projects_score}%` : 'N/A'}
            </div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-yellow-500"
                style={{ width: `${data.scores.projects_score !== null ? data.scores.projects_score : 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
