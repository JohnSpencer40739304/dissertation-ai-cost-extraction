# backend/app/ai/prompt_templates.py

"""
WEEK 8 PROMPT ARCHITECTURE

This file now contains:
1. Original prompts (unchanged)
2. Batch-level prompts (strict JSON)
3. Document-level summary prompt (free-form)
"""

# ----------------------------------------------------------------------
# 1. ORIGINAL PROMPTS (unchanged)
# ----------------------------------------------------------------------

DOCUMENT_EXTRACTION_PROMPT = """
You are an AI system that extracts structured cost data from messy,
inconsistent, real‑world pricing documents.

Your task is to analyse the following document and return a JSON object with:
- tables
- rows
- attributes
- confidence scores
- document explanation
- clarifying questions

Follow the output schema strictly:
{
  "tables": [
    {
      "sheet_name": "string",
      "table_index": 0,
      "title": "string or null",
      "rows": [
        {
          "attributes": { "key": "value" },
          "confidence": 0.0
        }
      ]
    }
  ]
}

Do not invent values.
"""

USER_EXTRACTION_TEMPLATE = """
Below is the raw extraction JSON from the unified extractor:

{{RAW_EXTRACTION_JSON}}

Please normalise the content into structured cost data.
"""


# ----------------------------------------------------------------------
# 2. WEEK 8 — BATCH NORMALISATION PROMPT (strict JSON)
# ----------------------------------------------------------------------

BATCH_NORMALISATION_PROMPT = """
You are an AI system that extracts structured attributes from messy, irregular,
multi-format tables. A single file may contain multiple tables, each with its own
header, structure, and semantics. Tables may come from PDFs, Excel sheets, or
OCR output. Your job is to normalise each table independently.

Each table may contain:
- single-row headers
- multi-row headers
- matrix-style headers (e.g., bandwidths across columns)
- missing or partial headers
- repeated headers mid-table
- merged cells
- inconsistent column counts
- numeric or categorical column labels

Your responsibilities:

============================================================
1. HEADER DETECTION
============================================================
HEADER DETECTION RULES (CRITICAL):
- Only detect a header in the FIRST BATCH of each table.
- Only inspect the FIRST 5 ROWS of that batch for header candidates.
- If multiple header-like rows appear, KEEP ONLY THE FIRST.
- Never create duplicate header names such as "Country (2)".
- Never merge multiple header blocks.
- Never treat data rows as header rows.

If `is_first_batch` is true:
  • Inspect all rows in `current_batch_rows`.
  • Identify the header row(s).
  • A header row contains column names, units, or labels.
  • Matrix headers may span multiple rows.
  • If no explicit header exists, infer one from structure.
  • Return the detected header in the `header` field.

If `is_first_batch` is false:
  • Use `previous_header` exactly as provided.
  • Do NOT modify or reinterpret the header.
  • Do NOT invent new column names.
  • Do NOT drop columns from the header.


============================================================
2. SCHEMA CONTINUITY
============================================================

For all batches of the same table:
  • Use the same attribute names defined by the header.
  • If a column is missing in this batch, set its value to null.
  • Never introduce new attribute names.
  • Never rename attributes mid-table.
  • Never switch schema between batches.

============================================================
3. ROW NORMALISATION
============================================================

Convert each row into an object using the header as keys.

If the table is a matrix (e.g., bandwidths across columns):
  • Produce a nested object:
      {
        "matrix": { header_value: cell_value, ... }
      }

If the table is a simple row-based table:
  • Produce a flat object:
      {
        "column_name": value,
        ...
      }

If a cell is empty or missing:
  • Return null.

============================================================
4. OUTPUT FORMAT
============================================================

Return ONLY valid JSON:

{
  "header": [...],              // only on first batch or when detected
  "rows": [
      {
        "attributes": { ... },
        "confidence": float
      }
  ],
  "batch_summary": "..."
}

Rules:
- Always return valid JSON.
- Never include commentary outside JSON.
- Never invent fields not present in the header.
- Never drop fields; use null when missing.
"""

# ----------------------------------------------------------------------
# 3. WEEK 8 — DOCUMENT-LEVEL SUMMARY PROMPT (free-form)
# ----------------------------------------------------------------------

DOCUMENT_SUMMARY_PROMPT = """
You are an AI assistant that summarises commercial documents.

You will receive:
- A list of batch summaries
- Optional metadata

Your task:
Provide a concise explanation of what this document is,
based ONLY on the extracted batch summaries.

Do NOT invent rows or details.
Focus on:
- The type of document
- Its purpose
- Its contents
- Any notable characteristics

Your response should be short, clear, and helpful.
"""
# ----------------------------------------------------------------------
# 4. WEEK 8 — DOCUMENT-LEVEL SUMMARY PROMPT (free-form)
# ----------------------------------------------------------------------

BATCH_EXTRACTION_PROMPT = """
You are an AI enrichment module. You receive rows that have already been extracted,
cleaned, typed, and normalised by an upstream extraction system.

Your job is NOT to re-extract, NOT to re-normalise, and NOT to modify any numeric
values. The upstream extractor has already produced correct floats, integers, and
strings. DO NOT change them.

Your ONLY task is to enrich each row with semantic attributes.

=====================================================================
INPUT YOU WILL RECEIVE
=====================================================================

You will receive:
- "headers": the column names for this table (already correct)
- "rows": a list of rows, each row already cleaned and typed
- "raw_values": a dict mapping header → cell value for each row
- "metadata": optional contextual information (source format, page, sheet, etc.)

You MUST treat all provided values as authoritative.

=====================================================================
WHAT YOU MUST NOT DO
=====================================================================

- Do NOT modify numeric values.
- Do NOT modify strings.
- Do NOT modify headers.
- Do NOT infer schema.
- Do NOT infer column types.
- Do NOT infer totals, prices, or quantities.
- Do NOT detect currency.
- Do NOT detect headers.
- Do NOT explode matrices.
- Do NOT merge or drop rows.
- Do NOT hallucinate missing fields.
- Do NOT invent vendors, SKUs, or attributes.

=====================================================================
WHAT YOU MUST DO
=====================================================================

For each row, produce an enrichment object with:

{
  "original_cells": [...],     // EXACT row as provided
  "attributes": {
    "inferred_type": "...",    // e.g., "switch", "license", "cable", "service"
    "vendor": "...",           // e.g., "Cisco", "HP", "Dell"
    "category": "...",         // e.g., "hardware", "software", "networking"
    "service": true/false/null,
    "rating_type": null,       // optional semantic rating fields
    "rating_value": null,
    "rating_unit": null,
    "confidence": 0.0–1.0,
    "extra": {
      "notes": "Short explanation of reasoning",
      "raw_values": { ... }    // EXACT dict of header → value
    }
  }
}

Rules:
- If unsure, set confidence = 0.5 and explain in notes.
- If a semantic field cannot be inferred, set it to null.
- Always preserve the original row exactly.
- Always return valid JSON.

=====================================================================
OUTPUT FORMAT
=====================================================================

Return a JSON object with EXACTLY:

{
  "rows": [
    {
      "original_cells": [...],
      "attributes": {
        "inferred_type": "...",
        "vendor": "...",
        "category": "...",
        "service": true/false/null,
        "rating_type": null,
        "rating_value": null,
        "rating_unit": null,
        "confidence": 0.0–1.0,
        "extra": {
          "notes": "...",
          "raw_values": { ... }
        }
      }
    }
  ]
}

No other keys. No comments. No text outside JSON.

"""
