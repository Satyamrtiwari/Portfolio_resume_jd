import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Zap, Shield, ChevronDown, CheckCircle2, ArrowRight } from 'lucide-react';

export const Hero: React.FC = () => {
  const scrollToConsole = () => {
    const element = document.getElementById('matcher');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="relative min-h-[90vh] flex flex-col justify-center items-center pt-16 pb-24 px-4 sm:px-6 lg:px-8 overflow-hidden bg-grid-pattern">
      {/* Floating Ambient Glow Blobs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-indigo-600/20 via-purple-600/15 to-pink-500/10 rounded-full blur-[140px] pointer-events-none animate-pulse-glow" />
      <div className="absolute bottom-10 left-1/4 w-[350px] h-[350px] bg-blue-600/10 rounded-full blur-[100px] pointer-events-none" />

      {/* Top Announcement Badge */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs sm:text-sm font-medium mb-8 backdrop-blur-md"
      >
        <span className="flex h-2 w-2 rounded-full bg-indigo-400 animate-ping" />
        <Sparkles className="w-4 h-4 text-indigo-400" />
        <span>Powered by BAAI/bge-large-en-v1.5 & Generative AI</span>
        <ArrowRight className="w-3.5 h-3.5 ml-1 text-indigo-400" />
      </motion.div>

      {/* Main Hero Heading */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.1 }}
        className="font-heading font-extrabold text-4xl sm:text-6xl md:text-7xl text-center max-w-4xl tracking-tight leading-[1.1] mb-6"
      >
        <span className="text-gradient">AI Resume Intelligence</span>
        <br />
        <span className="text-gray-400 text-3xl sm:text-5xl font-semibold">for Modern Recruitment</span>
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.2 }}
        className="text-gray-400 text-base sm:text-xl text-center max-w-2xl font-normal leading-relaxed mb-10"
      >
        Enterprise-grade Resume & Job Description Semantic Matching. Evaluate skills, experience, education, and domain fit with sub-second explainable AI reports.
      </motion.p>

      {/* CTA Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.3 }}
        className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4 w-full sm:w-auto mb-16"
      >
        <button
          onClick={scrollToConsole}
          className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold text-base shadow-xl shadow-indigo-600/30 hover:shadow-indigo-600/50 transition-all transform hover:-translate-y-0.5 flex items-center justify-center space-x-3 group"
        >
          <Zap className="w-5 h-5 group-hover:scale-110 transition-transform text-yellow-300 fill-yellow-300" />
          <span>Start Matching</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>

        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="w-full sm:w-auto px-8 py-4 rounded-xl glass-panel text-gray-300 hover:text-white font-medium text-base hover:bg-white/10 transition-all flex items-center justify-center space-x-2 border border-white/10"
        >
          <Shield className="w-5 h-5 text-gray-400" />
          <span>Explore API Docs</span>
        </a>
      </motion.div>

      {/* Feature Bullet Badges */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-8 text-xs sm:text-sm text-gray-400 max-w-4xl"
      >
        <div className="flex items-center space-x-2 glass-panel px-4 py-2.5 rounded-lg">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>PDF & DOCX Support</span>
        </div>
        <div className="flex items-center space-x-2 glass-panel px-4 py-2.5 rounded-lg">
          <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
          <span>BAAI/bge 1024-d Embeddings</span>
        </div>
        <div className="flex items-center space-x-2 glass-panel px-4 py-2.5 rounded-lg">
          <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0" />
          <span>Dynamic Weight Strategies</span>
        </div>
        <div className="flex items-center space-x-2 glass-panel px-4 py-2.5 rounded-lg">
          <CheckCircle2 className="w-4 h-4 text-pink-400 shrink-0" />
          <span>Explainable Recruiter Audit</span>
        </div>
      </motion.div>

      {/* Scroll Down Indicator */}
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        onClick={scrollToConsole}
        className="mt-16 text-gray-500 hover:text-gray-300 cursor-pointer flex flex-col items-center space-y-1 transition-colors"
      >
        <span className="text-xs uppercase tracking-widest font-mono">Scroll to Console</span>
        <ChevronDown className="w-5 h-5" />
      </motion.div>
    </section>
  );
};
