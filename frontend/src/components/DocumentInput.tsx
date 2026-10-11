import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Globe, AlertTriangle, ArrowRight, CheckCircle2, Sparkles } from 'lucide-react';
import type { DocumentInfo } from '../types';

interface DocumentInputProps {
  onIngestFile: (file: File) => Promise<DocumentInfo>;
  onIngestText: (text: string, title?: string) => Promise<DocumentInfo>;
  onIngestUrl: (url: string, title?: string) => Promise<DocumentInfo>;
  onStartAnalysis: (docId: string, options: { instructions: string; topic_of_interest: string; detail_level: string; confirm_healthcare_override: boolean }) => void;
  isLoading: boolean;
}

const INSTRUCTION_SUGGESTIONS = [
  "Focus on methodology and study design",
  "Highlight statistical results, p-values, and sample size",
  "Summarize treatment effectiveness and adverse events",
  "Explain findings in accessible patient-friendly language",
  "Identify healthcare institutions and hospital affiliations",
  "Focus on study limitations and future implications"
];

export const DocumentInput: React.FC<DocumentInputProps> = ({
  onIngestFile,
  onIngestText,
  onIngestUrl,
  onStartAnalysis,
  isLoading
}) => {
  const [activeTab, setActiveTab] = useState<'upload' | 'paste' | 'url'>('upload');
  
  // File state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Text state
  const [pastedText, setPastedText] = useState('');
  const [textTitle, setTextTitle] = useState('');

  // URL state
  const [paperUrl, setPaperUrl] = useState('');
  const [urlTitle, setUrlTitle] = useState('');

  // Instructions & options
  const [instructions, setInstructions] = useState('');
  const [topicOfInterest, setTopicOfInterest] = useState('');
  const [detailLevel, setDetailLevel] = useState<'concise' | 'balanced' | 'detailed'>('balanced');

  // Ingested document state (for review & domain check)
  const [ingestedDoc, setIngestedDoc] = useState<DocumentInfo | null>(null);
  const [ingestError, setIngestError] = useState<string | null>(null);
  const [confirmBorderline, setConfirmBorderline] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!['.pdf', '.docx', '.txt'].includes(ext)) {
      setIngestError(`Invalid file format '${ext}'. Please upload a PDF, DOCX, or TXT file.`);
      return;
    }
    setSelectedFile(file);
    setIngestError(null);
  };

  const handleProceedIngest = async () => {
    setIngestError(null);
    try {
      let doc: DocumentInfo;
      if (activeTab === 'upload') {
        if (!selectedFile) {
          setIngestError('Please select a PDF, DOCX, or TXT file to upload.');
          return;
        }
        doc = await onIngestFile(selectedFile);
      } else if (activeTab === 'paste') {
        if (!pastedText.trim() || pastedText.trim().length < 50) {
          setIngestError('Please paste at least 50 characters of research paper text.');
          return;
        }
        doc = await onIngestText(pastedText, textTitle || undefined);
      } else {
        if (!paperUrl.trim() || !paperUrl.startsWith('http')) {
          setIngestError('Please enter a valid research paper URL starting with http:// or https://');
          return;
        }
        doc = await onIngestUrl(paperUrl, urlTitle || undefined);
      }

      setIngestedDoc(doc);
    } catch (err: any) {
      setIngestError(err.response?.data?.detail || err.message || 'Failed to ingest research paper.');
    }
  };

  const handleTriggerFinalAnalysis = () => {
    if (!ingestedDoc) return;
    onStartAnalysis(ingestedDoc.id, {
      instructions,
      topic_of_interest: topicOfInterest,
      detail_level: detailLevel,
      confirm_healthcare_override: confirmBorderline
    });
  };

  return (
    <div className="w-full max-w-4xl mx-auto py-5 sm:py-8 px-3 sm:px-6">
      {/* Intro Header */}
      <div className="text-center mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-white tracking-tight px-2 leading-tight">
          Healthcare Research Paper Summarizer
        </h1>
        <p className="mt-2.5 sm:mt-3 text-xs sm:text-sm md:text-base text-slate-400 max-w-2xl mx-auto px-2">
          Multi-stage NLP analysis for clinical trials, epidemiology, pharmacology, and medical studies.
          Extracts evidence, preserves clinical uncertainties, and cites original sources.
        </p>
      </div>

      {/* Main Ingest Box */}
      <div className="bg-slate-900/90 border border-slate-800 shadow-xl overflow-hidden p-4 sm:p-7 md:p-8">
        
        {!ingestedDoc ? (
          <>
            {/* Input Method Navigation Tabs (Responsive scrollable container) */}
            <div className="flex border-b border-slate-800 mb-5 sm:mb-6 overflow-x-auto no-scrollbar gap-1">
              <button
                type="button"
                onClick={() => { setActiveTab('upload'); setIngestError(null); }}
                className={`flex items-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 font-semibold text-xs sm:text-sm border-b-2 whitespace-nowrap transition flex-shrink-0 cursor-pointer ${
                  activeTab === 'upload'
                    ? 'border-teal-400 text-teal-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <UploadCloud className="w-4 h-4" />
                <span>Upload Document</span>
              </button>

              <button
                type="button"
                onClick={() => { setActiveTab('paste'); setIngestError(null); }}
                className={`flex items-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 font-semibold text-xs sm:text-sm border-b-2 whitespace-nowrap transition flex-shrink-0 cursor-pointer ${
                  activeTab === 'paste'
                    ? 'border-teal-400 text-teal-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>Paste Text</span>
              </button>

              <button
                type="button"
                onClick={() => { setActiveTab('url'); setIngestError(null); }}
                className={`flex items-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 font-semibold text-xs sm:text-sm border-b-2 whitespace-nowrap transition flex-shrink-0 cursor-pointer ${
                  activeTab === 'url'
                    ? 'border-teal-400 text-teal-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Globe className="w-4 h-4" />
                <span>Research Paper URL</span>
              </button>
            </div>

            {/* TAB 1: File Upload */}
            {activeTab === 'upload' && (
              <div>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => e.target.files?.[0] && handleFileSelected(e.target.files[0])}
                  accept=".pdf,.docx,.txt"
                  className="hidden"
                />

                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed p-5 sm:p-8 text-center cursor-pointer transition ${
                    dragActive
                      ? 'border-teal-400 bg-teal-500/5'
                      : selectedFile
                      ? 'border-emerald-500/60 bg-emerald-500/5'
                      : 'border-slate-700 hover:border-slate-500 bg-slate-950/50'
                  }`}
                >
                  <div className="w-11 h-11 sm:w-14 sm:h-14 mx-auto mb-3 sm:mb-4 bg-slate-800 flex items-center justify-center text-teal-400">
                    <UploadCloud className="w-6 h-6 sm:w-7 sm:h-7" />
                  </div>
                  {selectedFile ? (
                    <div>
                      <p className="font-semibold text-emerald-400 text-sm sm:text-base break-all">{selectedFile.name}</p>
                      <p className="text-xs text-slate-400 mt-1">
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Tap or click to replace file
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="font-medium text-slate-200 text-xs sm:text-sm">
                        Drag and drop your research paper here, or <span className="text-teal-400 underline font-semibold">browse files</span>
                      </p>
                      <p className="text-[11px] sm:text-xs text-slate-500 mt-1.5 sm:mt-2">
                        Supported formats: PDF (native & scanned), DOCX, TXT (up to 30MB)
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* TAB 2: Pasted Text */}
            {activeTab === 'paste' && (
              <div className="space-y-3.5 sm:space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Paper Title (Optional)
                  </label>
                  <input
                    type="text"
                    value={textTitle}
                    onChange={(e) => setTextTitle(e.target.value)}
                    placeholder="e.g. Efficacy and Safety of GLP-1 Receptor Agonists in Adults with Type 2 Diabetes"
                    className="w-full bg-slate-950 border border-slate-700 px-3.5 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Research Paper Content / Abstract
                  </label>
                  <textarea
                    rows={7}
                    value={pastedText}
                    onChange={(e) => setPastedText(e.target.value)}
                    placeholder="Paste the full text, abstract, methodology, or results of the healthcare research paper here..."
                    className="w-full bg-slate-950 border border-slate-700 p-3 sm:p-4 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 font-mono text-[11px] sm:text-xs leading-relaxed"
                  />
                  <div className="text-right text-[11px] text-slate-500 mt-1">
                    {pastedText.length} characters
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: URL Ingest */}
            {activeTab === 'url' && (
              <div className="space-y-3.5 sm:space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Paper Title (Optional)
                  </label>
                  <input
                    type="text"
                    value={urlTitle}
                    onChange={(e) => setUrlTitle(e.target.value)}
                    placeholder="e.g. Phase 3 Results from Lancet / PubMed"
                    className="w-full bg-slate-950 border border-slate-700 px-3.5 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Public Research Paper URL (HTML or PDF)
                  </label>
                  <input
                    type="url"
                    value={paperUrl}
                    onChange={(e) => setPaperUrl(e.target.value)}
                    placeholder="https://example-journal.org/article/covid19-trial.pdf"
                    className="w-full bg-slate-950 border border-slate-700 px-3.5 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500"
                  />
                  <p className="text-[11px] sm:text-xs text-slate-500 mt-1.5">
                    Accepts direct open-access scientific publications and article URLs. SSRF protections active.
                  </p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {ingestError && (
              <div className="mt-4 p-3.5 sm:p-4 bg-rose-500/10 border border-rose-500/30 flex items-start space-x-2.5 sm:space-x-3 text-rose-300 text-xs sm:text-sm">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400 mt-0.5" />
                <div className="min-w-0">
                  <strong className="block font-semibold">Validation Notice:</strong>
                  <span className="break-words">{ingestError}</span>
                </div>
              </div>
            )}

            {/* Proceed Ingestion Button (full width on mobile, right aligned on desktop) */}
            <div className="mt-5 sm:mt-6 flex flex-col sm:flex-row justify-end">
              <button
                type="button"
                onClick={handleProceedIngest}
                disabled={isLoading}
                className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs sm:text-sm shadow-lg shadow-teal-500/25 transition disabled:opacity-50 cursor-pointer"
              >
                <span>{isLoading ? 'Ingesting Document...' : 'Verify Paper & Continue'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </>
        ) : (
          /* STEP 2: Configure Instructions and Confirm Domain */
          <div className="space-y-5 sm:space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div className="min-w-0">
                <span className="text-[11px] font-mono uppercase tracking-wider text-teal-400 font-semibold">
                  Document Ingested
                </span>
                <h3 className="text-base sm:text-lg font-bold text-white mt-0.5 line-clamp-1 break-words">{ingestedDoc.title}</h3>
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 mt-1">
                  <span>{ingestedDoc.word_count.toLocaleString()} words</span>
                  <span>•</span>
                  <span>{ingestedDoc.page_count} {ingestedDoc.page_count === 1 ? 'page' : 'pages'}</span>
                  <span>•</span>
                  <span className="text-teal-400 font-medium capitalize">{ingestedDoc.domain_validation.category}</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => { setIngestedDoc(null); setSelectedFile(null); }}
                className="text-xs text-slate-400 hover:text-white px-3 py-1.5 border border-slate-700 hover:bg-slate-800 transition w-fit cursor-pointer"
              >
                Change Paper
              </button>
            </div>

            {/* Domain Validation Feedback */}
            {ingestedDoc.domain_validation.is_healthcare ? (
              <div className="p-3.5 sm:p-4 bg-teal-500/10 border border-teal-500/30 flex items-start space-x-2.5 sm:space-x-3 text-teal-200 text-xs">
                <CheckCircle2 className="w-5 h-5 text-teal-400 flex-shrink-0 mt-0.5" />
                <div className="space-y-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                    <span className="font-bold text-xs sm:text-sm text-teal-300">Healthcare Domain Confirmed</span>
                    <span className="bg-teal-500/20 text-teal-300 px-2 py-0.5 font-mono text-[11px]">
                      {(ingestedDoc.domain_validation.confidence * 100).toFixed(0)}% Confidence
                    </span>
                  </div>
                  <p className="text-slate-300 text-xs">{ingestedDoc.domain_validation.reasons[0]}</p>
                </div>
              </div>
            ) : (
              <div className="p-3.5 sm:p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs space-y-2.5 sm:space-y-3">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />
                  <span className="font-bold text-xs sm:text-sm text-rose-200">Domain Restriction Notice</span>
                </div>
                <p className="text-xs leading-relaxed">
                  This application strictly synthesizes healthcare, clinical, biomedical, and pharmaceutical research papers.
                  The uploaded document was classified as non-healthcare with {(ingestedDoc.domain_validation.confidence * 100).toFixed(0)}% confidence.
                </p>
                <div className="flex items-start space-x-2 pt-1.5">
                  <input
                    type="checkbox"
                    id="overrideCheck"
                    checked={confirmBorderline}
                    onChange={(e) => setConfirmBorderline(e.target.checked)}
                    className="border-slate-700 text-teal-500 focus:ring-teal-500 bg-slate-950 mt-0.5"
                  />
                  <label htmlFor="overrideCheck" className="text-slate-200 cursor-pointer text-xs">
                    I confirm this paper contains legitimate healthcare research and request analysis override.
                  </label>
                </div>
              </div>
            )}

            {/* Custom Instructions */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex flex-wrap justify-between gap-1">
                <span>Custom Summarization Instructions (Optional)</span>
                <span className="text-slate-500 font-normal">Natural language directives</span>
              </label>
              <textarea
                rows={3}
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                placeholder="e.g. Focus on study limitations, explain treatment effectiveness in simple terms, or emphasize sample size and statistics..."
                className="w-full bg-slate-950 border border-slate-700 p-3 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 leading-relaxed"
              />

              {/* Responsive Suggestion Chips */}
              <div className="flex flex-wrap gap-1.5 mt-2">
                {INSTRUCTION_SUGGESTIONS.map((chip, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setInstructions(chip)}
                    className="text-[11px] sm:text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-300 px-2 sm:px-2.5 py-1 border border-slate-700/60 transition cursor-pointer text-left"
                  >
                    + {chip}
                  </button>
                ))}
              </div>
            </div>

            {/* Focused Topic of Interest */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Optional Topic of Interest / Key Parameter
              </label>
              <input
                type="text"
                value={topicOfInterest}
                onChange={(e) => setTopicOfInterest(e.target.value)}
                placeholder="e.g. mortality rate, HbA1c reduction, adverse reactions, biomarker evaluation"
                className="w-full bg-slate-950 border border-slate-700 px-3.5 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500"
              />
            </div>

            {/* Summary Detail Level Toggle (Responsive 1-col on mobile, 3-col on desktop) */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">
                Summary Detail Level
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3">
                {[
                  { id: 'concise', label: 'Concise', desc: '5 core evidence points' },
                  { id: 'balanced', label: 'Balanced', desc: '8 structured synthesis sections' },
                  { id: 'detailed', label: 'Detailed', desc: '14 comprehensive findings & context' }
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setDetailLevel(item.id as any)}
                    className={`p-3 border text-left transition cursor-pointer ${
                      detailLevel === item.id
                        ? 'border-teal-400 bg-teal-500/10 text-white shadow-sm shadow-teal-500/10'
                        : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div className="font-semibold text-xs sm:text-sm">{item.label}</div>
                    <div className="text-[11px] sm:text-xs text-slate-500 mt-0.5">{item.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Start Pipeline Button (Full width on mobile, right aligned on desktop) */}
            <div className="pt-3 sm:pt-4 flex flex-col sm:flex-row justify-end">
              <button
                type="button"
                onClick={handleTriggerFinalAnalysis}
                disabled={isLoading || (!ingestedDoc.domain_validation.is_healthcare && !confirmBorderline)}
                className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 sm:px-8 py-3.5 bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs sm:text-sm shadow-xl shadow-teal-500/25 transition disabled:opacity-40 cursor-pointer"
              >
                <Sparkles className="w-4 h-4 sm:w-5 sm:h-5" />
                <span>Run 10-Stage NLP Pipeline</span>
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
