import React from 'react';
import { motion } from 'framer-motion';
import { Mail, Phone, MapPin, Briefcase, GraduationCap, Building2, Globe, ExternalLink } from 'lucide-react';
import type { CandidateProfileSchema } from '../types';

interface CandidateProfileProps {
  profile: CandidateProfileSchema;
}

export const CandidateProfile: React.FC<CandidateProfileProps> = ({ profile }) => {
  const getInitials = (name: string | null) => {
    if (!name) return 'C';
    return name
      .split(' ')
      .map((part) => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 mb-8"
    >
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-6 border-b border-white/10 mb-6">
        {/* Left: Avatar & Main Bio */}
        <div className="flex items-center space-x-5">
          {/* Avatar Placeholder */}
          <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 p-0.5 shadow-xl shrink-0">
            <div className="w-full h-full bg-[#0d0e15] rounded-[14px] flex items-center justify-center font-heading font-black text-xl sm:text-2xl text-indigo-300">
              {getInitials(profile.name)}
            </div>
          </div>

          <div>
            <h3 className="font-heading font-extrabold text-2xl text-white tracking-tight">
              {profile.name || 'Candidate Profile'}
            </h3>
            <p className="text-sm font-medium text-indigo-400 mb-2">
              {profile.current_designation || 'Software Professional'}
            </p>

            <div className="flex flex-wrap gap-4 text-xs text-gray-400">
              {profile.email && (
                <div className="flex items-center space-x-1.5">
                  <Mail className="w-3.5 h-3.5 text-gray-500" />
                  <span>{profile.email}</span>
                </div>
              )}
              {profile.phone && (
                <div className="flex items-center space-x-1.5">
                  <Phone className="w-3.5 h-3.5 text-gray-500" />
                  <span>{profile.phone}</span>
                </div>
              )}
              {profile.location && (
                <div className="flex items-center space-x-1.5">
                  <MapPin className="w-3.5 h-3.5 text-gray-500" />
                  <span>{profile.location}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: External Web Links */}
        <div className="flex items-center space-x-3">
          {profile.links.github && (
            <a
              href={profile.links.github.startsWith('http') ? profile.links.github : `https://${profile.links.github}`}
              target="_blank"
              rel="noreferrer"
              className="p-3 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/10 transition-colors flex items-center space-x-2 text-xs"
            >
              <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              <span>GitHub</span>
              <ExternalLink className="w-3 h-3 text-gray-500" />
            </a>
          )}

          {profile.links.linkedin && (
            <a
              href={profile.links.linkedin.startsWith('http') ? profile.links.linkedin : `https://${profile.links.linkedin}`}
              target="_blank"
              rel="noreferrer"
              className="p-3 rounded-xl bg-blue-600/10 hover:bg-blue-600/20 text-blue-300 border border-blue-500/20 transition-colors flex items-center space-x-2 text-xs"
            >
              <svg className="w-4 h-4 fill-current text-blue-400" viewBox="0 0 24 24">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
              </svg>
              <span>LinkedIn</span>
              <ExternalLink className="w-3 h-3 text-blue-400/50" />
            </a>
          )}

          {profile.links.portfolio && (
            <a
              href={profile.links.portfolio.startsWith('http') ? profile.links.portfolio : `https://${profile.links.portfolio}`}
              target="_blank"
              rel="noreferrer"
              className="p-3 rounded-xl bg-purple-600/10 hover:bg-purple-600/20 text-purple-300 border border-purple-500/20 transition-colors flex items-center space-x-2 text-xs"
            >
              <Globe className="w-4 h-4 text-purple-400" />
              <span>Portfolio</span>
              <ExternalLink className="w-3 h-3 text-purple-400/50" />
            </a>
          )}
        </div>
      </div>

      {/* Grid Specs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Experience */}
        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-gray-400 block">Total Experience</span>
            <span className="font-heading font-bold text-base text-white">
              {profile.total_years_experience} Years
            </span>
          </div>
        </div>

        {/* Education */}
        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-gray-400 block">Highest Degree</span>
            <span className="font-heading font-bold text-base text-white">
              {profile.highest_degree || 'Graduate Degree'}{' '}
              {profile.degree_branch ? `(${profile.degree_branch})` : ''}
            </span>
          </div>
        </div>

        {/* Companies */}
        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-teal-500/10 text-teal-400">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-gray-400 block">Companies Worked At</span>
            <div className="flex flex-wrap gap-1 mt-0.5">
              {profile.company_names.length > 0 ? (
                profile.company_names.map((comp, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-white/5 text-xs text-gray-300 font-mono">
                    {comp}
                  </span>
                ))
              ) : (
                <span className="text-xs text-gray-500 italic">Not extracted</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
