# document_section_router_iii.py
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sqlalchemy.orm import Session

from backend.modules.db import (
    UploadedFile,
    get_db,
)

from .services.document_section_service_iii import (
    DocumentSectionServiceIII,
    DocumentSectionResult,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/section3",
    tags=["Document Section III"]
)


# -------------------------------------------
# Request Model serice etc
class SectionRequest(BaseModel):
    file_id: int

section_service = DocumentSectionServiceIII()


# -------------------------------------------------------
# Analyse Sections

@router.post(
    "/document",
    response_model=DocumentSectionResult
)
async def analyse_sections(request: SectionRequest):

    logger.info("Document section analysis requested.")

    # Get uploaded file from database
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

    # ---------------------------
    # Check file exists
    path = Path(uploaded.storage_path)
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {uploaded.storage_path}"
        )
    logger.info(
        "Sending document to AI for section analysis..."
    )

    # -------------------------------------------------
    # Call Section Service
    result = section_service.analyse_sections(
        request.file_id,
        uploaded.storage_path
    )

    # ----------------------------------------------
    # Check result
    if not result.success:

        logger.error(result.error)

        raise HTTPException(
            status_code=500,
            detail=result.error
        )

    logger.info(
        "Document section analysis complete."
    )

    return result

