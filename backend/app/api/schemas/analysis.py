from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AnalyzeRequest(BaseModel):
    instructions: Optional[str] = Field(None, description="Custom natural language summarization instructions")
    topic_of_interest: Optional[str] = Field(None, description="Optional focused topic")
    detail_level: str = Field("balanced", description="Summary detail level: concise, balanced, or detailed")
    confirm_healthcare_override: bool = Field(False, description="User confirmation to proceed if domain is borderline")

class CitationReference(BaseModel):
    citation_id: str
    sentence_id: str
    section: str
    page: int
    original_text: str

class BiomedicalEntity(BaseModel):
    text: str
    category: str  # Disease, Medication, Hospital, Biomarker, MedicalDevice, PatientPopulation, ClinicalOutcome, Measurement
    start_char: int
    end_char: int
    section: str
    page: int
    confidence: float

class EntityRelation(BaseModel):
    source_entity: str
    source_category: str
    relation_type: str  # treats, associated_with, investigated_by, conducted_at, measured, resulted_in
    target_entity: str
    target_category: str
    evidence_sentence: str
    section: str
    page: int
    confidence: float

class StatisticalFinding(BaseModel):
    metric: str
    value: str
    sample_size: Optional[str] = None
    p_value: Optional[str] = None
    confidence_interval: Optional[str] = None
    context_sentence: str
    section: str
    page: int

class SummarySection(BaseModel):
    title: str
    content: str
    key_points: List[str] = []
    citation_ids: List[str] = []

class MethodologyInfo(BaseModel):
    study_type: str
    sample_size: Optional[str] = None
    duration: Optional[str] = None
    controls_or_groups: Optional[str] = None
    primary_endpoint: Optional[str] = None
    statistical_methods: List[str] = []

from backend.app.api.schemas.document import StageExecutionRecord

class AnalysisResponse(BaseModel):
    document_id: str
    title: str
    executive_summary: str
    structured_sections: List[SummarySection]
    key_findings: List[str]
    methodology: MethodologyInfo
    statistical_findings: List[StatisticalFinding]
    entities_by_category: Dict[str, List[BiomedicalEntity]]
    entity_relationships: List[EntityRelation]
    study_limitations: List[str]
    clinical_implications: List[str]
    citations: List[CitationReference]
    processing_stages_completed: List[str]
    domain_validation: Dict[str, Any]
    instruction_focus_applied: Optional[str] = None
    summary_method: Optional[str] = None
    query_applied: Optional[str] = None
    stage_records: List[StageExecutionRecord] = []
