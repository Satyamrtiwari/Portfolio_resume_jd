import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle2, X } from 'lucide-react';

interface ToastProps {
  message: string | null;
  type?: 'error' | 'warning' | 'success';
  onClose: () => void;
}

export const ToastNotification: React.FC<ToastProps> = ({ message, type = 'error', onClose }) => {
  return (
    <AnimatePresence>
      {message && (
        <motion.div
          initial={{ opacity: 0, y: -20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          className="fixed top-20 right-6 z-50 max-w-md w-full"
        >
          <div
            className={`p-4 rounded-xl border backdrop-blur-xl shadow-2xl flex items-center justify-between space-x-3 ${
              type === 'error'
                ? 'bg-red-950/90 text-red-200 border-red-500/40 shadow-red-900/30'
                : type === 'warning'
                ? 'bg-yellow-950/90 text-yellow-200 border-yellow-500/40 shadow-yellow-900/30'
                : 'bg-emerald-950/90 text-emerald-200 border-emerald-500/40 shadow-emerald-900/30'
            }`}
          >
            <div className="flex items-center space-x-3">
              {type === 'success' ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              )}
              <span className="text-xs sm:text-sm font-medium leading-normal">{message}</span>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
