#document_analysis_service.py
from enum import Enum
from pathlib import Path
from typing import List, Optional
import logging
import time

from pydantic import BaseModel, Field
from openai import OpenAI

logger = logging.getLogger(__name__)

client = OpenAI()


# -------------------------------------
# Extraction Strategy

class ExtractionStrategy(str, Enum):
    SINGLE_TABLE = "single_table"
    SECTION_BY_SECTION = "section_by_section"
    PAGE_BY_PAGE = "page_by_page"
    IMAGE_BASED = "image_based"
    MIXED = "mixed"


# ---------------------------------------------
# Section

class DocumentSection(BaseModel):
    title: str = Field(description="Section title")
    page_start: int
    page_end: int


# -------------------------------
# Document Analysis

class DocumentAnalysis(BaseModel):
    document_type: str
    language: str
    page_count: int
    summary: str
    estimated_tables: int
    repeated_schema: bool
    multi_page_tables: bool
    recommended_strategy: ExtractionStrategy

    #expected_output_schema: List[str]
    expected_output_schema: List[str] = Field(default_factory=list)

    #sections: List[DocumentSection]
    sections: List[DocumentSection] = Field(default_factory=list)
    processing_notes: List[str] = Field(
    default_factory=list,
    description="Human-readable observations and recommendations generated during document analysis."
    )

    analysis_confidence: float = Field(
        ge=0,
        le=1
    )


# -----------------------------
# Result
class DocumentAnalysisResult(BaseModel):
    success: bool
    processing_time: float
    analysis: Optional[DocumentAnalysis] = None
    error: Optional[str] = None


# ----------------------------------------
# Service
class DocumentAnalysisService:

    SYSTEM_PROMPT = """
You are an expert document analyst.

Your job is NOT to extract tables.

Your job is to understand the document.

Analyse:

• document type

• language

• page count

• approximate number of tables

• repeated schemas

• multi-page tables

• logical sections

Recommend the best extraction strategy.

Also generate processing notes.

Processing notes should contain concise observations that
will help both the user and the extraction pipeline.

Examples:

- Product catalogue detected.
- Tables span multiple pages.
- Repeated schemas identified.
- German language detected.
- Section-by-section extraction recommended.
- Headers appear to be hierarchical.
- Images containing tables detected.
- OCR may be required for some pages.

Return between 3 and 8 notes.

Strategies:

single_table

section_by_section

page_by_page

image_based

mixed

Return ONLY structured data.
"""


    def analyse_document(
            self,
            file_path: str
    ) -> DocumentAnalysisResult:

        start = time.time()

        try:

            path = Path(file_path)

            if not path.exists():

                raise FileNotFoundError(file_path)

            logger.info("Analysing %s", path.name)


            logger.info("Uploading document to OpenAI...")

            with open(path, "rb") as f:

                uploaded_file = client.files.create(
                    file=f,
                    purpose="user_data"
                )

            logger.info(
                "OpenAI File ID: %s",
                uploaded_file.id
            )

            """
            response = client.responses.parse(

                model="gpt-5",

                input=[

                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },

                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file": open(path, "rb")
                            },
                            {
                                "type": "input_text",
                                "text": (
                                    "Analyse this document. "
                                    "Do not extract rows. "
                                    "Produce a DocumentAnalysis."
                                )
                            }
                        ]
                    }

                ],

                text_format=DocumentAnalysis

            )"""


            response = client.responses.create(

                model="gpt-4.1",

                input=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },

                    {
                        "role": "user",
                        "content": [

                            {
                                "type": "input_file",
                                "file_id": uploaded_file.id
                            },

                            {
                                "type": "input_text",
                                #"text": "What kind of document is this? Answer in one short paragraph."
                                "text": """
Analyse this document.

Do NOT extract table rows.

Return ONLY valid JSON using exactly this schema.

{
  "document_type": "",
  "language": "",
  "page_count": 0,
  "summary": "",
  "estimated_tables": 0,
  "repeated_schema": true,
  "multi_page_tables": true,
  "recommended_strategy": "",
  "processing_notes": [],
  "analysis_confidence": 0.0
}

Rules:

- processing_notes must contain between 3 and 8 strings.

- recommended_strategy must be one of:

single_table

section_by_section

page_by_page

image_based

mixed

Return JSON only.
"""
                            }
                        ]
                    }
                ]
            )

            #analysis = response.output_parsed
            #analysis_text = response.output_text
            import json
            analysis_json = json.loads(response.output_text)

            print("\n==============================")
            #print(analysis_text)
            print(analysis_json)
            print("==============================\n")
            elapsed = round(time.time() - start, 2)
            #logger.info(analysis_text)
            #logger.info(
            #    "Document analysed successfully in %.2f seconds",
            #    elapsed
            #)

            analysis = DocumentAnalysis(**analysis_json)
            return DocumentAnalysisResult(
                success=True,
                processing_time=elapsed,
                analysis=analysis
                #error=analysis_text # debugging line
            )

        except Exception as ex:
            elapsed = round(time.time() - start, 2)
            logger.exception(ex)
            return DocumentAnalysisResult(
                success=False,
                processing_time=elapsed,
                error=str(ex)
            )