from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class TextIngestRequest(BaseModel):
    text: str = Field(..., min_length=50, description="Raw text of the research paper")
    title: Optional[str] = Field(None, description="Optional title of the paper")

class UrlIngestRequest(BaseModel):
    url: str = Field(..., description="Accessible URL of the research paper (HTML or PDF)")
    title: Optional[str] = Field(None, description="Optional title of the paper")

class HealthcareValidationResult(BaseModel):
    is_healthcare: bool
    confidence: float
    category: str
    reasons: List[str]
    detected_terms: List[str]
    requires_confirmation: bool = False

class DocumentInfo(BaseModel):
    id: str
    title: str
    input_type: str
    filename: Optional[str] = None
    url: Optional[str] = None
    character_count: int
    word_count: int
    page_count: int = 1
    domain_validation: HealthcareValidationResult
    detected_sections: List[str] = []
    status: str = "ingested"
    created_at: datetime

class StageExecutionRecord(BaseModel):
    stage_id: str
    stage_name: str
    status: str  # "completed", "running", "pending"
    summary: str
    details: str
    metrics: Dict[str, Any] = {}

class DocumentStatusResponse(BaseModel):
    id: str
    status: str  # "ingested", "processing", "completed", "failed", "rejected"
    current_stage: Optional[str] = None
    stages_completed: List[str] = []
    progress_percentage: int = 0
    message: Optional[str] = None
    error: Optional[str] = None
    stage_records: List[StageExecutionRecord] = []
