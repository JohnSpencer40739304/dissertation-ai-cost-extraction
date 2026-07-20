# dissertation-ai-cost-extraction
### By John Spencer
### Student: 40739304
### Napier University
### MSC Data Engineering
### Supervisor: Dimitra Gkatzia 
### Internal Examiner: Saima Rafi
### Module Leader: Dr Mouad Lemoudden
Dissertation Project 2026 -  to see if AI can be used to extract and extrapolate dispersed supplier cost data from various different formats and incomplete data sets. Telecom products will be the used example.


# Week 12 (v20260720) - Adding additional features for Client AI
Previously the client end AI could run just one extrapolation method on the backend and perform some data summary work. Week 12 adds additional features to that. These include:
 - a more in depth summary whereby the user can ask for a summary breakdown by an attribute grouping field (such as country, or speed - any value which repeats and can be grouped)
 - a Spline (PCHIP) interpolation method allowing it to follow data points as a wave
 - a log/calculus curve fitting method
 AI is aware these additional tools exits within python on the backend, can discuss with the user advantages of each, make proposals, agree with user the selection and trigger the backend procedure. User can run and rerun these tools, the results appearing as additional columns in MS excel for the user to examin the results.
 The design is modular so additional analytics/extrapolation features can be added on the fly.
 At the same time, all AI elements on the client end were seperated from taskpane.js to become its own js module within a seperate AI folder.

### 2. Folder Structure
Code
```
backend/
  app/
    main.py                         → FastAPI entrypoint - Week 12 modified to serve excel chat client addtional features
    extract.py                      → Extraction router
    corrections.py                  → Processes data corrections sent from excel client
    extrapolation_router.py         → Week 10 - Extrapolation Router to find missing values
    copilot_router.py               → Week 10 - AI Extrapolation Chat Router
    analysis_router.py              → NEW Week 11 - AI Doucument Analysis Router
    document_section_router_iii.py  → NEW Week 11 - AI Doucument Section Router
    extractor_router_iii.py         → NEW Week 11 - AI Doucument Extraction Router

    ai/
      client.py                 → Week 10 redundent - OpenAI client wrapper
      copilot_ai.py             → Week 10 redundent - Test for AI excel router/prompt
      copilot_models.py         → Week 10 redundent - Test for AI excel router/prompt
      copilot_prompt.py         → Week 10 redundent - Test for AI excel router/prompt
      extrapolation_router.py   → Week 10 redundent - Test for AI excel router/prompt
      prompt_templates.py       → AI prompt definitions

    services/
      extraction_service.py           → Deterministic extraction logic
      normalisation_service.py        → Week‑8 normaliser (active)
      adapter.py                      → Converts extractor output → normaliser schema
      corrections_service.py          → Week 9 - Processes data corrections sent from excel client
      final_schema.py                 → Legacy (kept for reference)
      memory_store.py                 → Legacy (Week‑6/7 batch memory)
      extrapolation_orchestrator.py   → Week 10 - Orchestrates data extrapolation
      document_analysis_service.py    → NEW Week 11 - AI Doucument Analysis Service
      document_section_service_iii.py → NEW Week 11 - AI Doucument Section Service
      extractor_service_iii.py        → NEW Week 11 - AI Doucument Extraction Service

    tools/
      ai_table_extraction.py    → AI fallback for table extraction (active)
      cleaning.py               → Numeric cleaning utilities (active)
      currency_tool.py          → Currency inference helpers (active)
      analysis_tools.py         → Week 10 - Data Analytics tools and extrapolation 
                                → NEW Week 12 - additional tools: Breakdown summary by attribute, Spline Curve and Calculus Curve extrapoloation methods
      join_tools.py             → Week 10 - Table joining tools for AI Prompt

  modules/
    db.py                       → DB session + engine
    models.py                   → SQLAlchemy ORM models

client/
  excel-addin/
    deltic-excel-addin/               → Office.js Excel add-in
      src/taskpane/                   → Main UI logic - NEW week 10 to include AI Chatbot
        taskpane.js                   → Client Orchestrator
        taskpane.html                 → User interface
        taskpane.css                  → Appearence
      src/excel/
        populateExtrapolationBlock.je → Inserts extrapolation results into excel sheet
      src/ai/
        deltic_ai.js                  → Week 12 refectoring seperating AI elements from taskpane.js to here
      populateExtrapolationBlock.js   → Week 10 to ADD missing costs extrapolated via AI to the worksheet
      manifest.xml                    → Add-in manifest
      node_modules/                   → Ignored by Git
```

### 3. Next Steps
- Polished input device
- Enhanced AI extractor with smaller sections and better prompts POST disertation
- addition analytics features post disertation

# Week 11 (v20260630) - Testing Other Methods of AI extraction
Experiments using AI to try and improve data extraction. Found limits of what AI can capture and extract in one go. Added parts that use AI to analyse file and determine best section paths for AI extraction (some where still too big). This was done on the backend only and is a seperate extraction pipe. It is not connected to the normaliser, later steps nor the client front end.

### 1. Additions
Backend only:
- AI document Analysis router & procedure
- AI document section analysis router & procedure
- AI document extractor section by section
For use with PDFs only

### 2. Folder Structure
Code
```
backend/
  app/
    main.py                         → FastAPI entrypoint - Week 10 modified to serve excel chat client
    extract.py                      → Extraction router
    corrections.py                  → Processes data corrections sent from excel client
    extrapolation_router.py         → Week 10 - Extrapolation Router to find missing values
    copilot_router.py               → Week 10 - AI Extrapolation Chat Router
    analysis_router.py              → NEW Week 11 - AI Doucument Analysis Router
    document_section_router_iii.py  → NEW Week 11 - AI Doucument Section Router
    extractor_router_iii.py         → NEW Week 11 - AI Doucument Extraction Router

    ai/
      client.py                 → Week 10 redundent - OpenAI client wrapper
      copilot_ai.py             → Week 10 redundent - Test for AI excel router/prompt
      copilot_models.py         → Week 10 redundent - Test for AI excel router/prompt
      copilot_prompt.py         → Week 10 redundent - Test for AI excel router/prompt
      extrapolation_router.py   → Week 10 redundent - Test for AI excel router/prompt
      prompt_templates.py       → AI prompt definitions

    services/
      extraction_service.py           → Deterministic extraction logic
      normalisation_service.py        → Week‑8 normaliser (active)
      adapter.py                      → Converts extractor output → normaliser schema
      corrections_service.py          → Week 9 - Processes data corrections sent from excel client
      final_schema.py                 → Legacy (kept for reference)
      memory_store.py                 → Legacy (Week‑6/7 batch memory)
      extrapolation_orchestrator.py   → Week 10 - Orchestrates data extrapolation
      document_analysis_service.py    → NEW Week 11 - AI Doucument Analysis Service
      document_section_service_iii.py → NEW Week 11 - AI Doucument Section Service
      extractor_service_iii.py        → NEW Week 11 - AI Doucument Extraction Service

    tools/
      ai_table_extraction.py    → AI fallback for table extraction (active)
      cleaning.py               → Numeric cleaning utilities (active)
      currency_tool.py          → Currency inference helpers (active)
      analysis_tools.py         → Week 10 - Data Analytics tools and extrapolation
      join_tools.py             → Week 10 - Table joining tools for AI Prompt

  modules/
    db.py                       → DB session + engine
    models.py                   → SQLAlchemy ORM models

client/
  excel-addin/
    deltic-excel-addin/               → Office.js Excel add-in
      src/taskpane/                   → Main UI logic - NEW week 10 to include AI Chatbot
        taskpane.js                   → Client Orchestrator
        taskpane.html                 → User interface
        taskpane.css                  → Appearence
      src/excel/
        populateExtrapolationBlock.je → Inserts extrapolation results into excel sheet
      populateExtrapolationBlock.js   → Week 10 to ADD missing costs extrapolated via AI to the worksheet
      manifest.xml                    → Add-in manifest
      node_modules/                   → Ignored by Git
```
### 3. Next Steps
- Polished input device
- Enhanced AI extractor with smaller sections and better prompts POST disertation

# Week 10 (v20260620) - Building the AI Agent for Excel Client
The plug-in now contains a second tab with an AI chatbot to determine the type of data extrapolation for missing values. Currently only linear regression offered but additional ones can be added to the AI Prompt and pipe.

### 1. High‑Level Architecture Overview - Additions
Backend:
- Extraction Layer — deterministic parsing of Excel/PDF/DOCX + OCR + AI fallback
- Normalisation Layer — ultra‑light semantic cleaning, matrix explosion, and schema routing
- Persistence Layer — structured storage of raw extraction, normalised rows, and attributes
- data correction scripts to record user modifications made in excel
- NEW for week 10 - Open AI Chat router and sequencing using backend data
- NEW for week 10 - Extrapolation tools for missing cost data (limited to Regression but additions can be added)
- NEW for week 10 - AI Prompt to Managed the above two
Front End:
- Excel Client add-in - installation package needs to built but see below for method
- Button to select a file to be sent off for extraction and normalisation via the backend
- drop down list to select previous file already extracted that resides in the back end
- The above loads data into 3 sheets:
    - CleanCostData - key costing data - cannot be edited
    - CleanCostDataAttributes - Extended data table conatining all attributes  - cannot be edited
    - JoinedCostData - that merges the tables above and repivots the attribute rows into columns
- A user correction facility, user can make corrections in JoinedCostData and send corrections to the backend
- A table drop down list that allows user to select and see one table at a time in JoinedCostData when source file has multiple tables
- NEW for week 10 - An AI chatbox for data extrapolation
- NEW for week 10 - Tools to insert expolation results
- NEW for week 10 - Confirmation and various safety features to run it
Each layer is isolated, testable, and replaceable.

### 2. Folder Structure
Code

```
backend/
  app/
    main.py                     → FastAPI entrypoint - Week 10 modified to serve excel chat client
    extract.py                  → Extraction router
    corrections.py              → Processes data corrections sent from excel client
    extrapolation_router.py     → NEW Week 10 - Extrapolation Router to find missing values
    copilot_router.py           → NEW Week 10 - AI Extrapolation Chat Router

    ai/
      client.py                 → Week 10 redundent - OpenAI client wrapper
      copilot_ai.py             → Week 10 redundent - Test for AI excel router/prompt
      copilot_models.py         → Week 10 redundent - Test for AI excel router/prompt
      copilot_prompt.py         → Week 10 redundent - Test for AI excel router/prompt
      extrapolation_router.py   → Week 10 redundent - Test for AI excel router/prompt
      prompt_templates.py       → AI prompt definitions

    services/
      extraction_service.py        → Deterministic extraction logic
      normalisation_service.py     → Week‑8 normaliser (active)
      adapter.py                   → Converts extractor output → normaliser schema
      corrections_service.py       → Week 9 - Processes data corrections sent from excel client
      final_schema.py              → Legacy (kept for reference)
      memory_store.py              → Legacy (Week‑6/7 batch memory)
      extrapolation_orchestrator.py→ NEW Week 10 - Orchestrates data extrapolation

    tools/
      ai_table_extraction.py    → AI fallback for table extraction (active)
      cleaning.py               → Numeric cleaning utilities (active)
      currency_tool.py          → Currency inference helpers (active)
      analysis_tools.py         → NEW Week 10 - Data Analytics tools and extrapolation
      join_tools.py             → NEW Week 10 - Table joining tools for AI Prompt

  modules/
    db.py                       → DB session + engine
    models.py                   → SQLAlchemy ORM models

client/
  excel-addin/
    deltic-excel-addin/             → Office.js Excel add-in
      src/taskpane/                 → Main UI logic - NEW week 10 to include AI Chatbot
      populateExtrapolationBlock.js → NEW week 10 to ADD missing costs extrapolated via AI to the worksheet
      manifest.xml                  → Add-in manifest
      node_modules/                 → Ignored by Git
```

Legacy Week‑6/7 modules are preserved for dissertation evidence but not used in the active pipeline.
Failed Week 10 modules preserved to show experimentation.

### 3.  Pipeline Overview
1. Upload
User selects a file in Excel → sent to backend.
2. Extract
Backend parses the document into raw tables.
3. Normalise
AI + rule‑based engine converts raw tables into structured cost data.
4. Load
Excel add‑in fetches the final clean tables from the backend.
5. Join
Attributes are merged into the main table for correction.
6. Correction
User edits unlocked fields → corrections sent to backend.
7. Extrapolation
AI‑assisted cost prediction based on corrected data.

### 4. Extrapolation Engine 
The Excel add‑in now includes a chat engine that sends JSON as follows:
{{
  "reply": "a friendly, conversational natural-language reply to the user",
  "fields": ["list", "of", "fields", "to", "use"],
  "method": "analysis method or null",
  "notes": "extra notes or empty string",
  "action": "none | summarize | detect_zero_prices | extrapolate",
  "target": "unit_price",
  "attribute": "",
  "group_field": ""
}}
Once Extrapolated, the backend returns the following data:
{{
result = extrapolate_missing_values(
  df=self.df,
  target=target,
  attribute=attribute,
  group_field=group_field,
  degree=1
}}

### 5. Database Setup
Install PostgreSQL 14+ from https://www.postgresql.org/download/
Create the database:
createdb cost_dissertation_db

PostgreSQL instance is local and stored here: C:\Program Files\PostgreSQL\<version>\data\
Host: localhost
Port: 5432
Database: cost_dissertation_db
User: postgres

Run the backend:
uvicorn main:app --reload

### 6. Backend Setup via Command Prompt
Create a virtual environment:
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Running on local host: http://localhost:8000

### 7. Client Excel setup via Powershell
cd client/excel-addin/deltic-excel-addin
npm install
npm start
Then sideload the excel manifest into Add-Ins.


# Week 9 (v20260608) - Building the Excel Client
The client is an excel plugin built using a modern javascript and HTML front end calling the backend developed in previous weeks.

### 1. High‑Level Architecture Overview
Backend:
- Extraction Layer — deterministic parsing of Excel/PDF/DOCX + OCR + AI fallback
- Normalisation Layer — ultra‑light semantic cleaning, matrix explosion, and schema routing
- Persistence Layer — structured storage of raw extraction, normalised rows, and attributes
- NEW for week 9 - data correction scripts to record user modifications made in excel
Front End (new for week 9):
- Excel Client add-in - installation package needs to built but see below for method
- Button to select a file to be sent off for extraction and normalisation via the backend
- drop down list to select previous file already extracted that resides in the back end
- The above loads data into 3 sheets:
    - CleanCostData - key costing data - cannot be edited
    - CleanCostDataAttributes - Extended data table conatining all attributes  - cannot be edited
    - JoinedCostData - that merges the tables above and repivots the attribute rows into columns
- A user correction facility, user can make corrections in JoinedCostData and send corrections to the backend
- A table drop down list that allows user to select and see one table at a time in JoinedCostData when source file has multiple tables
Each layer is isolated, testable, and replaceable.

### 2. Folder Structure
Code

```
backend/
  app/
    main.py                     → FastAPI entrypoint - Week 9 modified for to serve excel client
    extract.py                  → Extraction router
    corrections.py              → NEW Week 9 - Processes data corrections sent from excel client

    ai/
      client.py                 → OpenAI client wrapper
      prompt_templates.py       → AI prompt definitions

    services/
      extraction_service.py     → Deterministic extraction logic
      normalisation_service.py  → Week‑8 normaliser (active)
      adapter.py                → Converts extractor output → normaliser schema
      corrections_service.py    → NEW Week 9 - Processes data corrections sent from excel client
      final_schema.py           → Legacy (kept for reference)
      memory_store.py           → Legacy (Week‑6/7 batch memory)

    tools/
      ai_table_extraction.py    → AI fallback for table extraction (active)
      cleaning.py               → Numeric cleaning utilities (active)
      currency_tool.py          → Currency inference helpers (active)

  modules/
    db.py                       → DB session + engine
    models.py                   → SQLAlchemy ORM models

client/
  excel-addin/
    deltic-excel-addin/               → Office.js Excel add-in
      src/taskpane/                   → Main UI logic
        taskpane.js                   → Client Orchestrator
        taskpane.html                 → User interface
        taskpane.css                  → Appearence
      manifest.xml          → Add-in manifest
      node_modules/         → Ignored by Git
```

Legacy Week‑6/7 modules are preserved for dissertation evidence but not used in the active pipeline.

### 3. Features
Backend
- Upload any file (PDF, DOCX, XLSX)
- AI‑assisted extraction of cost tables
- Normalisation into a unified schema:
- clean_cost_data
- clean_cost_data_attributes
- PostgreSQL persistence
- Correction ingestion API
- File history & re‑load support
Client (Excel Add‑in)
- Load any processed file from the backend
- View clean cost data and attributes
- Auto‑build a joined table for correction
- Select individual tables via dropdown
- Lock core fields, allow user edits on others
- Send corrections back to backend
- Full pipeline automation: Upload → Extract → Normalise → Load → Join → correct → reload

### 4.  Pipeline Overview
1. Upload
User selects a file in Excel → sent to backend.
2. Extract
Backend parses the document into raw tables.
3. Normalise
AI + rule‑based engine converts raw tables into structured cost data.
4. Load
Excel add‑in fetches the final clean tables from the backend.
5. Join
Attributes are merged into the main table for correction.
6. Correction
User edits unlocked fields → corrections sent to backend.
7. Extrapolation (coming next)
AI‑assisted cost prediction based on corrected data.

### 5. Corrections Engine 
The Excel add‑in builds a joined table with:
- Core fields (locked)
- Attribute fields (editable)
- User‑added columns (ignored)
- Row‑level IDs for backend updates
Corrections are sent as structured JSON:
{
  "source_row_id": 123,
  "file_id": 82,
  "field_type": "core",
  "field_name": "unit_price",
  "old_value": "12.50",
  "new_value": "14.00",
  "user": "excel_user"
}

### 6. Database Setup
Install PostgreSQL 14+ from https://www.postgresql.org/download/
Create the database:
createdb cost_dissertation_db

PostgreSQL instance is local and stored here: C:\Program Files\PostgreSQL\<version>\data\
Host: localhost
Port: 5432
Database: cost_dissertation_db
User: postgres

Run the backend:
uvicorn main:app --reload

### 7. Backend Setup via Command Prompt
Create a virtual environment:
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Running on local host: http://localhost:8000

### 8. Client Excel setup via Powershell
cd client/excel-addin/deltic-excel-addin
npm install
npm start

Then sideload the excel manifest into Add-Ins.

NEXT STEP - Data Extrapolation Tools....


# Week 8 (v20260528) - Normalisation Fixed with enhanced extraction
This backend implements a modular, AI‑assisted cost‑extraction and normalisation pipeline designed for heterogeneous commercial documents (Excel, PDF, DOCX, OCR images).
The architecture is intentionally simple, auditable, and aligned with the dissertation’s goals: traceability, modularity, and progressive refinement.

### 1. High‑Level Architecture Overview
The system is composed of three independent layers:
- Extraction Layer — deterministic parsing of Excel/PDF/DOCX + OCR + AI fallback
- Normalisation Layer — ultra‑light semantic cleaning, matrix explosion, and schema routing
- Persistence Layer — structured storage of raw extraction, normalised rows, and attributes
Each layer is isolated, testable, and replaceable.

### 2. Folder Structure (Final)
Code

```
backend/
  app/
    main.py                     → FastAPI entrypoint
    extract.py                  → Extraction router

    ai/
      client.py                 → OpenAI client wrapper
      prompt_templates.py       → AI prompt definitions

    services/
      extraction_service.py     → Deterministic extraction logic
      normalisation_service.py  → Week‑8 normaliser (active)
      adapter.py                → Converts extractor output → normaliser schema
      final_schema.py           → Legacy (kept for reference)
      memory_store.py           → Legacy (Week‑6/7 batch memory)

    tools/
      ai_table_extraction.py    → AI fallback for table extraction (active)
      cleaning.py               → Numeric cleaning utilities (active)
      currency_tool.py          → Currency inference helpers (active)

  modules/
    db.py                       → DB session + engine
    models.py                   → SQLAlchemy ORM models
```

Legacy Week‑6/7 modules are preserved for dissertation evidence but not used in the active pipeline.

### 3. Extraction Layer
Purpose
Convert arbitrary documents into a unified intermediate representation:
Code
{
  "file_id": ...,
  "tables": [...],
  "text": ...,
  "images": ...
}
**Components**
extraction_service.py
- Excel parsing (multi‑sheet, header detection)
- PDF text + OCR image table detection
- DOCX text, tables, embedded images
- OCR fallback for images
- Table reconstruction from OCR text
ai_table_extraction.py  
- AI fallback when deterministic extraction fails.
extract.py  
- FastAPI router orchestrating extraction and saving results to DB.

Output
All extraction results are stored in ExtractedContent for reproducibility.

### 4. Normalisation Layer (Week‑8)
Purpose
Transform raw extracted tables into a clean, row‑level cost dataset suitable for analysis.
Key Features
- Header‑based row mapping
- Numeric cleaning (clean_numeric)
- Currency inference
- AI‑assisted table classification
- Matrix table explosion
- Row‑level confidence scoring

Routing into:
- CleanCostData (core rows)
- CleanCostDataAttributes (extended attributes)

Components
- normalisation_service.py  The main Week‑8 normaliser.
- adapter.py  Ensures extractor output matches the schema expected by the normaliser.
- Output A unified, normalised dataset stored in two relational tables.

### 5. Persistence Layer
Models
- UploadedFile — metadata for uploaded documents
- ExtractedContent — raw extraction results
- NormalisedContent — debug storage of Week‑8 normaliser output
- CleanCostData — core cost rows
- CleanCostDataAttributes — extended attributes per row
- BatchMemory / TableHeader — legacy Week‑6/7 memory (kept for reference)
- Database Engine
Defined in db.py using SQLAlchemy ORM.

### 6. Legacy Modules (Preserved for Dissertation Evidence)
These modules represent earlier iterations (Week‑6/7) and are intentionally retained:
- memory_store.py — batch memory for multi‑pass AI normalisation
- adaptive_batch_size.py — experimental batch tuning
- batch_overlap.py — overlapping batch strategy
- ai_extraction.py — early AI‑first extractor prototype
- final_schema.py — early schema routing prototype
- prompt_template_semantic.py — early semantic classifier prompts
- They are not imported by the active pipeline.

### 7. Execution Flow Summary
Code
User uploads file →
  extract.py →
    extraction_service.py →
      (deterministic extraction)
      OR ai_table_extraction.py (fallback)
    → ExtractedContent saved

User triggers normalisation →
  normalisation_service.py →
    adapter.py (schema alignment)
    clean_numeric, currency inference
    AI table classification
    matrix explosion
    → CleanCostData + CleanCostDataAttributes saved

### 8. Design Principles
- Modularity — each layer is isolated and replaceable
- Auditability — raw extraction and normalised output stored separately
- Determinism first — AI used only when deterministic methods fail (faster than AI alone)
- Explainability — minimal AI involvement in Week‑8 normaliser
- Reproducibility — all intermediate states persisted


# Week 7 (v20260522) - Refinements to Normalisation step

The pipeline currently follows these steps:

1. **File extraction**
   - Extracts tables from the uploaded file.
   - For Excel: extracts all sheets but only processes the *first* one.
   - For Word: extracts all tables but merges them into a single list of rows.
2. **Classic Normalisation**
   - Attempts to convert raw rows into a simple `[service, rating, price]` schema.
   - Works only for very simple, single‑table inputs.
3. **AI Normalisation**
   - Uses an LLM to infer missing attributes and clean values.
4. **Semantic Normalisation**
   - Applies a second AI pass to assign meaning (service, rating type, currency, etc.).
5. **Database Storage**
   - Saves the final rows into PostgreSQL under a single `file_id`.

##  Known Limitations (Current State)
###  1. Only the first sheet of an Excel file is processed  
Even though extraction detects all sheets, the normaliser only receives the
first one. Multi‑sheet Excel files therefore produce incomplete or empty output.
###  2. Word documents with multiple tables are merged incorrectly  
Tables are concatenated into a single row list, causing:
- lost table boundaries  
- lost columns  
- misaligned rows  
- semantic misinterpretation  
###  3. Matrix tables are not supported  
Wide tables (e.g., bandwidth tiers across columns) are not exploded into
row‑based records. Most matrix tables currently return **0 rows**.
###  4. Currency parsing is unreliable  
Values like `$3,800` may be incorrectly parsed as `3.8`.
###  5. POP (Point of Presence) is misinterpreted as “Population”  
Semantic AI currently lacks telecom‑specific glossary rules.
###  6. The pipeline assumes “one file = one table”  
This assumption is incompatible with real telecom pricing documents.

## Current Behaviour
- Simple, single‑table documents may work.
- Multi‑table Word files produce partial or incorrect results.
- Multi‑sheet Excel files often return **zero rows**.
- Matrix tables are not handled at all.
- Semantic AI produces inconsistent interpretations due to upstream issues.

This repository currently represents a **failed prototype** pending a major
refactor.


# Week 6 (v20260515) - AI powered Cost Extraction and Normalisation

After OCRs failed to extract tabled data from images, the extraction step was modified to include AI for those tricky to find tables.
Week 6 main goal was the AI normaliser.

It now combines deterministic parsing, OCR, and generative AI to extract and normalise messy, unstructured pricing tables into clean, structured data.
- Extraction pipeline stable
- AI fallback extraction working
- Classic normaliser upgraded
- AI normaliser running end‑to‑end
- JSON decoding fixed
- Prompt template fixed
- Batch size logic fixed
- Data stored correctly in PostgreSQL
- SQL inspection validated

This is the first fully functional version of the system.

To start API : uvicorn backend.app.main:app --reload

License : Internal academic + research use (dissertation project).


# Week 5 (v20260505) - Normalisation Layer Using Classic Pipeline 

Week 5 seeks to normalise data prior to using AI data extraction and processing.
This version is NOT a full back version as it FAILs to work (see below).

This version intentionally preserves the classic approach to illustrate its weaknesses:
- Pandas cannot handle ragged or nested rows
- PDF tables vary wildly in structure
- Word tables may contain merged cells or inconsistent rows
- OCR output is unpredictable
- Row‑by‑row AI calls are costly
- Metadata is not fully propagated
- Normalisation fails on real‑world messy data

These limitations form the academic justification for the next architectural phase.

## Classic Normalisation (Baseline)
A deterministic cleaning layer attempts to:

remove empty rows
remove empty columns
clean text cells
detect column types
convert dates

This approach works for clean Excel files but fails on:
ragged OCR tables
nested lists
inconsistent row lengths
mixed text + table content

## AI using a dataframe (Baseline)
This works when data is easily derterministic and Pandas can generate a dataframe to swallowed by OpenAI API.
Our files are not. And while they reflect some real world messyness, they are still relatively tidy or lighter versions of that.
The determenistic route was inching closer to a very biased solution to clean my test files. Meaning it overfits and will have to be rewritten whenever there is a new file.

This limitation motivates the upcoming AI row processing batching rewrite in Week 6.



# Week 4 (v20260406) - Modifications to the data extraction pipeline to include Metadata 

Week 4 introduces a unified metadata extraction layer across all supported document formats (PDF, DOCX, XLSX).
This metadata improves traceability, validation, and downstream normalisation.

Metadata provides essential context for understanding and validating extracted content.

## Why?
This was inspired by best practices and data management within the handling of data for medical research:
- Data quality & reliability: Taylor et al. (BMJ Evidence‑Based Medicine) highlight that missing contextual information leads to unreliable outputs.
- Reproducibility & trust: The NIH states that metadata is required to “understand, trust, reproduce, or reuse data.”
- Integration of heterogeneous sources: NIH guidance emphasises metadata as critical when combining data from multiple formats.
- Structured workflows: Springer guidelines note that defining metadata early reduces discrepancies and supports consistent extraction.

## Metadata Extracted Per Format
### PDF
- page_count
- table_count
- image_count
- ocr_used
- file_size_kb
- extraction_time_ms

### DOCX
- paragraph_count
- table_count
- image_count
- file_size_kb
- extraction_time_ms

### Excel/CSV
- sheet_count
- rows_per_sheet
- columns_per_sheet
- file_size_kb
- extraction_time_ms

### End‑to‑End Test
- Successfully reloaded and extracted multiple file types via Swagger UI (/docs) and checked Metadata was recorded accordingly.
- Reverified extracted text, tables, and images stored correctly in PostgreSQL
- Reconfirmed OCR works for scanned PDFs and DOCX image extraction serializes correctly


# Week 3 (v20260330) - Data Extraction Pipeline

This week focused on implementing the full document‑extraction layer, enabling the system to process real supplier files across multiple formats. This forms the core technical capability required for later cost‑normalisation, pattern detection, and AI‑driven extrapolation.

### Key Outcomes
- Implemented a unified extraction engine for PDF, DOCX, Excel, and CSV
- Added OCR support using Tesseract for scanned or image‑based PDFs
- Extracted text, tables, and embedded images from Word documents
- Converted extracted images to base64 for JSON‑safe database storage
- Integrated all extractors into a single FastAPI endpoint
- Stored extracted content in PostgreSQL for traceability and downstream processing
- Ensured the architecture remains modular, reproducible, and extensible

### Supported Extraction Features
- PDF: text, tables, images, OCR
- DOCX: text, tables, embedded images
- Excel: sheets, tables, cell values
- CSV: row‑based parsing

### Database Table
The extracted_content table now stores:
- file ID
- raw extracted text
- extracted tables
- base64‑encoded images for JSON
- extraction status
- timestamp

### FastAPI Endpoint
- POST /extract-file/{file_id}  
- Automatically detects the file type and routes it to the appropriate extractor (PDF, DOCX, Excel, CSV).
- Stores the extracted content in PostgreSQL as structured JSON.

### Purpose
This extraction layer completes the ingestion + processing foundation required for the dissertation.
It enables the next phase: cost‑pattern extraction, normalisation, and AI‑driven inference across inconsistent supplier documents.

### End‑to‑End Test
- Successfully uploaded and extracted multiple file types via Swagger UI (/docs)
- Verified extracted text, tables, and images stored correctly in PostgreSQL
- Confirmed OCR works for scanned PDFs and DOCX image extraction serializes correctly


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
