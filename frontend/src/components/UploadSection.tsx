import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, FileCode2, X, CheckCircle, FileType, AlignLeft } from 'lucide-react';

interface UploadSectionProps {
  resumeFile: File | null;
  setResumeFile: (file: File | null) => void;
  resumeText: string;
  setResumeText: (text: string) => void;
  jdFile: File | null;
  setJdFile: (file: File | null) => void;
  jdText: string;
  setJdText: (text: string) => void;
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  resumeFile,
  setResumeFile,
  resumeText,
  setResumeText,
  jdFile,
  setJdFile,
  jdText,
  setJdText,
}) => {
  const [resumeTab, setResumeTab] = useState<'file' | 'text'>('file');
  const [jdTab, setJdTab] = useState<'file' | 'text'>('file');

  const resumeInputRef = useRef<HTMLInputElement>(null);
  const jdInputRef = useRef<HTMLInputElement>(null);

  const handleFileDrop = (
    e: React.DragEvent<HTMLDivElement>,
    type: 'resume' | 'jd'
  ) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (ext === 'pdf' || ext === 'docx') {
        if (type === 'resume') setResumeFile(file);
        else setJdFile(file);
      }
    }
  };

  const handleFileSelect = (
    e: React.ChangeEvent<HTMLInputElement>,
    type: 'resume' | 'jd'
  ) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (type === 'resume') setResumeFile(file);
      else setJdFile(file);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
      {/* ── 1. RESUME CARD ────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 flex flex-col justify-between"
      >
        <div>
          {/* Card Header & Tabs */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-heading font-bold text-xl text-white">Candidate Resume</h3>
                <p className="text-xs text-gray-400">Upload PDF / DOCX or paste plain text</p>
              </div>
            </div>

            {/* Input Toggle */}
            <div className="flex bg-white/5 p-1 rounded-lg border border-white/10 text-xs font-medium">
              <button
                type="button"
                onClick={() => setResumeTab('file')}
                className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition-all ${
                  resumeTab === 'file' ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white'
                }`}
              >
                <FileType className="w-3.5 h-3.5" />
                <span>PDF / DOCX</span>
              </button>
              <button
                type="button"
                onClick={() => setResumeTab('text')}
                className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition-all ${
                  resumeTab === 'text' ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white'
                }`}
              >
                <AlignLeft className="w-3.5 h-3.5" />
                <span>Text</span>
              </button>
            </div>
          </div>

          {/* File Upload Mode */}
          {resumeTab === 'file' ? (
            resumeFile ? (
              <div className="p-6 rounded-xl bg-indigo-950/30 border border-indigo-500/40 flex items-center justify-between transition-all">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">
                    {resumeFile.name.endsWith('.pdf') ? 'PDF' : 'DOCX'}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <p className="font-medium text-sm text-white truncate max-w-[200px] sm:max-w-[280px]">
                        {resumeFile.name}
                      </p>
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                    </div>
                    <p className="text-xs text-gray-400">
                      {(resumeFile.size / 1024).toFixed(1)} KB • Ready for extraction
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setResumeFile(null)}
                  className="p-2 rounded-lg bg-white/5 hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => handleFileDrop(e, 'resume')}
                onClick={() => resumeInputRef.current?.click()}
                className="border-2 border-dashed border-white/15 hover:border-indigo-500/50 rounded-xl p-8 text-center cursor-pointer bg-white/[0.02] hover:bg-indigo-500/[0.03] transition-all group"
              >
                <input
                  ref={resumeInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  className="hidden"
                  onChange={(e) => handleFileSelect(e, 'resume')}
                />
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                  <Upload className="w-8 h-8" />
                </div>
                <p className="text-sm font-semibold text-white mb-1">
                  Drag and drop candidate resume here
                </p>
                <p className="text-xs text-gray-400 mb-3">Accepts PDF or DOCX up to 10MB</p>
                <span className="inline-flex items-center text-xs font-medium text-indigo-400 bg-indigo-500/10 px-3 py-1.5 rounded-full border border-indigo-500/20">
                  Browse Files
                </span>
              </div>
            )
          ) : (
            /* Plaintext Mode */
            <div>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste full candidate resume text here (experience, skills, education)..."
                className="w-full h-48 p-4 rounded-xl bg-[#0d0e15] border border-white/10 text-xs sm:text-sm text-gray-200 focus:outline-none focus:border-indigo-500 transition-colors font-mono resize-none"
              />
              <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                <span>{resumeText.length} characters</span>
                {resumeText.length > 0 && (
                  <button type="button" onClick={() => setResumeText('')} className="text-gray-400 hover:text-red-400">
                    Clear Text
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* ── 2. JOB DESCRIPTION CARD ──────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 flex flex-col justify-between"
      >
        <div>
          {/* Card Header & Tabs */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
                <FileCode2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-heading font-bold text-xl text-white">Job Description</h3>
                <p className="text-xs text-gray-400">Upload PDF / DOCX or paste role requirements</p>
              </div>
            </div>

            {/* Input Toggle */}
            <div className="flex bg-white/5 p-1 rounded-lg border border-white/10 text-xs font-medium">
              <button
                type="button"
                onClick={() => setJdTab('file')}
                className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition-all ${
                  jdTab === 'file' ? 'bg-purple-600 text-white shadow-md' : 'text-gray-400 hover:text-white'
                }`}
              >
                <FileType className="w-3.5 h-3.5" />
                <span>PDF / DOCX</span>
              </button>
              <button
                type="button"
                onClick={() => setJdTab('text')}
                className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition-all ${
                  jdTab === 'text' ? 'bg-purple-600 text-white shadow-md' : 'text-gray-400 hover:text-white'
                }`}
              >
                <AlignLeft className="w-3.5 h-3.5" />
                <span>Text</span>
              </button>
            </div>
          </div>

          {/* File Upload Mode */}
          {jdTab === 'file' ? (
            jdFile ? (
              <div className="p-6 rounded-xl bg-purple-950/30 border border-purple-500/40 flex items-center justify-between transition-all">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center text-purple-400 font-bold">
                    {jdFile.name.endsWith('.pdf') ? 'PDF' : 'DOCX'}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <p className="font-medium text-sm text-white truncate max-w-[200px] sm:max-w-[280px]">
                        {jdFile.name}
                      </p>
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                    </div>
                    <p className="text-xs text-gray-400">
                      {(jdFile.size / 1024).toFixed(1)} KB • Ready for extraction
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setJdFile(null)}
                  className="p-2 rounded-lg bg-white/5 hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => handleFileDrop(e, 'jd')}
                onClick={() => jdInputRef.current?.click()}
                className="border-2 border-dashed border-white/15 hover:border-purple-500/50 rounded-xl p-8 text-center cursor-pointer bg-white/[0.02] hover:bg-purple-500/[0.03] transition-all group"
              >
                <input
                  ref={jdInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  className="hidden"
                  onChange={(e) => handleFileSelect(e, 'jd')}
                />
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                  <Upload className="w-8 h-8" />
                </div>
                <p className="text-sm font-semibold text-white mb-1">
                  Drag and drop Job Description here
                </p>
                <p className="text-xs text-gray-400 mb-3">Accepts PDF or DOCX up to 10MB</p>
                <span className="inline-flex items-center text-xs font-medium text-purple-400 bg-purple-500/10 px-3 py-1.5 rounded-full border border-purple-500/20">
                  Browse Files
                </span>
              </div>
            )
          ) : (
            /* Plaintext Mode */
            <div>
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste job description requirements, responsibilities & mandatory skills here..."
                className="w-full h-48 p-4 rounded-xl bg-[#0d0e15] border border-white/10 text-xs sm:text-sm text-gray-200 focus:outline-none focus:border-purple-500 transition-colors font-mono resize-none"
              />
              <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                <span>{jdText.length} characters</span>
                {jdText.length > 0 && (
                  <button type="button" onClick={() => setJdText('')} className="text-gray-400 hover:text-red-400">
                    Clear Text
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};
