import React, { useState, useEffect, useRef } from 'react';
import { AlertCircle, X } from 'lucide-react';
import { Navbar } from './components/Navbar';
import { DocumentInput } from './components/DocumentInput';
import { ProcessingProgress } from './components/ProcessingProgress';
import { SummaryView } from './components/SummaryView';
import { 
  uploadDocument, ingestText, ingestUrl, 
  getDocumentStatus, analyzeDocument
} from './api';
import type { DocumentInfo, DocumentStatusResponse, AnalysisResponse } from './types';

export const App: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<'input' | 'processing' | 'summary'>('input');
  const [processingStatus, setProcessingStatus] = useState<DocumentStatusResponse | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const pollIntervalRef = useRef<any>(null);

  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  useEffect(() => {
    return () => stopPolling();
  }, []);

  const handleIngestFile = async (file: File): Promise<DocumentInfo> => {
    setIsLoading(true);
    setGlobalError(null);
    try {
      const doc = await uploadDocument(file);
      return doc;
    } finally {
      setIsLoading(false);
    }
  };

  const handleIngestText = async (text: string, title?: string): Promise<DocumentInfo> => {
    setIsLoading(true);
    setGlobalError(null);
    try {
      const doc = await ingestText(text, title);
      return doc;
    } finally {
      setIsLoading(false);
    }
  };

  const handleIngestUrl = async (url: string, title?: string): Promise<DocumentInfo> => {
    setIsLoading(true);
    setGlobalError(null);
    try {
      const doc = await ingestUrl(url, title);
      return doc;
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartAnalysis = async (
    docId: string,
    options: {
      instructions: string;
      topic_of_interest: string;
      detail_level: string;
      confirm_healthcare_override: boolean;
    }
  ) => {
    setCurrentStep('processing');
    setGlobalError(null);

    // Initial status
    setProcessingStatus({
      id: docId,
      status: 'processing',
      current_stage: 'Stage 4: Linguistic analysis',
      stages_completed: ['Stage 1: Content extraction', 'Stage 2: Text cleaning and normalization', 'Stage 3: Research-section identification'],
      progress_percentage: 30,
      message: 'Beginning linguistic analysis and entity recognition...'
    });

    // Start polling status
    pollIntervalRef.current = setInterval(async () => {
      try {
        const stat = await getDocumentStatus(docId);
        setProcessingStatus(stat);
        if (stat.status === 'completed' || stat.status === 'failed') {
          stopPolling();
        }
      } catch {
        // Polling warning
      }
    }, 600);

    try {
      const result = await analyzeDocument(docId, options);
      stopPolling();
      setAnalysisResult(result);
      setCurrentStep('summary');
    } catch (err: any) {
      stopPolling();
      const msg = err.response?.data?.detail || err.message || 'Analysis pipeline failed or timed out.';
      setGlobalError(msg);
      setCurrentStep('input');
    }
  };

  const handleReset = () => {
    stopPolling();
    setProcessingStatus(null);
    setAnalysisResult(null);
    setGlobalError(null);
    setCurrentStep('input');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 pb-12 sm:pb-16">
        {globalError && (
          <div className="max-w-4xl mx-auto px-3 sm:px-4 mt-4 sm:mt-6">
            <div className="p-3.5 sm:p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs sm:text-sm flex items-start sm:items-center justify-between gap-3">
              <div className="flex items-center space-x-2 min-w-0">
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                <span className="break-words min-w-0">{globalError}</span>
              </div>
              <button 
                onClick={() => setGlobalError(null)}
                className="text-xs text-rose-400 hover:text-white flex items-center space-x-1 font-semibold cursor-pointer flex-shrink-0"
              >
                <span>Dismiss</span>
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {currentStep === 'input' && (
          <DocumentInput
            onIngestFile={handleIngestFile}
            onIngestText={handleIngestText}
            onIngestUrl={handleIngestUrl}
            onStartAnalysis={handleStartAnalysis}
            isLoading={isLoading}
          />
        )}

        {currentStep === 'processing' && (
          <ProcessingProgress status={processingStatus} />
        )}

        {currentStep === 'summary' && analysisResult && (
          <SummaryView analysis={analysisResult} onReset={handleReset} />
        )}
      </main>
    </div>
  );
};

export default App;
