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

    # if file_type in ["xlsx", "xls"]: # correction for . being recorded and also an expansion to csv and xlsm file types
    if ext in [".xlsx", ".xls", ".xlsm", ".csv"]: 
        raw_tables = extract_excel(file_path)

    # PDF section added here (2 lines)
    elif ext == ".pdf":
        raw_tables = extract_pdf(file_path)

    # Word section
    elif file_path.lower().endswith(".docx"):
        raw_tables = extract_docx(file_path)


    else:
        raise HTTPException(status_code=400, detail="Unsupported file type") # previously below
        
    # stores the extracted result
    extracted = ExtractedContent(
        file_id=file_id,
        raw_tables=raw_tables,
        raw_text=None,
        extraction_status="success",
        created_at=datetime.utcnow()
    )
    db.add(extracted)
    db.commit()
    db.refresh(extracted)
    return {
        "status": "success",
        "file_id": file_id,
        "sheets_extracted": len(raw_tables)
    }

    #raise HTTPException(status_code=400, detail="Unsupported file type") # moved above
