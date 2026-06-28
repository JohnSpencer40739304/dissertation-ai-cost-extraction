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


# Week 10 - adding router for AI extrapolation
#from backend.app.ai.extrapolation_router import runExtrapolationAI
from backend.app.copilot_router import router as copilot_router
from backend.app.extrapolation_router import router as extrapolation_router

# Database models
from backend.modules.db import UploadedFile, ExtractedContent
from backend.modules.models import CleanCostData, CleanCostDataAttributes


# Week 11 - AI document analysis part - used to understand the document being processed
from .analysis_router import router as analysis_router

from backend.app.extractor_router_iii import (
    router as extractor_router_iii
)

from backend.app.document_section_router_iii import (
    router as document_section_router_iii
)


# Week 1 - main body code
#class CostItem(BaseModel):
#    category: str
#    amount: float
#    year: int


app = FastAPI()
# init_db() week 10 moved below

# Week 11 - AI document analysis part
app.include_router(analysis_router)

app.include_router(
    document_section_router_iii
)

app.include_router(extractor_router_iii)




# CORS configuration which allows for a smoother API backend in fastAPI
#origins = ["*"]
#app.add_middleware(
#    CORSMiddleware,
    #allow_origins=origins,
    #allow_origins=["https://localhost:3000", "https://127.0.0.1:3000"],
    #allow_origins=["*"],
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:3000",
        "http://localhost:3000",
        "https://127.0.0.1:3000",
        "http://127.0.0.1:3000",
        "https://localhost",
        "http://localhost"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_db()


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

from backend.modules.db import ExtractedContent


#router = APIRouter()
normalisation_router = APIRouter()


#@router.post("/normalise/{file_id}")
@normalisation_router.post("/normalise/{file_id}")
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





#Week 9 addition
from backend.app import corrections
app.include_router(corrections.router)


#week 9 - send cost data to excel basd on file id:
from fastapi import HTTPException
from backend.modules.db import SessionLocal
from backend.modules.models import CleanCostData, CleanCostDataAttributes

@app.get("/file/{file_id}/data")
def get_clean_data(file_id: int):
    db = SessionLocal()

    rows = db.query(CleanCostData).filter(CleanCostData.file_id == file_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No clean_cost_data found for this file_id")

    attrs = (
        db.query(CleanCostDataAttributes)
        .filter(CleanCostDataAttributes.cost_item_id.in_([r.id for r in rows]))
        .all()
    )

    clean_data = [
        [
            "id",
            "file_id",
            "sheet_name",
            "table_index",
            "row_index",
            "item_description",
            "unit_price",
            "currency",
            "quantity",
            "ai_confidence_overall"
        ]
    ] + [
        [
            r.id,
            r.file_id,
            r.sheet_name,
            r.table_index,
            r.row_index,
            r.item_description,
            r.unit_price,
            r.currency,
            r.quantity,
            r.ai_confidence_overall
        ]
        for r in rows
    ]

    clean_attrs = [
        [
            "id",
            "cost_item_id",
            "attribute_name",
            "attribute_value",
            "extraction_method",
            "confidence_score"
        ]
    ] + [
        [
            a.id,
            a.cost_item_id,
            a.attribute_name,
            a.attribute_value,
            a.extraction_method,
            a.confidence_score
        ]
        for a in attrs
    ]

    return {
        "clean_cost_data": clean_data,
        "clean_cost_data_attributes": clean_attrs
    }

#week 9 - send a list of already loaded files to the plug-in
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.modules.db import SessionLocal
from backend.modules.db import UploadedFile

@app.get("/files")
def list_files():
    db = SessionLocal()
    files = db.query(UploadedFile).all()
    return [
        {"id": f.id, "name": f.filename}
        for f in files
    ]

# Week 10 - router endpoint for AI extrapolation 
# First attempt using AI only that exploded token counts
#@app.post("/extrapolation/run")
#async def extrapolation_run(payload: dict):
#    try:
#        result = await runExtrapolationAI(payload)
#        return result
#    except Exception as e:
#        print("Extrapolation error:", e)
#        return {"error": str(e)}

# ---------------------------------------------------------
# Register routers 
app.include_router(extract_router)
app.include_router(normalisation_router)
from backend.app import corrections
app.include_router(corrections.router)

# Week 10 AI routers
app.include_router(copilot_router, prefix="/copilot")
app.include_router(extrapolation_router, prefix="/analysis")


