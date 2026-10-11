from typing import Dict, Any, Optional
import os
import json
from datetime import datetime

class DocumentRepository:
    def __init__(self):
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._statuses: Dict[str, Dict[str, Any]] = {}
        self._analyses: Dict[str, Dict[str, Any]] = {}

    def save_document(self, doc_id: str, doc_data: Dict[str, Any]):
        self._documents[doc_id] = doc_data
        
        raw_blocks_count = len(doc_data.get("raw_blocks", []))
        word_count = doc_data.get("word_count", 0)
        page_count = doc_data.get("page_count", 1)
        input_type = doc_data.get("input_type", "document")
        detected_sections = doc_data.get("detected_sections", [])

        initial_stage_records = [
            {
                "stage_id": "Stage 1: Content extraction",
                "stage_name": "Content Extraction",
                "status": "completed",
                "summary": f"Extracted {raw_blocks_count} structural blocks across {page_count} page(s) ({word_count:,} words) from {input_type}.",
                "details": f"Document structure parsed cleanly. Preserved pagination, line boundaries, and structural blocks.",
                "metrics": {"blocks": raw_blocks_count, "words": word_count, "pages": page_count}
            },
            {
                "stage_id": "Stage 2: Text cleaning and normalization",
                "stage_name": "Text Cleaning and Normalization",
                "status": "completed",
                "summary": "Normalized medical text flow, repaired line wraps, and preserved clinical abbreviations and units.",
                "details": "Repaired hyphenated line breaks. Preserved clinical abbreviations, laboratory units (e.g. mg, mmHg, mmol/L), negations, and statistical notations without truncation.",
                "metrics": {"cleaned_blocks": len(doc_data.get("cleaned_blocks", []))}
            },
            {
                "stage_id": "Stage 3: Research-section identification",
                "stage_name": "Research-Section Identification",
                "status": "completed",
                "summary": f"Identified {len(detected_sections)} research sections: {', '.join(detected_sections)}.",
                "details": "Detected canonical scientific sections (Title/Abstract, Introduction/Background, Methodology, Results/Findings, Discussion, Limitations, Conclusion).",
                "metrics": {"sections": detected_sections}
            }
        ]

        self._statuses[doc_id] = {
            "id": doc_id,
            "status": "ingested",
            "current_stage": None,
            "stages_completed": [
                "Stage 1: Content extraction",
                "Stage 2: Text cleaning and normalization",
                "Stage 3: Research-section identification"
            ],
            "progress_percentage": 0,
            "message": "Document ingested and ready for analysis",
            "error": None,
            "stage_records": initial_stage_records
        }

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self._documents.get(doc_id)

    def update_status(self, doc_id: str, status: str, current_stage: Optional[str] = None, 
                      stages_completed: Optional[list] = None, progress: int = 0, 
                      message: Optional[str] = None, error: Optional[str] = None,
                      stage_records: Optional[list] = None):
        current = self._statuses.get(doc_id, {"id": doc_id})
        current["status"] = status
        if current_stage is not None:
            current["current_stage"] = current_stage
        if stages_completed is not None:
            current["stages_completed"] = stages_completed
        current["progress_percentage"] = progress
        if message is not None:
            current["message"] = message
        if error is not None:
            current["error"] = error
        if stage_records is not None:
            current["stage_records"] = stage_records
        elif "stage_records" not in current:
            current["stage_records"] = []
        self._statuses[doc_id] = current

    def get_status(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self._statuses.get(doc_id)

    def save_analysis(self, doc_id: str, analysis_data: Dict[str, Any]):
        self._analyses[doc_id] = analysis_data

    def get_analysis(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self._analyses.get(doc_id)

repository = DocumentRepository()
