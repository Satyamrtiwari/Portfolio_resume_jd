import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, HelpCircle, Briefcase, GraduationCap, Code2, FileSearch } from 'lucide-react';
import type { Explainability, ScoreBreakdown } from '../types';

interface ExplainabilityAccordionProps {
  explainability: Explainability;
  scores: ScoreBreakdown;
}

export const ExplainabilityAccordion: React.FC<ExplainabilityAccordionProps> = ({
  explainability,
  scores,
}) => {
  const [openSection, setOpenSection] = useState<string | null>('summary');

  const toggle = (section: string) => {
    setOpenSection(openSection === section ? null : section);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 mb-8"
    >
      <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-white/10">
        <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
          <HelpCircle className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-heading font-bold text-xl text-white">Transparent AI Audit & Explainability</h3>
          <p className="text-xs text-gray-400">Itemized decision logic explaining how score dimensions were evaluated</p>
        </div>
      </div>

      <div className="space-y-3">
        {/* Accordion Item 1: Summary Overview */}
        <div className="rounded-xl border border-white/10 overflow-hidden bg-white/[0.01]">
          <button
            type="button"
            onClick={() => toggle('summary')}
            className="w-full p-4 text-left flex items-center justify-between font-heading font-semibold text-sm text-white hover:bg-white/5 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <FileSearch className="w-4 h-4 text-indigo-400" />
              <span>Overall Match Rationale Summary</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${openSection === 'summary' ? 'rotate-180' : ''}`} />
          </button>
          <AnimatePresence>
            {openSection === 'summary' && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="p-4 pt-0 text-xs text-gray-300 leading-relaxed border-t border-white/5"
              >
                {explainability.summary}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Accordion Item 2: Experience Explanation */}
        <div className="rounded-xl border border-white/10 overflow-hidden bg-white/[0.01]">
          <button
            type="button"
            onClick={() => toggle('experience')}
            className="w-full p-4 text-left flex items-center justify-between font-heading font-semibold text-sm text-white hover:bg-white/5 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <Briefcase className="w-4 h-4 text-purple-400" />
              <span>Experience & Seniority Evaluation Alignment: {explainability.experience_alignment}</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${openSection === 'experience' ? 'rotate-180' : ''}`} />
          </button>
          <AnimatePresence>
            {openSection === 'experience' && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="p-4 pt-0 text-xs text-gray-300 border-t border-white/5 space-y-2"
              >
                <p className="text-gray-400">Detailed Experience Explainability Points:</p>
                <ul className="space-y-1.5 font-mono">
                  {scores.experience_explainability.map((item, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Accordion Item 3: Education Explanation */}
        <div className="rounded-xl border border-white/10 overflow-hidden bg-white/[0.01]">
          <button
            type="button"
            onClick={() => toggle('education')}
            className="w-full p-4 text-left flex items-center justify-between font-heading font-semibold text-sm text-white hover:bg-white/5 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <GraduationCap className="w-4 h-4 text-teal-400" />
              <span>Education & Branch Alignment: {explainability.education_alignment}</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${openSection === 'education' ? 'rotate-180' : ''}`} />
          </button>
          <AnimatePresence>
            {openSection === 'education' && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="p-4 pt-0 text-xs text-gray-300 leading-relaxed border-t border-white/5"
              >
                Candidate qualification tier and branch specialization evaluated against JD minimum degree prerequisites. Tier alignment: {explainability.education_alignment}.
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Accordion Item 4: Skill Explanation */}
        <div className="rounded-xl border border-white/10 overflow-hidden bg-white/[0.01]">
          <button
            type="button"
            onClick={() => toggle('skills')}
            className="w-full p-4 text-left flex items-center justify-between font-heading font-semibold text-sm text-white hover:bg-white/5 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <Code2 className="w-4 h-4 text-pink-400" />
              <span>Skill & Synonym Taxonomy Matching Explanation</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${openSection === 'skills' ? 'rotate-180' : ''}`} />
          </button>
          <AnimatePresence>
            {openSection === 'skills' && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="p-4 pt-0 text-xs text-gray-300 leading-relaxed border-t border-white/5 space-y-2"
              >
                <p>Matched {explainability.matched_skills.length} skills across languages, frameworks, tools, cloud & databases.</p>
                <p className="text-gray-400">Missing required skills: {explainability.missing_skills.join(', ') || 'None'}.</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};
