# Week 1 - Imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from modules.db import get_connection   # week 1 database connection test 20260307 Line Disactivated in Week 3
from pydantic import BaseModel  # week 1 insert data into DB using fastAPI from python


#Week 2 - Imports + some code defining directory and file types
from fastapi import UploadFile, File
import os
# from datetime import  # correction required here for API
from datetime import datetime


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg"}

# Week 1 - main body code

class CostItem(BaseModel):
    category: str
    amount: float
    year: int

app = FastAPI()


# CORS configuration which allows for a smoother API backend in fastAPI

origins = [
    "*",  # allow all origins during development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Week 1 database test endpoint from 20260307
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
    from modules.db import UploadedFile, get_db
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
from app.extract import router as extract_router
app.include_router(extract_router)

