import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, FileText, FileCode, Sliders, Download, Copy, Printer, Check } from 'lucide-react';
import type { MatchResponse } from '../types';

interface ProcessingStatsProps {
  data: MatchResponse;
}

export const ProcessingStats: React.FC<ProcessingStatsProps> = ({ data }) => {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopySummary = () => {
    const summaryText = `
FatPai AI Match Report Summary
------------------------------------
Candidate: ${data.candidate_profile.name || 'Unknown'}
Overall Match Score: ${data.match_score}% (${data.match_level})
Hiring Recommendation: ${data.recommendation.decision}
Confidence Score: ${data.confidence.score}%
Hiring Risk: ${data.recommendation.hiring_risk}

ATS Keyword Coverage: ${data.ats_analysis.coverage_percentage ?? 'N/A'}%
Matched Skills: ${data.explainability.matched_skills.join(', ') || 'None'}
Critical Missing Skills: ${data.ats_analysis.critical_missing_skills.join(', ') || 'None'}

Summary: ${data.recommendation.summary}
    `.trim();

    navigator.clipboard.writeText(summaryText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Match_Report_${data.candidate_profile.name?.replace(/\s+/g, '_') || 'Candidate'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrintReport = () => {
    window.print();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 mb-16"
    >
      {/* Small Stat Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-panel p-4 rounded-xl border border-white/10 flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] text-gray-400 block uppercase font-mono">Execution Speed</span>
            <span className="font-mono font-bold text-sm text-white">{data.processing_time}</span>
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-white/10 flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] text-gray-400 block uppercase font-mono">Resume Length</span>
            <span className="font-mono font-bold text-sm text-white">{data.resume_length} words</span>
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-white/10 flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-teal-500/10 text-teal-400">
            <FileCode className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] text-gray-400 block uppercase font-mono">JD Length</span>
            <span className="font-mono font-bold text-sm text-white">{data.jd_length} words</span>
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-white/10 flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-pink-500/10 text-pink-400">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] text-gray-400 block uppercase font-mono">Strategy Used</span>
            <span className="font-mono font-bold text-sm text-white">{data.weight_strategy.strategy_used}</span>
          </div>
        </div>
      </div>

      {/* Export Action Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-white/10 flex flex-wrap items-center justify-between gap-4">
        <span className="text-xs text-gray-400 font-mono">Export Candidate Audit Report:</span>

        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={handleCopySummary}
            className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/10 text-xs font-medium transition-all flex items-center space-x-2"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied to Clipboard!' : 'Copy Summary'}</span>
          </button>

          <button
            type="button"
            onClick={handleDownloadJson}
            className="px-4 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-medium transition-all flex items-center space-x-2"
          >
            <Download className="w-4 h-4 text-indigo-400" />
            <span>Download JSON</span>
          </button>

          <button
            type="button"
            onClick={handlePrintReport}
            className="px-4 py-2 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs font-medium transition-all flex items-center space-x-2"
          >
            <Printer className="w-4 h-4 text-purple-400" />
            <span>Print PDF Report</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
};
