import React, { useState, useEffect } from 'react';
import { Sparkles, Cpu, Activity, Terminal } from 'lucide-react';

export const Navbar: React.FC = () => {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    fetch('/api/v1/')
      .then((res) => res.json())
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-[#0d0e15] rounded-[10px] flex items-center justify-center">
              <Cpu className="w-5 h-5 text-indigo-400 animate-pulse" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-heading font-extrabold text-xl text-white tracking-tight">FatPai</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 uppercase tracking-widest font-semibold">
                AI Matcher v3
              </span>
            </div>
            <p className="text-xs text-gray-400 -mt-0.5">Enterprise Resume Intelligence</p>
          </div>
        </div>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
          <a href="#how-it-works" className="text-gray-300 hover:text-white transition-colors">How It Works</a>
          <a href="#matcher" className="text-gray-300 hover:text-white transition-colors">Match Console</a>
          <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
          <a href="/docs" target="_blank" rel="noreferrer" className="flex items-center space-x-1.5 text-gray-300 hover:text-indigo-400 transition-colors">
            <Terminal className="w-4 h-4" />
            <span>API Docs</span>
          </a>
        </nav>

        {/* Right Status Badge & Actions */}
        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-mono">
            <Activity className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-gray-400">API Status:</span>
            {apiOnline === null ? (
              <span className="text-yellow-400 animate-pulse">Checking...</span>
            ) : apiOnline ? (
              <span className="flex items-center text-emerald-400 font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-ping"></span>
                Healthy
              </span>
            ) : (
              <span className="text-amber-400 font-semibold">Ready (Local Engine)</span>
            )}
          </div>

          <a
            href="#matcher"
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-xs sm:text-sm shadow-lg shadow-indigo-500/25 transition-all transform hover:-translate-y-0.5"
          >
            <Sparkles className="w-4 h-4" />
            <span>Start Matching</span>
          </a>
        </div>
      </div>
    </header>
  );
};
