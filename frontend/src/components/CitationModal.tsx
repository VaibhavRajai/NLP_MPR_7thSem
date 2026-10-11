import React from 'react';
import { X, BookOpen, MapPin, Hash } from 'lucide-react';
import type { CitationReference } from '../types';

interface CitationModalProps {
  citation: CitationReference | null;
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <div 
        className="bg-slate-900 border border-teal-500/30 max-w-xl w-full p-4 sm:p-6 shadow-2xl relative text-left max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 sm:top-4 sm:right-4 text-slate-400 hover:text-white p-1.5 hover:bg-slate-800 transition cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 text-teal-400 mb-2.5 sm:mb-3 pr-8">
          <BookOpen className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />
          <span className="font-semibold text-xs sm:text-sm uppercase tracking-wider">Source Citation Grounding</span>
          <span className="bg-teal-500/20 text-teal-300 text-[11px] sm:text-xs px-2 py-0.5 font-mono font-medium">
            {citation.citation_id}
          </span>
        </div>

        <h3 className="text-base sm:text-lg font-bold text-white mb-3 sm:mb-4">Original Extracted Document Evidence</h3>

        <div className="bg-slate-950/80 p-3.5 sm:p-4 border border-slate-800 mb-3.5 sm:mb-4 text-slate-200 text-xs sm:text-sm leading-relaxed font-serif break-words">
          "{citation.original_text}"
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 text-xs text-slate-400 pt-2 border-t border-slate-800/80">
          <div className="flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-cyan-400 flex-shrink-0" />
            <span className="truncate">Section: <strong className="text-slate-200 capitalize">{citation.section}</strong></span>
          </div>
          <div className="flex items-center space-x-2">
            <Hash className="w-4 h-4 text-cyan-400 flex-shrink-0" />
            <span>Page Number: <strong className="text-slate-200">{citation.page}</strong></span>
          </div>
        </div>

        <div className="mt-5 flex justify-end">
          <button
            onClick={onClose}
            className="w-full sm:w-auto px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition cursor-pointer text-center"
          >
            Close Reference
          </button>
        </div>
      </div>
    </div>
  );
};
