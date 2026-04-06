# WEEK 3 - Routing extrated data scripts 
# For routing excel data through the APIs
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from modules.db import get_db, UploadedFile, ExtractedContent
# from app.services.extraction_service import extract_excel
#from app.services.extraction_service import extract_excel, extract_pdf # above line with PDFs added
# Add word to the list
from app.services.extraction_service import (
    extract_pdf,
    extract_excel,
    extract_docx   
)

from datetime import datetime

import os  # correction for . being recorded and also an expansion to csv and xlsm file types

router = APIRouter()

@router.post("/extract-file/{file_id}")
def extract_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(UploadedFile).filter_by(id=file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = file.storage_path
    #file_type = file.file_type.lower() # correction for . (dot) being recorded 
    ext = os.path.splitext(file.filename)[1].lower()
    # week 4 - meta data setting default values
    metadata = {}
    raw_text = ""
    raw_tables = []
    raw_images = []

    # if file_type in ["xlsx", "xls"]: # correction for . being recorded and also an expansion to csv and xlsm file types
    if ext in [".xlsx", ".xls", ".xlsm", ".csv"]: 
        #raw_tables = extract_excel(file_path)
        # week 4 - meta data setting default values
        excel_result = extract_excel(file_path)
        raw_tables = excel_result["tables"]
        metadata = excel_result["metadata"]
        raw_text = ""  
        raw_images = []

    # PDF section added here (2 lines)
    elif ext == ".pdf":
        #raw_tables = extract_pdf(file_path)
        # week 4 - meta data modifications
        pdf_result = extract_pdf(file_path)
        raw_text = "\n".join([
            page.get("text", "") for page in pdf_result["pages"] if page.get("text")
        ])
        raw_tables = [
            table for page in pdf_result["pages"] for table in page.get("image_tables", [])
        ]
        raw_images = []

        metadata = pdf_result["metadata"]


    # Word section
    #elif file_path.lower().endswith(".docx"):
    #    raw_tables = extract_docx(file_path)
    # week 4 modifications for metadata
    elif ext == ".docx":
        docx_result = extract_docx(file_path)
        raw_text = docx_result["text"]
        raw_tables = docx_result["tables"]
        raw_images = docx_result["images"]
        metadata = docx_result["metadata"]

    else:
        raise HTTPException(status_code=400, detail="Unsupported file type") # previously below
        
    # stores the extracted result
    extracted = ExtractedContent(
        file_id=file_id,
        raw_tables=raw_tables,
        # raw_text=None, week 4  correction
        raw_text=raw_text,
        extraction_metadata=metadata,
        extraction_status="success",
        created_at=datetime.utcnow()
    )
    db.add(extracted)
    db.commit()
    db.refresh(extracted)
    return {
        "status": "success",
        "file_id": file_id,
        "sheets_extracted": len(raw_tables),
        "images_extracted": len(raw_images), # week 4 extra rows for meta data
        "metadata": metadata
    }

    #raise HTTPException(status_code=400, detail="Unsupported file type") # moved above




