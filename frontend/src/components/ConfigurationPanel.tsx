import React from 'react';
import { motion } from 'framer-motion';
import { Sliders, Sparkles, AlertCircle, Info, Layers } from 'lucide-react';
import type { StrategyType, PresetType } from '../types';

interface ConfigurationPanelProps {
  strategy: StrategyType;
  setStrategy: (s: StrategyType) => void;
  preset: PresetType;
  setPreset: (p: PresetType) => void;
  isManual: boolean;
  setIsManual: (m: boolean) => void;
  weights: {
    skills: number;
    experience: number;
    semantic: number;
    education: number;
    projects: number;
  };
  setWeights: React.Dispatch<
    React.SetStateAction<{
      skills: number;
      experience: number;
      semantic: number;
      education: number;
      projects: number;
    }>
  >;
}

const presetsList: { id: PresetType; label: string; description: string }[] = [
  { id: 'ai_engineer', label: 'AI Engineer', description: 'Emphasizes LLM/PyTorch frameworks (40% skills, 10% projects)' },
  { id: 'backend_engineer', label: 'Backend Engineer', description: 'High skill & API architecture emphasis (45% skills)' },
  { id: 'frontend_engineer', label: 'Frontend Engineer', description: 'Focuses on UI frameworks & portfolio projects (10% projects)' },
  { id: 'data_scientist', label: 'Data Scientist', description: 'Combines statistical skills & high education weight (15% education)' },
  { id: 'healthcare_rcm', label: 'Healthcare RCM', description: 'Heavy experience focus (35% experience, ICD/CPT coding)' },
  { id: 'finance', label: 'Finance & FinTech', description: 'High weight on industry experience & financial modeling' },
  { id: 'sales', label: 'Sales & BD', description: 'Prioritizes deal history & quotas (40% experience, 0% projects)' },
  { id: 'hr', label: 'Human Resources', description: 'Prioritizes recruitment operations (40% experience)' },
  { id: 'general_software_engineer', label: 'General Software Engineer', description: 'Balanced technical profile evaluation' },
];

export const ConfigurationPanel: React.FC<ConfigurationPanelProps> = ({
  strategy,
  setStrategy,
  preset,
  setPreset,
  isManual,
  setIsManual,
  weights,
  setWeights,
}) => {
  const totalWeight = weights.skills + weights.experience + weights.semantic + weights.education + weights.projects;
  const isSumValid = totalWeight === 100;

  const handleWeightChange = (key: keyof typeof weights, value: number) => {
    setWeights((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 mb-12"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <Sliders className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-xl text-white">Matching Strategy & Weight Configuration</h3>
            <p className="text-xs text-gray-400">Customize how the AI scoring engine evaluates resume dimensions</p>
          </div>
        </div>

        {/* Strategy Selector Pills */}
        <div className="flex bg-white/5 p-1 rounded-xl border border-white/10 text-xs font-medium self-start sm:self-auto">
          <button
            type="button"
            onClick={() => {
              setStrategy('AUTO');
              setIsManual(false);
            }}
            className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all ${
              strategy === 'AUTO' && !isManual ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Auto Detect</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setStrategy('PRESET');
              setIsManual(false);
            }}
            className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all ${
              strategy === 'PRESET' && !isManual ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Role Preset</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setStrategy('MANUAL');
              setIsManual(true);
            }}
            className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all ${
              isManual ? 'bg-pink-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>Manual Weights</span>
          </button>
        </div>
      </div>

      {/* Mode 1: Preset Dropdown */}
      {strategy === 'PRESET' && !isManual && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
            Select Role Preset
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {presetsList.map((p) => (
              <div
                key={p.id}
                onClick={() => setPreset(p.id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  preset === p.id
                    ? 'bg-purple-500/15 border-purple-500/50 shadow-lg shadow-purple-500/10'
                    : 'bg-white/[0.02] border-white/10 hover:border-white/20'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-heading font-semibold text-sm text-white">{p.label}</span>
                  {preset === p.id && <span className="w-2 h-2 rounded-full bg-purple-400" />}
                </div>
                <p className="text-xs text-gray-400 leading-tight">{p.description}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Mode 2: Manual Weight Sliders */}
      {isManual && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Weight Total Indicator Header */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center space-x-2">
              <Info className="w-4 h-4 text-indigo-400" />
              <span className="text-xs text-gray-300">
                Adjust dimension weight allocation. Sum must equal <strong className="text-white">100%</strong>.
              </span>
            </div>
            <div
              className={`px-3 py-1 rounded-full text-xs font-mono font-bold flex items-center space-x-1.5 ${
                isSumValid ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-red-500/20 text-red-300 border border-red-500/30 animate-pulse'
              }`}
            >
              {!isSumValid && <AlertCircle className="w-3.5 h-3.5" />}
              <span>Total: {totalWeight}%</span>
            </div>
          </div>

          {/* Sliders Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            {/* Skills Slider */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-medium text-gray-300">Skills Weight</span>
                <span className="font-mono font-bold text-indigo-400 text-sm">{weights.skills}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weights.skills}
                onChange={(e) => handleWeightChange('skills', Number(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>

            {/* Experience Slider */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-medium text-gray-300">Experience Weight</span>
                <span className="font-mono font-bold text-purple-400 text-sm">{weights.experience}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weights.experience}
                onChange={(e) => handleWeightChange('experience', Number(e.target.value))}
                className="w-full accent-purple-500 cursor-pointer"
              />
            </div>

            {/* Semantic Slider */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-medium text-gray-300">Semantic Weight</span>
                <span className="font-mono font-bold text-pink-400 text-sm">{weights.semantic}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weights.semantic}
                onChange={(e) => handleWeightChange('semantic', Number(e.target.value))}
                className="w-full accent-pink-500 cursor-pointer"
              />
            </div>

            {/* Education Slider */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-medium text-gray-300">Education Weight</span>
                <span className="font-mono font-bold text-teal-400 text-sm">{weights.education}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weights.education}
                onChange={(e) => handleWeightChange('education', Number(e.target.value))}
                className="w-full accent-teal-500 cursor-pointer"
              />
            </div>

            {/* Projects Slider */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-medium text-gray-300">Projects Weight</span>
                <span className="font-mono font-bold text-yellow-400 text-sm">{weights.projects}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weights.projects}
                onChange={(e) => handleWeightChange('projects', Number(e.target.value))}
                className="w-full accent-yellow-500 cursor-pointer"
              />
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};
