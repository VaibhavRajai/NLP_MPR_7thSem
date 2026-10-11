import React from 'react';
import { Activity, ShieldCheck, Stethoscope } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-2.5 sm:space-x-3 min-w-0">
          <div className="w-9 h-9 sm:w-10 sm:h-10 bg-gradient-to-tr from-teal-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-teal-500/20 flex-shrink-0">
            <Stethoscope className="w-5 h-5 sm:w-6 sm:h-6 text-slate-950 font-bold" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center space-x-1.5 sm:space-x-2">
              <span className="font-bold text-base sm:text-lg text-white tracking-tight truncate">MediSummarize</span>
              <span className="px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs font-semibold bg-teal-500/10 text-teal-400 border border-teal-500/30 whitespace-nowrap">
                Healthcare NLP
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-400 truncate hidden xs:block">
              Clinical Research Paper Synthesizer & Evidence Grounding
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-4 text-xs text-slate-300 flex-shrink-0">
          <div className="hidden lg:flex items-center space-x-1.5 bg-slate-800/80 px-3 py-1.5 border border-slate-700/60">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Healthcare Domain Only</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-slate-800/80 px-2.5 py-1 sm:px-3 sm:py-1.5 border border-slate-700/60 text-[11px] sm:text-xs">
            <Activity className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-cyan-400 animate-pulse" />
            <span className="text-slate-200">10-Stage Pipeline</span>
          </div>
        </div>
      </div>
    </header>
  );
};
