#document_section_service_iii.py
import json
import logging
import time
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from openai import OpenAI


from backend.modules.db import (
    SessionLocal,
    DocumentSection,
)

logger = logging.getLogger(__name__)

client = OpenAI()


# ------------------------------------------------
# Models


class ExtractionSection(BaseModel):
    title: str = Field(
        description="Logical extraction section"
    )
    page_start: int
    page_end: int
    expected_tables: int = 0
    notes: List[str] = Field(
        default_factory=list
    )

class DocumentSectionAnalysis(BaseModel):
    recommended_strategy: str
    sections: List[ExtractionSection]


class DocumentSectionResult(BaseModel):
    success: bool
    processing_time: float
    analysis: Optional[DocumentSectionAnalysis] = None
    error: Optional[str] = None


# ----------------------------------------
# Service
class DocumentSectionServiceIII:
    def __init__(self):
        self.db = SessionLocal()


    SYSTEM_PROMPT = """
You are an expert document segmentation engine.

Your task is NOT to extract tables.

Your task is NOT to analyse pricing.

Your task is ONLY to determine the logical
extraction sections.

Each extraction section should:

• preserve complete tables

• preserve business context

• avoid splitting multi-page tables

• group logically related pages

Return ONLY valid JSON.
"""

    # -------------------------
    # Public Entry Point
    def analyse_sections(
        self,
        file_id: int,
        file_path: str
    ) -> DocumentSectionResult:

        start = time.time()

        try:

            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(file_path)
            logger.info(
                "Analysing extraction sections..."
            )

            # Upload document
            with open(path, "rb") as f:
                uploaded_file = client.files.create(
                    file=f,
                    purpose="user_data"
                )

            logger.info(
                "OpenAI File ID: %s",
                uploaded_file.id
            )

            # Ask OpenAI
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
                                "text": """
Analyse this document.

Determine ONLY the logical extraction sections.

Do NOT extract rows.

Return ONLY valid JSON.

{
    "recommended_strategy":"section_by_section",
    "sections":[
        {
            "title":"",
            "page_start":0,
            "page_end":0,
            "expected_tables":0,
            "notes":[]
        }
    ]
}
Rules

• Keep multi-page tables together.

• Do not split business sections.

• expected_tables is approximate.

Return JSON only.
"""

                            }
                        ]
                    }
                ]
            )

            # Parse JSON
            section_json = json.loads(
                response.output_text
            )

            logger.info("=" * 60)
            logger.info("SECTION ANALYSIS")
            logger.info("=" * 60)
            logger.info(section_json)
            logger.info("=" * 60)

            analysis = DocumentSectionAnalysis(
                **section_json
            )
            self._save_sections(
                file_id,
                analysis
            )

            elapsed = round(
                time.time() - start,
                2
            )

            return DocumentSectionResult(
                success=True,
                processing_time=elapsed,
                analysis=analysis
            )

        except Exception as ex:
            elapsed = round(
                time.time() - start,
                2
            )
            logger.exception(ex)
            return DocumentSectionResult(
                success=False,
                processing_time=elapsed,
                error=str(ex)
            )
    # Save Section Analysis

    def _save_sections(
        self,
        file_id: int,
        analysis: DocumentSectionAnalysis
    ):

        logger.info("Saving section analysis...")

        # Remove previous analysis
        self.db.query(DocumentSection).filter(
            DocumentSection.file_id == file_id
        ).delete()

        # Save each section
        for index, section in enumerate(analysis.sections):
            row = DocumentSection(
                file_id=file_id,
                section_number=index,
                title=section.title,
                page_start=section.page_start,
                page_end=section.page_end,
                expected_tables=section.expected_tables,
                notes=section.notes
            )

            self.db.add(row)
        self.db.commit()

        logger.info(
            "Saved %s sections.",
            len(analysis.sections)
        )