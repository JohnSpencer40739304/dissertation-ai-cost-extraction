# dissertation-ai-cost-extraction
### By John Spencer
### Student: 40739304
### Napier University
### MSC Data Engineering
### Supervisor: Dimitra Gkatzia 
### Internal Examiner: Saima Rafi
### Module Leader: Dr Mouad Lemoudden
Dissertation Project 2026 -  to see if AI can be used to extract and extrapolate dispersed supplier cost data from various different formats and incomplete data sets. Telecom products will be the used example.

# Week 1 Summary (v20260307) - Set up the backend and release management

### Release Management
- Git Hub created and set up for release management and traceability of project development
### Database Setup
- PostgreSQL installed locally
- Database created: `cost_dissertation_db`
- Table created: `cost_items`  This to test connection - not the final table schema.
  Columns: `id`, `category`, `amount`, `year`
 ### Backend Setup 
- FastAPI backend setup
- Folder structure setup
### API Endpoints Implemented
- `GET /` – basic health check  
- `GET /db-test` – verifies database connectivity  
- `POST /add-cost` – inserts a cost item into the database

###  End-to-End Test
- Successfully inserted data via Swagger UI (`/docs`) http://127.0.0.1:8000/docs#/default/db_test_db_test_get
- Verified data stored in PostgreSQL using SQL Shell

## How to Run using initial local PC development
1. Start PostgreSQL locally  
2. Navigate to the backend folder  
3. Run the API


# Week 2 (v20260315) - File Ingestion Pipeline

This week focused on building the backend ingestion layer that will support all later extraction and cost-normalisation work.

### Key Outcomes
- Added a FastAPI endpoint to upload cost supplier procurement files  
- Validated file types before accepting them  
- Stored uploaded files in backend/uploads/  
- Inserted metadata into PostgreSQL for traceability  
- Ensured reproducibility and minimal scope (no extraction yet)

### Supported File Types
.pdf, .docx, .xlsx, .xls, .csv, .png, .jpg, .jpeg

### Database Table
A new table `uploaded_files` tracks:
- original filename  
- file type  
- storage path  
- timestamp  
- status  

### FastAPI Endpoint
`POST /upload-file`  
Accepts a file, validates it, stores it, and records metadata in the database.

### Purpose
This ingestion layer forms the foundation for Week 3 , where text extraction, OCR, and structured parsing will be implemented.

###  End-to-End Test
- Successfully inserted data via Swagger UI (`/docs`) http://127.0.0.1:8000/docs#/default/db_test_db_test_get
- Verified data stored in PostgreSQL using SQL Shell that data table containing file details was updated and set to pending status
