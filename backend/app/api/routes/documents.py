from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional
from backend.app.api.schemas.document import (
    TextIngestRequest, UrlIngestRequest, DocumentInfo, DocumentStatusResponse
)
from backend.app.services.document_service import DocumentService
from backend.app.storage.repository import repository

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    doc = await DocumentService.ingest_file(file)
    return DocumentInfo(
        id=doc["id"],
        title=doc["title"],
        input_type=doc["input_type"],
        filename=doc.get("filename"),
        url=doc.get("url"),
        character_count=doc["character_count"],
        word_count=doc["word_count"],
        page_count=doc["page_count"],
        domain_validation=doc["domain_validation"],
        detected_sections=doc["detected_sections"],
        status=doc["status"],
        created_at=doc["created_at"]
    )

@router.post("/text", response_model=DocumentInfo)
def ingest_text(req: TextIngestRequest):
    doc = DocumentService.ingest_pasted_text(req.text, req.title)
    return DocumentInfo(
        id=doc["id"],
        title=doc["title"],
        input_type=doc["input_type"],
        filename=doc.get("filename"),
        url=doc.get("url"),
        character_count=doc["character_count"],
        word_count=doc["word_count"],
        page_count=doc["page_count"],
        domain_validation=doc["domain_validation"],
        detected_sections=doc["detected_sections"],
        status=doc["status"],
        created_at=doc["created_at"]
    )

@router.post("/url", response_model=DocumentInfo)
def ingest_url(req: UrlIngestRequest):
    doc = DocumentService.ingest_url(req.url, req.title)
    return DocumentInfo(
        id=doc["id"],
        title=doc["title"],
        input_type=doc["input_type"],
        filename=doc.get("filename"),
        url=doc.get("url"),
        character_count=doc["character_count"],
        word_count=doc["word_count"],
        page_count=doc["page_count"],
        domain_validation=doc["domain_validation"],
        detected_sections=doc["detected_sections"],
        status=doc["status"],
        created_at=doc["created_at"]
    )

@router.get("/{document_id}", response_model=DocumentInfo)
def get_document_info(document_id: str):
    doc = repository.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentInfo(
        id=doc["id"],
        title=doc["title"],
        input_type=doc["input_type"],
        filename=doc.get("filename"),
        url=doc.get("url"),
        character_count=doc["character_count"],
        word_count=doc["word_count"],
        page_count=doc["page_count"],
        domain_validation=doc["domain_validation"],
        detected_sections=doc["detected_sections"],
        status=doc["status"],
        created_at=doc["created_at"]
    )

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(document_id: str):
    stat = repository.get_status(document_id)
    if not stat:
        raise HTTPException(status_code=404, detail="Status for document not found")
    return DocumentStatusResponse(**stat)
