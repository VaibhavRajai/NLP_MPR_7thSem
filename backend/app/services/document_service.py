import uuid
import os
import shutil
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from datetime import datetime, timezone

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.nlp.extraction import DocumentExtractor
from backend.app.nlp.cleaning import TextCleaner
from backend.app.nlp.section_detection import SectionDetector
from backend.app.services.healthcare_classifier import HealthcareDomainClassifier
from backend.app.storage.repository import repository

class DocumentService:
    @staticmethod
    def _create_and_validate_document(
        raw_blocks: list,
        input_type: str,
        filename: Optional[str] = None,
        url: Optional[str] = None,
        user_title: Optional[str] = None
    ) -> Dict[str, Any]:
        if not raw_blocks:
            raise HTTPException(status_code=400, detail="Document contains no extractable text.")

        # Clean blocks
        cleaned_blocks = TextCleaner.clean_blocks(raw_blocks)
        if not cleaned_blocks:
            raise HTTPException(status_code=400, detail="Extracted text was empty or corrupted after normalization.")

        # Detect sections
        segmented_sections = SectionDetector.segment_document(cleaned_blocks)
        detected_section_names = [k for k, v in segmented_sections.items() if len(v) > 0 and k != "title_metadata"]

        # Paper title
        paper_title = user_title or SectionDetector.extract_paper_title(cleaned_blocks)
        total_text = " ".join([b["text"] for b in cleaned_blocks])

        # Domain classification
        domain_val = HealthcareDomainClassifier.classify_document(paper_title, total_text)

        doc_id = str(uuid.uuid4())
        page_count = max([b.get("page", 1) for b in cleaned_blocks], default=1)

        doc_data = {
            "id": doc_id,
            "title": paper_title,
            "input_type": input_type,
            "filename": filename,
            "url": url,
            "raw_blocks": raw_blocks,
            "cleaned_blocks": cleaned_blocks,
            "segmented_sections": segmented_sections,
            "detected_sections": detected_section_names,
            "character_count": len(total_text),
            "word_count": len(total_text.split()),
            "page_count": page_count,
            "domain_validation": domain_val,
            "status": "ingested",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        repository.save_document(doc_id, doc_data)
        return doc_data

    @staticmethod
    async def ingest_file(file: UploadFile) -> Dict[str, Any]:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Supported formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Save to disk
        file_id = str(uuid.uuid4())
        saved_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        try:
            with open(saved_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Check size
            file_size_mb = os.path.getsize(saved_path) / (1024 * 1024)
            if file_size_mb > settings.MAX_FILE_SIZE_MB:
                os.remove(saved_path)
                raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB.")

            # Extract based on extension
            if ext == ".pdf":
                raw_blocks = DocumentExtractor.extract_from_pdf(saved_path)
            elif ext == ".docx":
                raw_blocks = DocumentExtractor.extract_from_docx(saved_path)
            elif ext == ".txt":
                with open(saved_path, "r", encoding="utf-8", errors="ignore") as f:
                    txt_content = f.read()
                raw_blocks = DocumentExtractor.extract_from_txt(txt_content)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format.")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to process file {file.filename}: {e}")
            raise HTTPException(status_code=400, detail=f"Error reading or parsing document: {str(e)}")
        finally:
            # Clean up uploaded file from storage
            if os.path.exists(saved_path):
                os.remove(saved_path)

        return DocumentService._create_and_validate_document(
            raw_blocks=raw_blocks,
            input_type="file_upload",
            filename=file.filename
        )

    @staticmethod
    def ingest_pasted_text(text: str, title: Optional[str] = None) -> Dict[str, Any]:
        if len(text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Pasted text is too short. Please provide a complete paper or abstract.")
        
        raw_blocks = DocumentExtractor.extract_from_txt(text)
        return DocumentService._create_and_validate_document(
            raw_blocks=raw_blocks,
            input_type="pasted_text",
            user_title=title
        )

    @staticmethod
    def ingest_url(url: str, title: Optional[str] = None) -> Dict[str, Any]:
        if not url.startswith("http://") and not url.startswith("https://"):
            raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http:// or https://")

        try:
            raw_blocks = DocumentExtractor.extract_from_url(url)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch research paper from URL: {str(e)}")

        return DocumentService._create_and_validate_document(
            raw_blocks=raw_blocks,
            input_type="url_ingest",
            url=url,
            user_title=title
        )
