from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.modules.db import get_db, UploadedFile, ExtractedContent

from backend.app.services.extraction_service import (
    extract_pdf,
    extract_excel,
    extract_docx,
    ocr_image,
    parse_table_from_text
)

from backend.app.tools.ai_table_extraction import ai_extract_any_table

from datetime import datetime
import os
import json

router = APIRouter()


@router.post("/extract-file/{file_id}")
def extract_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(UploadedFile).filter_by(id=file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = file.storage_path
    ext = os.path.splitext(file.filename)[1].lower()

    metadata = {}
    raw_text = ""
    raw_tables = []
    raw_images = []

    # -------------------------------------------------------------------
    # EXCEL — Week 6 + multi-sheet + your two fields

    if ext in [".xlsx", ".xls", ".xlsm", ".csv"]:
        excel_result = extract_excel(file_path)

        raw_tables = excel_result["tables"]
        metadata = excel_result["metadata"]
        raw_text = ""
        raw_images = []

    # -----------------------------------------------
    # PDF — Week 6
    elif ext == ".pdf":
        pdf_result = extract_pdf(file_path)

        raw_text = "\n".join([
            page.get("text", "") for page in pdf_result["pages"] if page.get("text")
        ])

        raw_tables = [
            table for page in pdf_result["pages"] for table in page.get("image_tables", [])
        ]

        raw_images = []
        metadata = pdf_result["metadata"]

    # -----------------------------------------------------
    # DOCX — Week 6 - extracting Word docs
    elif ext == ".docx":
        docx_result = extract_docx(file_path)

        raw_text = docx_result["text"]
        raw_tables = docx_result["tables"]
        raw_images = docx_result["images"]  # these are PIL images again

        # OCR fallback for   images
        for img in raw_images:
            ocr_text = ocr_image(img)
            table = parse_table_from_text(ocr_text)
            if table:
                raw_tables.append({
                    "sheet_name": "docx_ocr",
                    "table_index": len(raw_tables),
                    "headers": [],
                    "rows": table
                })

        metadata = docx_result["metadata"]

    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # ------------------------ -------------
    # Week 6  AI extraction fallback
    def tables_are_useless(tables):
        if not tables:
            return True
        for t in tables:
            if t.get("rows") or t.get("headers"):
                return False
        return True

    if tables_are_useless(raw_tables):
        combined_text = raw_text or ""

        for img in raw_images:
            t = ocr_image(img)
            combined_text += "\n" + t

        if not combined_text.strip():
            combined_text = (
                "The document contains one or more images that likely contain tables. "
                "Extract all tables you can infer."
            )


        ai_result = ai_extract_any_table(combined_text)
        raw_tables = ai_result.get("tables", [])

        metadata["table_count"] = len(raw_tables)
        metadata["sheets_extracted"] = len(raw_tables)

    # -------------------------------------- ----------------
    # Week 6 save JSON to No SQL export to the database
    extracted = ExtractedContent(
        file_id=file_id,
        #raw_tables=json.dumps(raw_tables),
        raw_tables=raw_tables,
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
        "images_extracted": len(raw_images),
        "metadata": metadata
    }


# ---------------------------------------------------
# normalisation helper
def extract_tables(file_id: int):
    db = next(get_db())
    record = db.query(ExtractedContent).filter(ExtractedContent.file_id == file_id).first()

    if not record:
        return None

    return record.raw_tables


