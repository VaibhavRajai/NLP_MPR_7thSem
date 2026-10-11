from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.app.api.schemas.analysis import AnalyzeRequest, AnalysisResponse
from backend.app.services.summary_service import SummaryService
from backend.app.storage.repository import repository
from backend.app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Analysis"])

@router.post("/{document_id}/analyze", response_model=AnalysisResponse)
def trigger_analysis(
    document_id: str,
    req: AnalyzeRequest,
    background_tasks: BackgroundTasks = None
):
    doc = repository.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        # Run pipeline synchronously for direct response or when invoked
        analysis_res = SummaryService.run_pipeline(
            doc_id=document_id,
            instructions=req.instructions,
            topic_of_interest=req.topic_of_interest,
            detail_level=req.detail_level,
            confirm_healthcare_override=req.confirm_healthcare_override
        )
        return AnalysisResponse(**analysis_res)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing document {document_id}: {e}")
        repository.update_status(
            document_id,
            status="failed",
            error=str(e),
            message=f"Pipeline execution encountered an error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

@router.get("/{document_id}/summary", response_model=AnalysisResponse)
def get_summary(document_id: str):
    analysis = repository.get_analysis(document_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Summary not found for this document. Please trigger /analyze first.")
    return AnalysisResponse(**analysis)
