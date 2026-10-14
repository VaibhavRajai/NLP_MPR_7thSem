export interface HealthcareValidationResult {
  is_healthcare: boolean;
  confidence: number;
  category: string;
  reasons: string[];
  detected_terms: string[];
  requires_confirmation: boolean;
}

export interface DocumentInfo {
  id: string;
  title: string;
  input_type: string;
  filename?: string;
  url?: string;
  character_count: number;
  word_count: number;
  page_count: number;
  domain_validation: HealthcareValidationResult;
  detected_sections: string[];
  status: string;
  created_at: string;
}

export interface StageExecutionRecord {
  stage_id: string;
  stage_name: string;
  status: 'completed' | 'running' | 'pending';
  summary: string;
  details: string;
  metrics?: Record<string, any>;
}

export interface DocumentStatusResponse {
  id: string;
  status: 'ingested' | 'processing' | 'completed' | 'failed' | 'rejected';
  current_stage?: string;
  stages_completed: string[];
  progress_percentage: number;
  message?: string;
  error?: string;
  stage_records?: StageExecutionRecord[];
}

export interface CitationReference {
  citation_id: string;
  sentence_id: string;
  section: string;
  page: number;
  original_text: string;
}

export interface BiomedicalEntity {
  text: string;
  category: 'Disease' | 'Medication' | 'Hospital' | 'Biomarker' | 'MedicalDevice' | 'PatientPopulation' | 'ClinicalOutcome' | 'Measurement' | 'Location';
  start_char: number;
  end_char: number;
  section: string;
  page: number;
  confidence: number;
}

export interface EntityRelation {
  source_entity: string;
  source_category: string;
  relation_type: string;
  target_entity: string;
  target_category: string;
  evidence_sentence: string;
  section: string;
  page: number;
  confidence: number;
}

export interface StatisticalFinding {
  metric: string;
  value: string;
  sample_size?: string;
  p_value?: string;
  confidence_interval?: string;
  context_sentence: string;
  section: string;
  page: number;
}

export interface SummarySection {
  title: string;
  content: string;
  key_points: string[];
  citation_ids: string[];
}

export interface MethodologyInfo {
  study_type: string;
  sample_size?: string;
  duration?: string;
  controls_or_groups?: string;
  primary_endpoint?: string;
  statistical_methods: string[];
}

export interface AnalysisResponse {
  document_id: string;
  title: string;
  executive_summary: string;
  structured_sections: SummarySection[];
  key_findings: string[];
  methodology: MethodologyInfo;
  statistical_findings: StatisticalFinding[];
  entities_by_category: Record<string, BiomedicalEntity[]>;
  entity_relationships: EntityRelation[];
  study_limitations: string[];
  clinical_implications: string[];
  citations: CitationReference[];
  processing_stages_completed: string[];
  domain_validation: HealthcareValidationResult;
  instruction_focus_applied?: string;
  summary_method?: string;
  query_applied?: string;
  stage_records?: StageExecutionRecord[];
}
