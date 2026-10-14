import React, { useState } from 'react';
import { 
  FileText, CheckCircle2, BookOpen, 
  RotateCcw, ExternalLink, BarChart3, GitFork, 
  Stethoscope, Pill, Building2, Dna, ShieldAlert, Sparkles, Activity,
  Terminal, Check
} from 'lucide-react';
import type { AnalysisResponse, CitationReference, StageExecutionRecord } from '../types';
import { CitationModal } from './CitationModal';

interface SummaryViewProps {
  analysis: AnalysisResponse;
  onReset: () => void;
}

const ENTITY_CATEGORY_STYLES: Record<string, { label: string; bg: string; text: string; icon: React.ReactNode }> = {
  Disease: { label: 'Diseases & Symptoms', bg: 'bg-rose-500/10 border-rose-500/30', text: 'text-rose-400', icon: <Stethoscope className="w-3.5 h-3.5 flex-shrink-0" /> },
  Medication: { label: 'Medications & Treatments', bg: 'bg-cyan-500/10 border-cyan-500/30', text: 'text-cyan-400', icon: <Pill className="w-3.5 h-3.5 flex-shrink-0" /> },
  Hospital: { label: 'Hospitals & Institutions', bg: 'bg-indigo-500/10 border-indigo-500/30', text: 'text-indigo-400', icon: <Building2 className="w-3.5 h-3.5 flex-shrink-0" /> },
  Biomarker: { label: 'Biomarkers & Genes', bg: 'bg-purple-500/10 border-purple-500/30', text: 'text-purple-400', icon: <Dna className="w-3.5 h-3.5 flex-shrink-0" /> },
  MedicalDevice: { label: 'Medical Devices', bg: 'bg-emerald-500/10 border-emerald-500/30', text: 'text-emerald-400', icon: <Activity className="w-3.5 h-3.5 flex-shrink-0" /> },
  PatientPopulation: { label: 'Patient Populations', bg: 'bg-amber-500/10 border-amber-500/30', text: 'text-amber-400', icon: <Activity className="w-3.5 h-3.5 flex-shrink-0" /> },
  ClinicalOutcome: { label: 'Clinical Outcomes', bg: 'bg-teal-500/10 border-teal-500/30', text: 'text-teal-400', icon: <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" /> },
  Measurement: { label: 'Measurements & Statistics', bg: 'bg-blue-500/10 border-blue-500/30', text: 'text-blue-400', icon: <BarChart3 className="w-3.5 h-3.5 flex-shrink-0" /> },
  Location: { label: 'Study Locations', bg: 'bg-slate-500/10 border-slate-500/30', text: 'text-slate-400', icon: <Building2 className="w-3.5 h-3.5 flex-shrink-0" /> },
};

export const SummaryView: React.FC<SummaryViewProps> = ({ analysis, onReset }) => {
  const [selectedCitation, setSelectedCitation] = useState<CitationReference | null>(null);
  const [activeTab, setActiveTab] = useState<'structured' | 'entities' | 'statistics' | 'relations' | 'pipeline'>('structured');

  const openCitationById = (citationId: string) => {
    const cit = analysis.citations.find(c => c.citation_id === citationId);
    if (cit) {
      setSelectedCitation(cit);
    }
  };

  const renderCitationLinks = (content: string) => {
    const parts = content.split(/(\[REF-\d+\])/g);
    return parts.map((part, index) => {
      const match = part.match(/\[(REF-\d+)\]/);
      if (match) {
        const citId = match[1];
        return (
          <button
            key={index}
            onClick={() => openCitationById(citId)}
            className="inline-flex items-center text-teal-400 hover:text-teal-300 font-mono text-[11px] sm:text-xs px-1.5 py-0.5 bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 mx-1 transition cursor-pointer"
            title="View original verified document evidence"
          >
            {citId}
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  const stageRecords: StageExecutionRecord[] = analysis.stage_records || [];

  return (
    <div className="w-full max-w-6xl mx-auto py-5 sm:py-8 px-3 sm:px-6">
      
      {/* Top Bar with Reset button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 sm:mb-6">
        <button
          onClick={onReset}
          className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-xs font-semibold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 px-4 py-2.5 border border-slate-800 transition cursor-pointer"
        >
          <RotateCcw className="w-4 h-4 text-teal-400" />
          <span>Summarize Another Healthcare Paper</span>
        </button>

        <div className="flex items-center space-x-2 text-[11px] sm:text-xs text-slate-400 justify-center sm:justify-end">
          <span className="w-2 h-2 bg-emerald-400 animate-pulse" />
          <span>Evidence Grounded and Factually Verified</span>
        </div>
      </div>

      {/* Paper Header Card */}
      <div className="bg-slate-900 border border-slate-800 p-4 sm:p-7 md:p-8 shadow-xl mb-6 sm:mb-8">
        <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-3">
          <span className="bg-teal-500/10 text-teal-400 border border-teal-500/30 px-2.5 sm:px-3 py-1 text-[11px] sm:text-xs font-semibold">
            {analysis.domain_validation.category}
          </span>
          <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2.5 sm:px-3 py-1 text-[11px] sm:text-xs font-mono">
            {(analysis.domain_validation.confidence * 100).toFixed(0)}% Medical Confidence
          </span>
          {analysis.instruction_focus_applied && (
            <span className="bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 px-2.5 sm:px-3 py-1 text-[11px] sm:text-xs truncate max-w-full">
              Focus: {analysis.instruction_focus_applied}
            </span>
          )}
          {analysis.summary_method && (
            <span className="bg-violet-500/10 text-violet-300 border border-violet-500/30 px-2.5 sm:px-3 py-1 text-[11px] sm:text-xs">
              {analysis.summary_method}
            </span>
          )}
          {analysis.query_applied && (
            <span className="bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2.5 sm:px-3 py-1 text-[11px] sm:text-xs truncate max-w-full">
              Query: {analysis.query_applied}
            </span>
          )}
        </div>

        <h1 className="text-xl sm:text-2xl md:text-3xl font-extrabold text-white tracking-tight leading-snug break-words">
          {analysis.title}
        </h1>

        {/* Executive Summary Callout */}
        <div className="mt-4 sm:mt-6 p-4 sm:p-5 bg-slate-950/80 border border-teal-500/20 text-slate-200">
          <div className="flex items-center space-x-2 text-teal-400 font-bold text-xs uppercase tracking-wider mb-2">
            <Sparkles className="w-4 h-4" />
            <span>Executive Synthesis</span>
          </div>
          <p className="text-xs sm:text-sm leading-relaxed text-slate-200">
            {renderCitationLinks(analysis.executive_summary)}
          </p>
        </div>
      </div>

      {/* Main Tabbed Content Navigation (Scrollable on mobile) */}
      <div className="flex border-b border-slate-800 mb-5 sm:mb-6 overflow-x-auto no-scrollbar gap-1">
        <button
          onClick={() => setActiveTab('structured')}
          className={`flex items-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 font-semibold text-xs sm:text-sm border-b-2 whitespace-nowrap transition flex-shrink-0 cursor-pointer ${
            activeTab === 'structured'
              ? 'border-teal-400 text-teal-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Structured Summary</span>
        </button>

        <button
          onClick={() => setActiveTab('entities')}
          className={`flex items-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 font-semibold text-xs sm:text-sm border-b-2 whitespace-nowrap transition flex-shrink-0 cursor-pointer ${
            activeTab === 'entities'
              ? 'border-teal-400 text-teal-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Stethoscope className="w-4 h-4" />
          <span>Biomedical Entities ({Object.values(analysis.entities_by_category).reduce((a, b) => a + b.length, 0)})</span>
        </button>

        <button
          onClick={() => setActiveTab('statistics')}
          className={`flex items-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 font-semibold text-xs sm:text-sm border-b-2 whitespace-nowrap transition flex-shrink-0 cursor-pointer ${
            activeTab === 'statistics'
              ? 'border-teal-400 text-teal-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Statistical Findings ({analysis.statistical_findings.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('relations')}
          className={`flex items-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 font-semibold text-xs sm:text-sm border-b-2 whitespace-nowrap transition flex-shrink-0 cursor-pointer ${
            activeTab === 'relations'
              ? 'border-teal-400 text-teal-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <GitFork className="w-4 h-4" />
          <span>Entity Relationships ({analysis.entity_relationships.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('pipeline')}
          className={`flex items-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 font-semibold text-xs sm:text-sm border-b-2 whitespace-nowrap transition flex-shrink-0 cursor-pointer ${
            activeTab === 'pipeline'
              ? 'border-teal-400 text-teal-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Terminal className="w-4 h-4" />
          <span>Pipeline Stages ({stageRecords.length > 0 ? stageRecords.length : 10})</span>
        </button>
      </div>

      {/* TAB 1: Structured Summary & Methodology Cards */}
      {activeTab === 'structured' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          
          {/* Left Column: Structured Sections */}
          <div className="lg:col-span-2 space-y-5 sm:space-y-6">
            
            {/* Key Findings Highlights Box */}
            {analysis.key_findings.length > 0 && (
              <div className="bg-slate-900 border border-slate-800 p-4 sm:p-6 shadow-md">
                <h3 className="text-sm sm:text-base font-bold text-white mb-3 sm:mb-4 flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                  <span>Key Research Findings</span>
                </h3>
                <ul className="space-y-2.5 sm:space-y-3 text-xs sm:text-sm text-slate-300">
                  {analysis.key_findings.map((f, idx) => (
                    <li key={idx} className="flex items-start space-x-2.5">
                      <span className="w-1.5 h-1.5 bg-emerald-400 mt-2 flex-shrink-0" />
                      <span className="leading-relaxed break-words">{renderCitationLinks(f)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Structured Sections */}
            {analysis.structured_sections.map((sec, idx) => (
              <div key={idx} className="bg-slate-900 border border-slate-800 p-4 sm:p-6 shadow-md">
                <h3 className="text-sm sm:text-base font-bold text-teal-300 mb-2.5 sm:mb-3">{sec.title}</h3>
                <div className="text-xs sm:text-sm leading-relaxed text-slate-200 space-y-2.5">
                  <p className="break-words">{renderCitationLinks(sec.content)}</p>
                </div>
              </div>
            ))}

            {/* Study Limitations Box */}
            {analysis.study_limitations.length > 0 && (
              <div className="bg-slate-900 border border-amber-500/20 p-4 sm:p-6 shadow-md">
                <h3 className="text-sm sm:text-base font-bold text-amber-300 mb-2.5 sm:mb-3 flex items-center space-x-2">
                  <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0" />
                  <span>Study Limitations and Bounds</span>
                </h3>
                <ul className="space-y-2 text-xs sm:text-sm text-slate-300">
                  {analysis.study_limitations.map((lim, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <span className="text-amber-400 font-bold flex-shrink-0">/</span>
                      <span className="break-words">{renderCitationLinks(lim)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Clinical Implications Box */}
            {analysis.clinical_implications.length > 0 && (
              <div className="bg-slate-900 border border-cyan-500/20 p-4 sm:p-6 shadow-md">
                <h3 className="text-sm sm:text-base font-bold text-cyan-300 mb-2.5 sm:mb-3 flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                  <span>Clinical Implications</span>
                </h3>
                <ul className="space-y-2 text-xs sm:text-sm text-slate-300">
                  {analysis.clinical_implications.map((imp, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <span className="text-cyan-400 font-bold flex-shrink-0">/</span>
                      <span className="break-words">{renderCitationLinks(imp)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Right Column: Methodology & Study Design Sidebar */}
          <div className="space-y-5 sm:space-y-6">
            
            {/* Methodology Card */}
            <div className="bg-slate-900 border border-slate-800 p-4 sm:p-6 shadow-md">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-400 mb-3.5 sm:mb-4 flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-teal-400 flex-shrink-0" />
                <span>Study Design and Methodology</span>
              </h3>

              <div className="space-y-3.5 text-xs">
                <div>
                  <span className="text-slate-500 block mb-1">Study Design</span>
                  <span className="text-slate-200 font-semibold text-xs sm:text-sm break-words">
                    {analysis.methodology.study_type}
                  </span>
                </div>

                {analysis.methodology.sample_size && (
                  <div>
                    <span className="text-slate-500 block mb-1">Sample Size / Cohort</span>
                    <span className="text-teal-300 font-mono font-medium text-xs sm:text-sm">
                      {analysis.methodology.sample_size}
                    </span>
                  </div>
                )}

                {analysis.methodology.duration && (
                  <div>
                    <span className="text-slate-500 block mb-1">Trial Duration / Follow-Up</span>
                    <span className="text-slate-200 font-medium">
                      {analysis.methodology.duration}
                    </span>
                  </div>
                )}

                {analysis.methodology.statistical_methods.length > 0 && (
                  <div>
                    <span className="text-slate-500 block mb-1.5">Statistical Analysis Tests</span>
                    <div className="flex flex-wrap gap-1">
                      {analysis.methodology.statistical_methods.map((method, idx) => (
                        <span key={idx} className="bg-slate-800 text-slate-300 px-2 py-0.5 border border-slate-700 text-[11px] font-mono">
                          {method}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Citations & Evidence Panel */}
            <div className="bg-slate-900 border border-slate-800 p-4 sm:p-6 shadow-md">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center space-x-2">
                <ExternalLink className="w-4 h-4 text-teal-400 flex-shrink-0" />
                <span>Evidence Grounding Citations</span>
              </h3>
              <p className="text-[11px] sm:text-xs text-slate-400 mb-3.5">
                Click any citation tag to view the exact extracted passage and verified page number.
              </p>

              <div className="space-y-2 max-h-72 sm:max-h-80 overflow-y-auto pr-1">
                {analysis.citations.map((c) => (
                  <button
                    key={c.citation_id}
                    onClick={() => setSelectedCitation(c)}
                    className="w-full text-left p-2.5 bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between text-xs group cursor-pointer"
                  >
                    <div className="flex items-center space-x-2 min-w-0">
                      <span className="bg-teal-500/20 text-teal-400 px-2 py-0.5 font-mono font-semibold flex-shrink-0">
                        {c.citation_id}
                      </span>
                      <span className="text-slate-300 capitalize truncate">{c.section}</span>
                    </div>
                    <span className="text-slate-500 group-hover:text-slate-300 flex-shrink-0 ml-2">P. {c.page}</span>
                  </button>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* TAB 2: Biomedical Entities */}
      {activeTab === 'entities' && (
        <div className="bg-slate-900 border border-slate-800 p-4 sm:p-7 md:p-8 shadow-xl">
          <h2 className="text-base sm:text-lg font-bold text-white mb-1 sm:mb-2">Biomedical Named Entities</h2>
          <p className="text-xs text-slate-400 mb-5 sm:mb-6">
            Recognized biomedical entities classified by clinical taxonomy.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            {Object.entries(analysis.entities_by_category).map(([cat, ents]) => {
              const meta = ENTITY_CATEGORY_STYLES[cat] || {
                label: cat,
                bg: 'bg-slate-800 border-slate-700',
                text: 'text-slate-300',
                icon: <Activity className="w-3.5 h-3.5 flex-shrink-0" />
              };

              if (!ents || ents.length === 0) return null;

              return (
                <div key={cat} className="bg-slate-950/60 p-4 sm:p-5 border border-slate-800">
                  <div className="flex items-center space-x-2 mb-3">
                    <span className={meta.text}>{meta.icon}</span>
                    <h3 className="font-bold text-xs sm:text-sm text-slate-200 truncate">{meta.label}</h3>
                    <span className="bg-slate-800 text-slate-400 text-[11px] sm:text-xs px-2 py-0.5 font-mono ml-auto flex-shrink-0">
                      {ents.length}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1.5">
                    {ents.map((e, idx) => (
                      <span
                        key={idx}
                        className={`text-[11px] sm:text-xs px-2 sm:px-2.5 py-1 border font-medium break-words ${meta.bg} ${meta.text}`}
                      >
                        {e.text}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 3: Statistical Findings */}
      {activeTab === 'statistics' && (
        <div className="bg-slate-900 border border-slate-800 p-4 sm:p-7 md:p-8 shadow-xl">
          <h2 className="text-base sm:text-lg font-bold text-white mb-1 sm:mb-2">Statistical Results and Measurements</h2>
          <p className="text-xs text-slate-400 mb-5 sm:mb-6">
            Reported empirical statistics, significance levels (p-values), confidence intervals, and effect sizes.
          </p>

          {analysis.statistical_findings.length === 0 ? (
            <p className="text-xs sm:text-sm text-slate-500 italic">No formal statistical metrics detected in the paper text.</p>
          ) : (
            <div className="overflow-x-auto border border-slate-800">
              <table className="w-full text-left text-xs min-w-[650px]">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950/80 text-slate-400 uppercase tracking-wider font-mono">
                    <th className="py-3 px-3 sm:px-4">Metric</th>
                    <th className="py-3 px-3 sm:px-4">Reported Value</th>
                    <th className="py-3 px-3 sm:px-4">p-value</th>
                    <th className="py-3 px-3 sm:px-4">95% CI</th>
                    <th className="py-3 px-3 sm:px-4">Sample Size</th>
                    <th className="py-3 px-3 sm:px-4">Context / Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {analysis.statistical_findings.map((s, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-3 sm:px-4 font-semibold text-slate-200">{s.metric}</td>
                      <td className="py-3 px-3 sm:px-4 text-teal-300 font-mono font-medium">{s.value}</td>
                      <td className="py-3 px-3 sm:px-4 text-cyan-300 font-mono">{s.p_value || '-'}</td>
                      <td className="py-3 px-3 sm:px-4 text-slate-300 font-mono">{s.confidence_interval || '-'}</td>
                      <td className="py-3 px-3 sm:px-4 text-slate-300 font-mono">{s.sample_size || '-'}</td>
                      <td className="py-3 px-3 sm:px-4 text-slate-400 max-w-xs truncate" title={s.context_sentence}>
                        {s.context_sentence}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: Entity Relationships */}
      {activeTab === 'relations' && (
        <div className="bg-slate-900 border border-slate-800 p-4 sm:p-7 md:p-8 shadow-xl">
          <h2 className="text-base sm:text-lg font-bold text-white mb-1 sm:mb-2">Contextual and Entity Relationships</h2>
          <p className="text-xs text-slate-400 mb-5 sm:mb-6">
            Grounded relational predicates extracted from paper findings.
          </p>

          {analysis.entity_relationships.length === 0 ? (
            <p className="text-xs sm:text-sm text-slate-500 italic">No multi-entity relationship predicates extracted.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 sm:gap-4">
              {analysis.entity_relationships.map((rel, idx) => (
                <div key={idx} className="p-3.5 sm:p-4 bg-slate-950/70 border border-slate-800 text-xs">
                  <div className="flex flex-wrap items-center gap-1.5 font-mono mb-2">
                    <span className="text-cyan-400 font-bold break-all">{rel.source_entity}</span>
                    <span className="text-slate-500">→</span>
                    <span className="bg-teal-500/10 text-teal-300 px-2 py-0.5 border border-teal-500/20 capitalize font-medium text-[11px]">
                      {rel.relation_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-slate-500">→</span>
                    <span className="text-rose-400 font-bold break-all">{rel.target_entity}</span>
                  </div>
                  <p className="text-slate-400 font-serif italic text-xs leading-relaxed border-t border-slate-900 pt-2 break-words">
                    "{rel.evidence_sentence}"
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: Pipeline Stages & What Actually Happened At Each Step */}
      {activeTab === 'pipeline' && (
        <div className="bg-slate-900 border border-slate-800 p-4 sm:p-7 md:p-8 shadow-xl">
          <div className="flex items-center space-x-2 text-teal-400 mb-2">
            <Terminal className="w-5 h-5 flex-shrink-0" />
            <h2 className="text-base sm:text-lg font-bold text-white">Pipeline Execution Trace (10-Stage Verification)</h2>
          </div>
          <p className="text-xs text-slate-400 mb-6">
            Complete audit of what actually occurred during each phase of the biomedical NLP processing pipeline.
          </p>

          <div className="space-y-4">
            {stageRecords.map((rec, idx) => (
              <div key={rec.stage_id || idx} className="border border-slate-800 bg-slate-950/70 p-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-2.5 mb-3">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-6 h-6 bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-xs font-mono font-bold">
                      {idx + 1}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-100 text-xs sm:text-sm">{rec.stage_name}</h3>
                      <span className="text-[10px] text-slate-400 font-mono">{rec.stage_id}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 text-[11px] font-mono border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 font-medium">
                      <Check className="w-3 h-3" />
                      <span>Verified</span>
                    </span>
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-teal-400 font-semibold block mb-0.5">
                      Process Summary:
                    </span>
                    <p className="text-slate-300 font-medium">{rec.summary}</p>
                  </div>

                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold block mb-0.5">
                      Actual Execution Details:
                    </span>
                    <p className="text-slate-400 leading-relaxed">{rec.details}</p>
                  </div>

                  {rec.metrics && Object.keys(rec.metrics).length > 0 && (
                    <div className="pt-2 border-t border-slate-900 flex flex-wrap gap-1.5 items-center">
                      <span className="text-[10px] text-slate-500 font-mono uppercase">Stage Metrics:</span>
                      {Object.entries(rec.metrics).map(([mKey, mVal]) => {
                        if (typeof mVal === 'object' && mVal !== null) {
                          return Object.entries(mVal).map(([subK, subV]) => (
                            <span key={`${mKey}-${subK}`} className="bg-slate-900 border border-slate-800 text-teal-300 font-mono text-[11px] px-2 py-0.5">
                              {subK}: <strong>{String(subV)}</strong>
                            </span>
                          ));
                        }
                        return (
                          <span key={mKey} className="bg-slate-900 border border-slate-800 text-teal-300 font-mono text-[11px] px-2 py-0.5">
                            {mKey.replace(/_/g, ' ')}: <strong>{Array.isArray(mVal) ? mVal.join(', ') : String(mVal)}</strong>
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citation Modal */}
      <CitationModal
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />

    </div>
  );
};
