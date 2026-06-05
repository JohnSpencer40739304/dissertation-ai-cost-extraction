# Week 8 tidy up of imports
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os

#from backend.modules.db import init_db
from backend.modules.db import init_db, SessionLocal
from backend.app.extract import router as extract_router
#from backend.app.services.extraction_service import extract_raw_content
from backend.app.services.normalisation_service import NormalisationService
from backend.app.services.adapter import adapt_unified_extractor_output

# Week 1 - Imports
#from fastapi import FastAPI
#from fastapi.middleware.cors import CORSMiddleware
# from modules.db import get_connection   # week 1 database connection test 20260307 Line Disactivated in Week 3
#from pydantic import BaseModel  # week 1 insert data into DB using fastAPI from python

#Week 2 - Imports + some code defining directory and file types
#from fastapi import UploadFile, File, HTTPException
#import os
# from datetime import  # correction required here for API
#from datetime import datetime

#Week 5 additions (2 lines below)
#from backend.app.services.extraction_service import ExtractionService # used if Class existed in file but we have direct functions there
#from backend.app.services.extraction_service import extract_tables #replaced below week 8
#from backend.app.services.normalisation_service import NormalisationService
#from backend.modules.db import init_db





# Week 1 - main body code
#class CostItem(BaseModel):
#    category: str
#    amount: float
#    year: int
app = FastAPI()
init_db()


# CORS configuration which allows for a smoother API backend in fastAPI
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg"}

# Week 5 additions (2 lines below) 
#extraction_service = ExtractionService()
#normalisation_service = NormalisationService()

# Week 1 database test endpoint from 20260307 ROOT ENDPOINT
@app.get("/")
def root():
    return {"message": "TEST from the dissertation backend to check that the API works"}


# Week 2 - load file
@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Store metadata in DB
    # from modules.db import UploadedFile, get_db #week 5 correction
    from backend.modules.db import UploadedFile, get_db
    from sqlalchemy.orm import Session

    db: Session = next(get_db())
    uploaded = UploadedFile(
        filename=file.filename,
        storage_path=file_path,
        file_type=ext,
        uploaded_at=datetime.utcnow()
    )

    db.add(uploaded)
    db.commit()
    db.refresh(uploaded)

    return {
        "status": "success",
        "file_id": uploaded.id,
        "filename": uploaded.filename
    }


# Week 3 data extraction scripts
#from app.extract import router as extract_router
# week 5 line correction to the above then moved to the top in week 8
#from backend.app.extract import router as extract_router
#app.include_router(extract_router)


# Week 5 - run normalisation layer
"""
#@app.get("/normalise/{file_id}")
#async def normalise_file(file_id: int):
    # Step 1 — Extract raw table
    #extraction_service = ExtractionService() # extraction not a class object but a function
    #table = extraction_service.extract_tables(file_id) 
#    table = extract_tables(file_id)
#    if table is None:
#        raise HTTPException(status_code=404, detail="File not found or extraction failed")
    # Step 2 — Run classic + AI normalisation
#    normalisation_service = NormalisationService()
#    result = normalisation_service.normalise(table)
    # generates dataframes
    #classic_json = result["classic_clean_df"].to_dict(orient="records")
    #ai_json = result["ai_enriched_df"].to_dict(orient="records")
    # corrections to above
#    classic_df = result["classic_clean_df"]
#    ai_df = result["ai_enriched_df"]  
    # save to the database
#    normalisation_service.save_to_db(file_id, classic_df, ai_df)
#    return {
#        "file_id": file_id,
        # "classic_clean": classic_json,   # dataframe only
        # "ai_enriched": ai_json           # dataframe only - lines modified to store in DB
#        "classic_clean": classic_df.to_dict(orient="records"),
#        "ai_enriched": ai_df.to_dict(orient="records")
#    }
"""

""" This Section used for weeks 6 and 7 was killed off in week 8 and replace with version below
# Corrected for change away from DF to batch data
#@app.get("/normalise/{file_id}")
#async def normalise_file(file_id: int):
    # Step 1 — Extract raw table
#    table = extract_tables(file_id)
#    if table is None:
#        raise HTTPException(status_code=404, detail="File not found or extraction failed")
    # Step 2 — Run classic + AI normalisation
#    normalisation_service = NormalisationService()
    #result = normalisation_service.normalise(table, file_metadata={"file_id": file_id})
#    file_metadata = {
#        "file_id": file_id,
#        "source_format": table[0].get("source_format")
#    }
#    result = normalisation_service.normalise(table, file_metadata)
#    classic_rows = result["classic_clean"]
#    ai_rows = result["ai_enriched"]
    # Step 3 — Save AI rows to DB
#    normalisation_service.save_to_db(file_id, ai_rows)
#    return {
#        "file_id": file_id,
#        "classic_clean": classic_rows,
#        "ai_enriched": ai_rows
#    }
"""


# WEEK 8 - new normalisation part
#from fastapi import APIRouter, HTTPException
#router = APIRouter()
#@router.get("/normalise/{file_id}")
#async def normalise_file(file_id: int):
#    # 1  Extract raw content (all sheets, tables, text)
#    raw_extraction = extract_raw_content(file_id)
#    if raw_extraction is None:
#        raise HTTPException(status_code=404, detail="File not found or extraction missing")
    # 2   Run AI-first normalisation
#    service = NormalisationService(raw_extraction)
#    ai_output = service.run()
#    service.save_to_normalised_content(file_id, ai_output)
    # 3    Return structured output
#    return {
#        "file_id": file_id,
#        "status": "normalised",
#        "tables": ai_output.get("tables", []),
#        "document_explanation": ai_output.get("document_explanation"),
#        "clarifying_questions": ai_output.get("clarifying_questions", [])
#    }
    # save to database normalised content
#    normalisation_service.save_to_normalised_content(file_id, ai_output)


#  WEEK 8 ADDITION: register the normalisation router
router = APIRouter()

from backend.modules.db import ExtractedContent

@router.post("/normalise/{file_id}")
async def normalise_file(file_id: int):
    db = SessionLocal()

    # Load raw extraction from extracted_content
    raw = db.query(ExtractedContent).filter(ExtractedContent.file_id == file_id).first()
    if not raw:
        raise HTTPException(status_code=404, detail="Raw extraction not found")

    #raw_extraction = raw.raw_tables  # extractor output
    raw_extraction = {
        "file_id": file_id,
        "tables": raw.raw_tables
    }

    # Run the normalisation pipeline
    service = NormalisationService(raw_extraction)
    output = service.run()

    return {
        "file_id": file_id,
        "status": "normalised",
        "tables": output.get("tables", []),
        "document_explanation": output.get("document_explanation"),
        "clarifying_questions": output.get("clarifying_questions", [])
    }


# record the routers
app.include_router(extract_router)
app.include_router(router)






