import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Loader2, Cpu, CheckCircle2 } from 'lucide-react';

interface AnalysisButtonProps {
  onMatch: () => void;
  loading: boolean;
  disabled: boolean;
}

const processingStages = [
  'Extracting Resume Text & Parsing Structure...',
  'Understanding Job Requirements & Industry Domain...',
  'Executing Keyword & Synonym Taxonomy Matching...',
  'Computing BAAI/bge Vector Cosine Similarity...',
  'Calibrating Experience & Education Scores...',
  'Generating Recruiter Decision Report & Explainability...',
];

export const AnalysisButton: React.FC<AnalysisButtonProps> = ({
  onMatch,
  loading,
  disabled,
}) => {
  const [currentStageIdx, setCurrentStageIdx] = useState<number>(0);

  useEffect(() => {
    if (!loading) {
      setCurrentStageIdx(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStageIdx((prev) => (prev < processingStages.length - 1 ? prev + 1 : prev));
    }, 1500);

    return () => clearInterval(interval);
  }, [loading]);

  return (
    <div className="flex flex-col items-center justify-center mb-16">
      <motion.button
        whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
        whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
        onClick={onMatch}
        disabled={disabled || loading}
        className={`relative group px-10 py-5 rounded-2xl font-heading font-extrabold text-lg sm:text-xl transition-all shadow-2xl flex items-center space-x-4 overflow-hidden ${
          disabled
            ? 'bg-gray-800 text-gray-500 cursor-not-allowed border border-white/5'
            : loading
            ? 'bg-indigo-950 text-indigo-200 border border-indigo-500/50 cursor-wait'
            : 'bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-indigo-600/30 hover:shadow-indigo-600/50 cursor-pointer border border-white/20'
        }`}
      >
        {/* Glow Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 pointer-events-none" />

        {loading ? (
          <>
            <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
            <span>Analyzing Match...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-6 h-6 text-yellow-300 fill-yellow-300 group-hover:rotate-12 transition-transform" />
            <span>Generate AI Match Report</span>
            <Cpu className="w-5 h-5 text-indigo-300 opacity-80" />
          </>
        )}
      </motion.button>

      {/* Animated Loading Stages Text */}
      <AnimatePresence mode="wait">
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-6 flex flex-col items-center"
          >
            <div className="flex items-center space-x-2 text-sm font-mono text-indigo-300 mb-2 bg-indigo-500/10 px-4 py-1.5 rounded-full border border-indigo-500/20">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 animate-pulse" />
              <span>{processingStages[currentStageIdx]}</span>
            </div>

            {/* Progress Bar Track */}
            <div className="w-64 h-1.5 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: `${((currentStageIdx + 1) / processingStages.length) * 100}%` }}
                transition={{ duration: 0.5 }}
                className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
