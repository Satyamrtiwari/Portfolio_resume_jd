import React from 'react';
import { motion } from 'framer-motion';
import { Layers, ArrowRight } from 'lucide-react';
import type { SectionMatch } from '../types';

interface SimilarityCardsProps {
  sections: SectionMatch[];
}

export const SimilarityCards: React.FC<SimilarityCardsProps> = ({ sections }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 mb-8"
    >
      <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-white/10">
        <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
          <Layers className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-heading font-bold text-xl text-white">Top Section Semantic Similarities</h3>
          <p className="text-xs text-gray-400">Deep BAAI/bge vector alignment between candidate resume sections and JD requirements</p>
        </div>
      </div>

      <div className="space-y-3">
        {sections.map((sec, idx) => {
          const pct = Math.round(sec.similarity * 100);
          return (
            <div
              key={idx}
              className="p-4 rounded-xl bg-white/[0.02] border border-white/10 hover:border-indigo-500/30 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                <span className="font-mono text-xs text-gray-500 font-bold">0{idx + 1}</span>
                <span className="px-3 py-1 rounded-lg bg-indigo-500/10 text-xs font-semibold text-indigo-300 truncate max-w-[200px]">
                  {sec.resume_section}
                </span>

                <ArrowRight className="w-4 h-4 text-gray-600 shrink-0" />

                <span className="px-3 py-1 rounded-lg bg-purple-500/10 text-xs font-semibold text-purple-300 truncate max-w-[200px]">
                  {sec.jd_section}
                </span>
              </div>

              <div className="flex items-center space-x-3 shrink-0">
                <div className="w-24 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      pct >= 70 ? 'bg-emerald-400' : pct >= 50 ? 'bg-indigo-400' : 'bg-yellow-400'
                    }`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="font-mono font-bold text-sm text-white w-12 text-right">{pct}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};
