import React from 'react';
import { motion } from 'framer-motion';
import { FileText, FileCode2, Sliders, Cpu, Award, ArrowDown } from 'lucide-react';

interface Step {
  id: number;
  title: string;
  subtitle: string;
  icon: React.ElementType;
  gradient: string;
}

const steps: Step[] = [
  {
    id: 1,
    title: 'Upload Resume',
    subtitle: 'Upload PDF or DOCX candidate resume file, or paste plaintext.',
    icon: FileText,
    gradient: 'from-blue-500 to-indigo-600',
  },
  {
    id: 2,
    title: 'Upload Job Description',
    subtitle: 'Upload PDF or DOCX job requirements, or paste role details.',
    icon: FileCode2,
    gradient: 'from-indigo-500 to-purple-600',
  },
  {
    id: 3,
    title: 'Choose Strategy',
    subtitle: 'Select AUTO analysis, industry role preset, or custom weights.',
    icon: Sliders,
    gradient: 'from-purple-500 to-pink-600',
  },
  {
    id: 4,
    title: 'AI Analysis',
    subtitle: 'Generative AI entity extraction & BAAI/bge semantic embedding match.',
    icon: Cpu,
    gradient: 'from-pink-500 to-rose-600',
  },
  {
    id: 5,
    title: 'Recruiter Report',
    subtitle: 'Instantly view match score, ATS coverage, candidate profile & hiring risk.',
    icon: Award,
    gradient: 'from-emerald-500 to-teal-600',
  },
];

export const HowItWorks: React.FC = () => {
  return (
    <section id="how-it-works" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="font-heading text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
          How It Works
        </h2>
        <p className="text-gray-400 text-base sm:text-lg max-w-xl mx-auto font-normal">
          5 simple steps to transform raw resumes and job descriptions into actionable hiring intelligence.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              className="glass-card glass-card-hover p-6 rounded-2xl relative flex flex-col justify-between"
            >
              <div>
                {/* Step Number & Icon */}
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${step.gradient} p-0.5 shadow-lg`}>
                    <div className="w-full h-full bg-[#0d0e15] rounded-[10px] flex items-center justify-center">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <span className="font-mono text-2xl font-black text-gray-700">0{step.id}</span>
                </div>

                <h3 className="font-heading font-bold text-lg text-white mb-2">{step.title}</h3>
                <p className="text-xs text-gray-400 leading-relaxed">{step.subtitle}</p>
              </div>

              {/* Arrow Connector for Desktop */}
              {idx < steps.length - 1 && (
                <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                  <div className="w-6 h-6 rounded-full bg-[#141824] border border-white/10 flex items-center justify-center text-gray-500">
                    <span className="text-xs font-bold">→</span>
                  </div>
                </div>
              )}

              {/* Arrow Connector for Mobile */}
              {idx < steps.length - 1 && (
                <div className="md:hidden flex justify-center mt-4 text-gray-600">
                  <ArrowDown className="w-5 h-5 animate-bounce" />
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </section>
  );
};
