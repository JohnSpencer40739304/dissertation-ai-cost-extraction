# WEEK 3 - Routing extrated data scripts 
# For routing excel data through the APIs
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
# from modules.db import get_db, UploadedFile, ExtractedContent
# Week 5 correction
from backend.modules.db import get_db, UploadedFile, ExtractedContent

# in week 6 it was discovered the classic extraction pipeline does not work on tables that were not constructed as true tables in documents ONLY AI can handle that
from backend.app.services.ai_table_extraction import ai_extract_table

# from app.services.extraction_service import extract_excel
#from app.services.extraction_service import extract_excel, extract_pdf # above line with PDFs added
# Add word to the list
# from app.services.extraction_service import (  # Week 5 correction below
from backend.app.services.extraction_service import (
    extract_pdf,
    extract_excel,
    extract_docx,
    ocr_image,              # added in week 6 after OCR issues in word
    parse_table_from_text   # added in week 6 after OCR issues in word
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
    # replaced in week6
    #elif ext == ".docx":
    #    docx_result = extract_docx(file_path)
    #    raw_text = docx_result["text"]
    #    raw_tables = docx_result["tables"]
    #    raw_images = docx_result["images"]
    #    metadata = docx_result["metadata"]

    # week 6 modification replacing the above as table images in word failed
    elif ext == ".docx":
        docx_result = extract_docx(file_path)
        raw_text = docx_result["text"]
        raw_tables = docx_result["tables"]

        # NEW: OCR tables from embedded images
        raw_images = docx_result["images"]  # these are PIL images now
        for img in raw_images:
            ocr_text = ocr_image(img)  # uses your improved preprocessing
            table = parse_table_from_text(ocr_text)
            if table:
                raw_tables.append(table)

        metadata = docx_result["metadata"]
        # end of week 6 modif





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


# Week 5 - added to determine the table that needs to be picked up by the normalising step. It fetches the extracted table for the next step.
from backend.modules.db import get_db, ExtractedContent

def extract_tables(file_id: int):
    db = next(get_db())
    record = db.query(ExtractedContent).filter(ExtractedContent.file_id == file_id).first()

    if not record:
        return None

    return record.raw_tables




def extract_file(file_path):

    raw_text = ""
    raw_tables = []
    raw_images = []

    # 1. Extract text (PDF or DOCX)
    raw_text = extract_text(file_path)

    # 2. Extract images
    raw_images = extract_images(file_path)

    # 3. OCR images
    for img in raw_images:
        t = ocr_image(img)
        if t.strip():
            raw_text += "\n" + t

    # 4. Deterministic table extraction
    raw_tables = extract_tables(file_path, raw_text)

    # 5. AI fallback (STEP 2)
    if not raw_tables:
        combined_text = raw_text or ""

        for img in raw_images:
            t = ocr_image(img)
            if not t.strip():
                t = run_paddleocr(img)
            combined_text += "\n" + t

        if combined_text.strip():
            ai_result = ai_extract_any_table(combined_text)
            raw_tables = ai_result.get("tables", [])

    # 6. Save to DB
    save_to_db(raw_text, raw_tables, metadata)



