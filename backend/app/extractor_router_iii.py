#extractor_router_iii.py
# Week 11 - new extractor

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.extractor_service_iii import (
    ExtractorServiceIII,
)
logger = logging.getLogger(__name__)

# -------------------------------  -----------------
# Router
router = APIRouter(
    prefix="/extractor3",
    tags=["Extractor III"]
)

# -------------------------------------------------------
# Request which model and service to use
class ExtractionRequest(BaseModel):
    file_id: int

extractor_service = ExtractorServiceIII()

# ----------------------------------------------------
# Run Extractor III
@router.post(
    "/run"
)
async def run_extractor(
    request: ExtractionRequest
):
    logger.info(
        "=" * 60
    )
    logger.info(
        "Extractor III requested"
    )
    logger.info(
        "File ID : %s",
        request.file_id
    )
    logger.info(
        "=" * 60
    )
    result = extractor_service.extract_document(
        file_id=request.file_id
    )
    if not result.success:
        raise HTTPException(
            status_code=500,
            detail=result.error
        )
    return result


# Original version without document section divider
"""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.modules.db import (
    UploadedFile,
    get_db,
)
from backend.app.services.document_analysis_service import (
    DocumentAnalysisService,
)
from backend.app.services.extractor_service_iii import (
    ExtractorServiceIII,
)
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/extractor3",
    tags=["Extractor III"]
)


# ----------------------------------------------------
# Request & service
class ExtractionRequest(BaseModel):
    file_id: int

# ------------------------------------------------------------
# Services

analysis_service = DocumentAnalysisService()
extractor_service = ExtractorServiceIII()


# ---------------------------------------------------
# Endpoint

@router.post("/extract")
async def extract_document(
    request: ExtractionRequest
):

    logger.info(
        "Extractor III requested for file_id=%s",
        request.file_id
    )

    db: Session = next(get_db())

    uploaded = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == request.file_id)
        .first()
    )

    if uploaded is None:

        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found."
        )

    #
    # STEP 1
    # Analyse document
    #

    analysis_result = (
        analysis_service.analyse_document(
            uploaded.storage_path
        )
    )

    if not analysis_result.success:

        raise HTTPException(
            status_code=500,
            detail=analysis_result.error
        )

    #
    # STEP 2
    # Extract document
    #

    extraction_result = (
        extractor_service.extract_from_analysis(

            file_id=request.file_id,

            analysis=analysis_result.analysis

        )
    )

    if not extraction_result.success:

        raise HTTPException(
            status_code=500,
            detail=extraction_result.error
        )

    return extraction_result

"""