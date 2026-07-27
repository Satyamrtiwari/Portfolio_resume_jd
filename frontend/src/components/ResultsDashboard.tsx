import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Award, FileCode, UserCheck, Layers, HelpCircle, Code, CheckCircle2 } from 'lucide-react';
import type { MatchResponse } from '../types';
import { ScoreCards } from './ScoreCards';
import { ATSCard } from './ATSCard';
import { CandidateProfile } from './CandidateProfile';
import { RecruiterSummary } from './RecruiterSummary';
import { SimilarityCards } from './SimilarityCards';
import { ExplainabilityAccordion } from './ExplainabilityAccordion';
import { ProcessingStats } from './ProcessingStats';

interface ResultsDashboardProps {
  data: MatchResponse;
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'ats' | 'profile' | 'similarity' | 'explainability' | 'json'>('overview');

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-8"
    >
      {/* ── Top Header Banner ──────────────────────────────────── */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center space-x-2 text-xs font-mono text-indigo-400 mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>AI Match Analysis Completed</span>
          </div>
          <h2 className="font-heading font-black text-2xl sm:text-4xl text-white tracking-tight">
            Candidate Evaluation Report
          </h2>
        </div>

        {/* View Tabs */}
        <div className="flex bg-white/5 p-1.5 rounded-2xl border border-white/10 text-xs font-medium overflow-x-auto">
          <button
            type="button"
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-xl flex items-center space-x-2 transition-all shrink-0 ${
              activeTab === 'overview' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Award className="w-4 h-4" />
            <span>Overview</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('ats')}
            className={`px-4 py-2 rounded-xl flex items-center space-x-2 transition-all shrink-0 ${
              activeTab === 'ats' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <FileCode className="w-4 h-4" />
            <span>ATS Coverage</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('profile')}
            className={`px-4 py-2 rounded-xl flex items-center space-x-2 transition-all shrink-0 ${
              activeTab === 'profile' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <UserCheck className="w-4 h-4" />
            <span>Profile</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('similarity')}
            className={`px-4 py-2 rounded-xl flex items-center space-x-2 transition-all shrink-0 ${
              activeTab === 'similarity' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Sections</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('explainability')}
            className={`px-4 py-2 rounded-xl flex items-center space-x-2 transition-all shrink-0 ${
              activeTab === 'explainability' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            <span>Explainability</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('json')}
            className={`px-4 py-2 rounded-xl flex items-center space-x-2 transition-all shrink-0 ${
              activeTab === 'json' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Code className="w-4 h-4" />
            <span>Raw JSON</span>
          </button>
        </div>
      </div>

      {/* ── Active Tab View Content ────────────────────────────── */}
      {activeTab === 'overview' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <ScoreCards data={data} />
          <RecruiterSummary summary={data.recruiter_summary} recommendation={data.recommendation} />
          <ATSCard ats={data.ats_analysis} />
          <CandidateProfile profile={data.candidate_profile} />
        </motion.div>
      )}

      {activeTab === 'ats' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <ATSCard ats={data.ats_analysis} />
        </motion.div>
      )}

      {activeTab === 'profile' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <CandidateProfile profile={data.candidate_profile} />
        </motion.div>
      )}

      {activeTab === 'similarity' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <SimilarityCards sections={data.top_matching_sections} />
        </motion.div>
      )}

      {activeTab === 'explainability' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <ExplainabilityAccordion explainability={data.explainability} scores={data.scores} />
        </motion.div>
      )}

      {activeTab === 'json' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="glass-panel p-6 rounded-2xl border border-white/10">
            <h4 className="font-mono text-xs text-gray-400 mb-4 uppercase">Raw API JSON Payload</h4>
            <pre className="p-4 rounded-xl bg-[#0d0e15] border border-white/10 text-xs font-mono text-indigo-300 overflow-x-auto max-h-[600px]">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        </motion.div>
      )}

      {/* Processing Footer Statistics */}
      <ProcessingStats data={data} />
    </motion.div>
  );
};
