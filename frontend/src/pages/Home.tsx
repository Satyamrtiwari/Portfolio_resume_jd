import React, { useState } from 'react';
import confetti from 'canvas-confetti';
import { Navbar } from '../components/Navbar';
import { Hero } from '../components/Hero';
import { HowItWorks } from '../components/HowItWorks';
import { UploadSection } from '../components/UploadSection';
import { ConfigurationPanel } from '../components/ConfigurationPanel';
import { AnalysisButton } from '../components/AnalysisButton';
import { ResultsDashboard } from '../components/ResultsDashboard';
import { EmptyState } from '../components/EmptyState';
import { ToastNotification } from '../components/ToastNotification';
import type { StrategyType, PresetType, MatchResponse } from '../types';

export const Home: React.FC = () => {
  // Input State
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState<string>('');
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState<string>('');

  // Config State
  const [strategy, setStrategy] = useState<StrategyType>('AUTO');
  const [preset, setPreset] = useState<PresetType>('ai_engineer');
  const [isManual, setIsManual] = useState<boolean>(false);
  const [weights, setWeights] = useState({
    skills: 40,
    experience: 30,
    semantic: 15,
    education: 10,
    projects: 5,
  });

  // Result & UI State
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [toastError, setToastError] = useState<string | null>(null);

  // 1-Click Sample Pre-loader
  const handleLoadSample = (sampleType: 'ai_engineer' | 'healthcare_rcm') => {
    if (sampleType === 'ai_engineer') {
      setResumeFile(null);
      setResumeText(
        `Satyam R Tiwari\ntiwarisatyamr10@gmail.com | +91 8208854485 | Palghar, Maharashtra, India\nGitHub: github.com/Satyamrtiwari | LinkedIn: linkedin.com/in/satyam-tiwari-219583276\n\nSUMMARY\nPassionate AI & Machine Learning Engineer specializing in PyTorch, Large Language Models (LLMs), RAG pipelines, Vector Search (Milvus/Faiss), HuggingFace Transformers, and Docker containerized API services.\n\nEXPERIENCE\nAI Engineer Intern — Infinx (2024 - Present)\n- Developed RAG pipelines and fine-tuned SentenceTransformers for semantic search.\n- Built high-throughput API endpoints with FastAPI and PyTorch.\n\nEDUCATION\nBachelor of Engineering in Computer Science (AI & ML) — Mumbai University\n\nTECHNICAL SKILLS\nLanguages: Python, C++, SQL\nFrameworks: PyTorch, FastAPI, Flask, HuggingFace, LangChain\nTools & DBs: Docker, Milvus, Git, GitHub`
      );
      setJdFile(null);
      setJdText(
        `Senior AI & Machine Learning Engineer\nResponsibilities:\n- Build production RAG and LLM applications using PyTorch, HuggingFace, LangChain, and Milvus vector DB.\n- Develop scalable APIs using FastAPI / Flask.\nRequirements:\n- 2+ years of experience in Python, PyTorch, Natural Language Processing (NLP), BERT, GPT models, Milvus, Git.`
      );
      setStrategy('PRESET');
      setPreset('ai_engineer');
      setIsManual(false);
    } else {
      setResumeFile(null);
      setResumeText(
        `Anay Gurav\nanaygurav@gmail.com | Mumbai, India\n\nPROFESSIONAL SUMMARY\nSenior Revenue Cycle Management (RCM) & Pre-Authorization Specialist with 4+ years of experience in medical billing, claims verification, ICD-10 coding, HIPAA compliance, and insurance denial management.\n\nEXPERIENCE\nPre-Auth Senior Associate — Sagility Healthcare (2021 - Present)\n- Managed prior authorizations and insurance verification for US hospital networks.\n\nEDUCATION\nBachelor of Science — Mumbai University`
      );
      setJdFile(null);
      setJdText(
        `Healthcare RCM & Pre-Authorization Specialist\nRequirements:\n- 3+ years of experience in US Healthcare RCM, medical billing, prior authorization, HIPAA compliance, AR process, and claims auditing.`
      );
      setStrategy('PRESET');
      setPreset('healthcare_rcm');
      setIsManual(false);
    }
  };

  // API Call Execution
  const handleMatch = async () => {
    if (!resumeFile && !resumeText.trim()) {
      setToastError('Please upload a Resume PDF/DOCX file or paste candidate text.');
      return;
    }
    if (!jdFile && !jdText.trim()) {
      setToastError('Please upload a Job Description PDF/DOCX file or paste requirements.');
      return;
    }

    if (isManual) {
      const total = weights.skills + weights.experience + weights.semantic + weights.education + weights.projects;
      if (total !== 100) {
        setToastError(`Manual weights total must equal 100%. Current total: ${total}%.`);
        return;
      }
    }

    setToastError(null);
    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();

      if (resumeFile) formData.append('resume_file', resumeFile);
      if (resumeText.trim()) formData.append('resume_text', resumeText.trim());
      if (jdFile) formData.append('jd_file', jdFile);
      if (jdText.trim()) formData.append('jd_text', jdText.trim());

      const activeStrategy = isManual ? 'MANUAL' : strategy;
      formData.append('strategy', activeStrategy);

      if (activeStrategy === 'PRESET') {
        formData.append('preset_name', preset);
      } else if (activeStrategy === 'MANUAL') {
        formData.append('manual_weights', JSON.stringify(weights));
      }

      const response = await fetch('/api/v1/match', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({ detail: 'Analysis failed.' }));
        throw new Error(errJson.detail || 'Match request failed.');
      }

      const data: MatchResponse = await response.json();
      setResult(data);

      // Trigger Confetti if score >= 75%
      if (data.match_score >= 75) {
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 },
        });
      }

      // Scroll to results
      setTimeout(() => {
        const element = document.getElementById('results-section');
        if (element) element.scrollIntoView({ behavior: 'smooth' });
      }, 200);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to connect to AI Matching Backend.';
      setToastError(msg);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = (Boolean(resumeFile) || Boolean(resumeText.trim())) && (Boolean(jdFile) || Boolean(jdText.trim()));

  return (
    <div className="min-h-screen flex flex-col bg-[#090a0f] text-gray-100 selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Toast Notification */}
      <ToastNotification message={toastError} type="error" onClose={() => setToastError(null)} />

      {/* Header */}
      <Navbar />

      {/* Hero */}
      <Hero />

      {/* How It Works */}
      <HowItWorks />

      {/* Match Console Section */}
      <section id="matcher" className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        {/* Upload Panel */}
        <UploadSection
          resumeFile={resumeFile}
          setResumeFile={setResumeFile}
          resumeText={resumeText}
          setResumeText={setResumeText}
          jdFile={jdFile}
          setJdFile={setJdFile}
          jdText={jdText}
          setJdText={setJdText}
        />

        {/* Configuration Panel */}
        <ConfigurationPanel
          strategy={strategy}
          setStrategy={setStrategy}
          preset={preset}
          setPreset={setPreset}
          isManual={isManual}
          setIsManual={setIsManual}
          weights={weights}
          setWeights={setWeights}
        />

        {/* Match Execute Button */}
        <AnalysisButton onMatch={handleMatch} loading={loading} disabled={!isFormValid} />

        {/* Results or Empty State */}
        <div id="results-section">
          {result ? <ResultsDashboard data={result} /> : !loading && <EmptyState onLoadSample={handleLoadSample} />}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-white/10 text-center text-xs text-gray-500 glass-panel">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 FatPai Resume Intelligence Platform. BAAI/bge-large-en-v1.5 & Generative AI Matching.</p>
          <div className="flex items-center space-x-4">
            <a href="/docs" target="_blank" rel="noreferrer" className="hover:text-gray-300 transition-colors">
              FastAPI Swagger Docs
            </a>
            <a href="#how-it-works" className="hover:text-gray-300 transition-colors">
              How It Works
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};
