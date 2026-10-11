import React, { useState } from 'react';
import { Loader2, CheckCircle2, Clock, AlertCircle, ChevronDown, ChevronUp, Terminal } from 'lucide-react';
import type { DocumentStatusResponse, StageExecutionRecord } from '../types';

interface ProcessingProgressProps {
  status: DocumentStatusResponse | null;
}

const DEFAULT_STAGE_METRICS_INFO: Record<string, { label: string; actionDesc: string }> = {
  'Stage 1: Content extraction': {
    label: '1. Content Extraction',
    actionDesc: 'Parsed native layout blocks, paragraphs, and exact page coordinates from the research document.'
  },
  'Stage 2: Text cleaning and normalization': {
    label: '2. Text Cleaning & Normalization',
    actionDesc: 'Reconstructed broken line-wraps and hyphenations while strictly preserving clinical dosages, abbreviations, and statistical notations.'
  },
  'Stage 3: Research-section identification': {
    label: '3. Research-Section Identification',
    actionDesc: 'Classified document content blocks into standard scientific IMRaD taxonomy sections (Abstract, Methods, Results, Discussion, Limitations).'
  },
  'Stage 4: Linguistic analysis': {
    label: '4. Linguistic Analysis',
    actionDesc: 'Segmented clinical sentences with decimal safeguards; evaluated NegEx clinical negation rules and detected hedging uncertainty markers.'
  },
  'Stage 5: Biomedical named entity recognition': {
    label: '5. Biomedical Named Entity Recognition',
    actionDesc: 'Classified biomedical entities across diseases & symptoms, medications & treatments, healthcare institutions, biomarkers, and medical devices.'
  },
  'Stage 6: Contextual and relationship analysis': {
    label: '6. Contextual & Relationship Analysis',
    actionDesc: 'Extracted relational predicates mapping treatments to clinical outcomes and medical centers to clinical cohorts.'
  },
  'Stage 7: Semantic representation': {
    label: '7. Semantic Embeddings & Representation',
    actionDesc: 'Constructed contextual section chunks with dense semantic embeddings and TF-IDF representations for evidence retrieval.'
  },
  'Stage 8: Extractive summarization': {
    label: '8. TextRank Sentence Centrality & MMR',
    actionDesc: 'Formed sentence similarity graph, computed PageRank graph centrality, and applied Maximal Marginal Relevance (MMR) for diversity.'
  },
  'Stage 9: Custom instruction interpretation': {
    label: '9. Custom Instruction Interpretation',
    actionDesc: 'Parsed natural-language user directives to modulate section retrieval weights, summary length quotas, and clinical priorities.'
  },
  'Stage 10: Constructive summary generation & validation': {
    label: '10. Grounded Synthesis & Citation Validation',
    actionDesc: 'Generated constructive multi-section synthesis; grounded each finding to source sentences and verified page coordinates [REF-X].'
  }
};

const ORDERED_STAGES = [
  'Stage 1: Content extraction',
  'Stage 2: Text cleaning and normalization',
  'Stage 3: Research-section identification',
  'Stage 4: Linguistic analysis',
  'Stage 5: Biomedical named entity recognition',
  'Stage 6: Contextual and relationship analysis',
  'Stage 7: Semantic representation',
  'Stage 8: Extractive summarization',
  'Stage 9: Custom instruction interpretation',
  'Stage 10: Constructive summary generation & validation'
];

export const ProcessingProgress: React.FC<ProcessingProgressProps> = ({ status }) => {
  const [expandedStages, setExpandedStages] = useState<Record<string, boolean>>({
    'Stage 1: Content extraction': true,
    'Stage 2: Text cleaning and normalization': true,
    'Stage 3: Research-section identification': true,
    'Stage 4: Linguistic analysis': true,
    'Stage 5: Biomedical named entity recognition': true,
  });

  const toggleStage = (id: string) => {
    setExpandedStages(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const completedStages = status?.stages_completed || [];
  const currentStage = status?.current_stage;
  const progressPercent = status?.progress_percentage || 15;
  const stageRecords = status?.stage_records || [];

  const getStageRecord = (stageId: string): StageExecutionRecord | undefined => {
    return stageRecords.find(r => r.stage_id === stageId);
  };

  return (
    <div className="w-full max-w-4xl mx-auto py-6 sm:py-10 px-3 sm:px-6">
      <div className="bg-slate-900 border border-slate-800 p-4 sm:p-7 md:p-8 shadow-2xl">
        <div className="text-center mb-6 sm:mb-8">
          <div className="inline-flex p-3 bg-teal-500/10 text-teal-400 mb-2.5 sm:mb-3 border border-teal-500/20">
            <Loader2 className="w-6 h-6 sm:w-7 sm:h-7 animate-spin" />
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-white px-2 tracking-tight">
            Synthesizing Healthcare Research Paper
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl mx-auto px-2">
            {status?.message || 'Executing biomedical NLP pipeline stages and validating source evidence...'}
          </p>

          {/* Progress Bar (Square Edges) */}
          <div className="w-full bg-slate-950 h-2.5 mt-5 sm:mt-6 border border-slate-800 overflow-hidden">
            <div
              className="bg-gradient-to-r from-teal-500 to-cyan-400 h-full transition-all duration-500 ease-out"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className="flex justify-between items-center text-[11px] sm:text-xs text-slate-500 mt-2 font-mono">
            <span>Overall Progress: {progressPercent}%</span>
            <span>{completedStages.length} of {ORDERED_STAGES.length} Stages Completed</span>
          </div>
        </div>

        {/* Section Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-4">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
            <Terminal className="w-4 h-4 text-teal-400" />
            <span>Process Execution Trace & Stage Audit</span>
          </div>
          <button
            type="button"
            onClick={() => {
              const allExpanded = ORDERED_STAGES.every(s => expandedStages[s]);
              const nextState: Record<string, boolean> = {};
              ORDERED_STAGES.forEach(s => { nextState[s] = !allExpanded; });
              setExpandedStages(nextState);
            }}
            className="text-[11px] text-teal-400 hover:text-teal-300 cursor-pointer font-medium"
          >
            {ORDERED_STAGES.every(s => expandedStages[s]) ? 'Collapse All' : 'Expand All'}
          </button>
        </div>

        {/* Process Steps */}
        <div className="space-y-3">
          {ORDERED_STAGES.map((stageId) => {
            const isCompleted = completedStages.includes(stageId);
            const isCurrent = currentStage === stageId || (!isCompleted && completedStages.length === 0 && stageId.startsWith('Stage 1'));
            const record = getStageRecord(stageId);
            const stageMeta = DEFAULT_STAGE_METRICS_INFO[stageId] || {
              label: stageId,
              actionDesc: 'Executing NLP processing pipeline stage.'
            };
            const isExpanded = expandedStages[stageId] ?? (isCompleted || isCurrent);

            return (
              <div
                key={stageId}
                className={`border transition ${
                  isCompleted
                    ? 'border-emerald-500/30 bg-emerald-500/5'
                    : isCurrent
                    ? 'border-teal-400/50 bg-teal-500/10 shadow-lg shadow-teal-500/5'
                    : 'border-slate-800 bg-slate-950/40 text-slate-500'
                }`}
              >
                {/* Stage Header Row */}
                <button
                  type="button"
                  onClick={() => toggleStage(stageId)}
                  className="w-full p-3 sm:p-3.5 flex items-center justify-between gap-3 text-left cursor-pointer"
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-400 flex-shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 text-teal-400 animate-spin flex-shrink-0" />
                    ) : (
                      <Clock className="w-4 h-4 sm:w-5 sm:h-5 text-slate-600 flex-shrink-0" />
                    )}
                    <div className="min-w-0">
                      <div className={`font-semibold text-xs sm:text-sm ${
                        isCompleted ? 'text-slate-100' : isCurrent ? 'text-teal-300' : 'text-slate-400'
                      }`}>
                        {stageMeta.label}
                      </div>
                      <div className="text-[11px] sm:text-xs text-slate-400 font-normal truncate">
                        {record?.summary || stageMeta.actionDesc}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2.5 flex-shrink-0">
                    <div className="text-[11px] sm:text-xs font-mono">
                      {isCompleted ? (
                        <span className="text-emerald-400 font-medium px-2 py-0.5 border border-emerald-500/30 bg-emerald-500/10">Done</span>
                      ) : isCurrent ? (
                        <span className="text-teal-400 font-medium animate-pulse px-2 py-0.5 border border-teal-500/30 bg-teal-500/10">Running</span>
                      ) : (
                        <span className="text-slate-600 px-2 py-0.5 border border-slate-800 bg-slate-950">Pending</span>
                      )}
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </button>

                {/* What Actually Happened in this Process */}
                {isExpanded && (
                  <div className="px-3 pb-3 sm:px-4 sm:pb-3.5 pt-1 border-t border-slate-800/80 bg-slate-950/60 text-xs">
                    <div className="space-y-2">
                      <div>
                        <span className="text-[10px] font-mono uppercase tracking-wider text-teal-400 font-semibold block mb-0.5">
                          What actually occurred during this process:
                        </span>
                        <p className="text-slate-200 leading-relaxed text-xs">
                          {record?.details || stageMeta.actionDesc}
                        </p>
                      </div>

                      {/* Metrics and Counts Tag Cloud */}
                      {record?.metrics && Object.keys(record.metrics).length > 0 && (
                        <div className="pt-2 border-t border-slate-800/60 flex flex-wrap gap-1.5 items-center">
                          <span className="text-[10px] text-slate-400 font-mono uppercase">Metrics:</span>
                          {Object.entries(record.metrics).map(([key, val]) => {
                            if (typeof val === 'object' && val !== null) {
                              return Object.entries(val).map(([subK, subV]) => (
                                <span
                                  key={`${key}-${subK}`}
                                  className="font-mono text-[11px] bg-slate-900 border border-slate-700 text-teal-300 px-2 py-0.5"
                                >
                                  {subK}: <strong>{String(subV)}</strong>
                                </span>
                              ));
                            }
                            return (
                              <span
                                key={key}
                                className="font-mono text-[11px] bg-slate-900 border border-slate-700 text-teal-300 px-2 py-0.5"
                              >
                                {key.replace(/_/g, ' ')}: <strong>{Array.isArray(val) ? val.join(', ') : String(val)}</strong>
                              </span>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {status?.error && (
          <div className="mt-5 p-3.5 sm:p-4 bg-rose-500/10 border border-rose-500/30 flex items-start space-x-2.5 text-rose-300 text-xs sm:text-sm">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
            <span className="break-words min-w-0">{status.error}</span>
          </div>
        )}
      </div>
    </div>
  );
};
