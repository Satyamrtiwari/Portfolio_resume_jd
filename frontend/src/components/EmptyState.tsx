import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, FileText, UploadCloud, Play } from 'lucide-react';

interface EmptyStateProps {
  onLoadSample: (sampleType: 'ai_engineer' | 'healthcare_rcm') => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onLoadSample }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-panel p-10 sm:p-16 rounded-3xl border border-white/10 text-center max-w-3xl mx-auto my-12 relative overflow-hidden"
    >
      {/* Glow Effect */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-600/10 rounded-full blur-[90px] pointer-events-none" />

      {/* Illustration Icon */}
      <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 p-0.5 shadow-2xl shadow-indigo-500/20">
        <div className="w-full h-full bg-[#0d0e15] rounded-[22px] flex items-center justify-center">
          <UploadCloud className="w-10 h-10 text-indigo-400" />
        </div>
      </div>

      <h3 className="font-heading font-extrabold text-2xl sm:text-3xl text-white tracking-tight mb-3">
        Ready for AI Resume Intelligence
      </h3>

      <p className="text-gray-400 text-sm sm:text-base max-w-lg mx-auto leading-relaxed mb-8">
        Upload a candidate Resume and Job Description (PDF/DOCX or plain text) above to generate a comprehensive AI match analysis, ATS keyword coverage, and recruiter hiring report.
      </p>

      {/* 1-Click Sample Pre-load Buttons */}
      <div className="pt-6 border-t border-white/10">
        <span className="text-xs text-gray-500 font-mono uppercase tracking-wider block mb-4">
          Or test instantly with 1-click sample data:
        </span>

        <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
          <button
            type="button"
            onClick={() => onLoadSample('ai_engineer')}
            className="w-full sm:w-auto px-5 py-3 rounded-xl bg-indigo-600/15 hover:bg-indigo-600/25 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-all flex items-center justify-center space-x-2 group"
          >
            <Sparkles className="w-4 h-4 text-indigo-400 group-hover:rotate-12 transition-transform" />
            <span>Load AI Engineer Sample</span>
            <Play className="w-3.5 h-3.5 text-indigo-400 ml-1" />
          </button>

          <button
            type="button"
            onClick={() => onLoadSample('healthcare_rcm')}
            className="w-full sm:w-auto px-5 py-3 rounded-xl bg-purple-600/15 hover:bg-purple-600/25 text-purple-300 border border-purple-500/30 text-xs font-semibold transition-all flex items-center justify-center space-x-2 group"
          >
            <FileText className="w-4 h-4 text-purple-400 group-hover:rotate-12 transition-transform" />
            <span>Load Healthcare RCM Sample</span>
            <Play className="w-3.5 h-3.5 text-purple-400 ml-1" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};
