# app/analysis_router.py
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sqlalchemy.orm import Session

from backend.modules.db import (
    UploadedFile,
    get_db,
)

from .services.document_analysis_service import (
    DocumentAnalysisService,
    DocumentAnalysisResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analysis",
    tags=["Document Analysis"]
)


# ------------------------------------------------------------
# Request Model & service

class AnalysisRequest(BaseModel):
    file_id: int

analysis_service = DocumentAnalysisService()


# -------------------------------------------
# Load document to be analysed 
@router.post(
    "/document",
    response_model=DocumentAnalysisResult
)
async def analyse_document(request: AnalysisRequest):

    logger.info("Document analysis requested.")
    db: Session = next(get_db())

    uploaded = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == request.file_id)
        .first()
    )

    if uploaded is None:
        raise HTTPException(
            status_code=404,
            detail=f"Uploaded file ID {request.file_id} not found."
        )

    logger.info(
        "Found uploaded file: %s",
        uploaded.filename
    )

    path = Path(uploaded.storage_path)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {uploaded.storage_path}"
        )
    logger.info(
        "Sending document to AI for semantic analysis..."
    )

    # -----------------------------------------------
    # Call Document Analysis Service

    result = analysis_service.analyse_document(
        uploaded.storage_path
    )

    if not result.success:
        logger.error(result.error)
        raise HTTPException(
            status_code=500,
            detail=result.error
        )

    logger.info(
        "Document analysed successfully."
    )

    return result