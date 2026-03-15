# Week 1 - Imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.db import get_connection   # week 1 database connection test 20260307
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


@app.get("/db-test")
def db_test():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return {"db_response": result}

# week 1 test to add data very python using fastAPI
@app.post("/add-cost")
def add_cost(item: CostItem):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cost_items (category, amount, year) VALUES (%s, %s, %s) RETURNING id;",
        (item.category, item.amount, item.year)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"inserted_id": new_id}

# Week 2 - main body code

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    # check that the filename extension is valid and is either csv, excel, word etc 
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()

    if ext not in ALLOWED_EXTENSIONS:
        return {"error": f"Unsupported file type: {ext}"}

    # Create unique filename with a date time stamp - this will allow user to reload the same file IF they modify manually
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stored_name = f"{timestamp}_{file.filename}"
    storage_path = os.path.join(UPLOAD_DIR, stored_name)

    with open(storage_path, "wb") as f:
        f.write(await file.read())

    # Insert all the metadata into DB - this is quite complex
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO uploaded_files (filename, file_type, storage_path)
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (file.filename, ext, storage_path)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {
        "uploaded_id": new_id,
        "original_filename": file.filename,
        "stored_as": stored_name,
        "file_type": ext,
        "status": "stored"
    }


