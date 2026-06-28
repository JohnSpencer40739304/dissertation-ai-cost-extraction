# extractor_service_iii.py
import json
import logging
import time
from pathlib import Path
from typing import List, Optional

from openai import OpenAI

from backend.modules.db import (
    UploadedFile,
    DocumentSection,
    ExtractedContent,
    SessionLocal
)
from backend.app.services.document_analysis_service import (
    DocumentAnalysis,
    DocumentAnalysisService,
)

from pathlib import Path
from pypdf import PdfReader, PdfWriter


logger = logging.getLogger(__name__)

client = OpenAI()

TESTSEC = 1  #Scientific Testing of each section
# ------------------------------------------------------------
# Result Models
class ExtractionResult:

    def __init__(
        self,
        success: bool,
        processing_time: float,
        raw_extraction: Optional[dict] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.processing_time = processing_time
        self.raw_extraction = raw_extraction
        self.error = error

    #def extract_from_analysis(
    #    self,
    #    file_id: int,
    #    analysis: DocumentAnalysis
    #) -> ExtractionResult:
        

class ExtractorServiceIII:

    def __init__(self):

        self.db = SessionLocal()

    def extract_document(
        self,
        file_id: int
    ) -> ExtractionResult:

        """
        Main orchestration method.
        """

        start = time.time()

        try:

            logger.info("=" * 60)
            logger.info("Starting Extractor Service III")
            logger.info("=" * 60)

            # ---------------------------------------------
            # STEP 1 - Load uploaded document
            logger.info("STEP 1 - Loading uploaded document...")

            uploaded = (
                self.db.query(UploadedFile)
                .filter(UploadedFile.id == file_id)
                .first()
            )
            if uploaded is None:
                raise FileNotFoundError(
                    f"Uploaded file {file_id} not found."
                )

            logger.info(
                "Document: %s",
                uploaded.filename
            )
            logger.info("STEP 2 - Loading extraction plan...")

            sections = self._load_sections(file_id)
            section = sections[TESTSEC]

            logger.info("=" * 60)
            logger.info(
                "Testing section: %s",
                section.title
            )
            logger.info(
                "Pages: %d - %d",
                section.page_start,
                section.page_end
            )
            logger.info("=" * 60)

            if not sections:
                raise RuntimeError(
                    "No document sections found. "
                    "Run DocumentSectionServiceIII first."
                )
            logger.info(
                "Loaded %d extraction sections.",
                len(sections)
            )
            logger.info("Document: %s", uploaded.filename)

            # ----------------------------------------------
            # STEP 2 - Document analysis
            logger.info("STEP 2 - Running Document Analysis...")
            analysis_service = DocumentAnalysisService()
            analysis_result = analysis_service.analyse_document(
                uploaded.storage_path
            )

            if not analysis_result.success:
                raise RuntimeError(
                    analysis_result.error
                )

            analysis = analysis_result.analysis
            self._log_document_analysis(analysis)

            # -------------------------------------------------
            # STEP 3 - Build prompt
            logger.info("STEP 3 - Building extraction prompt...")
            prompt = self._build_prompt(analysis)
            logger.info(prompt)

            # --------------------------------------------------
            # STEP 4 - Extract tables
            section = sections[TESTSEC]

            section_pdf = self._create_section_pdf(
                Path(uploaded.storage_path),
                section
            )
            raw_output = self._extract_tables(
                section_pdf,
                #Path(uploaded.storage_path),
                prompt,
                section
            )
            self._save_raw_extraction(
                file_id,
                raw_output
            )
            elapsed = round(time.time() - start, 2)
            return ExtractionResult(
                success=True,
                processing_time=elapsed,
                raw_extraction=raw_output
            )

        except Exception as ex:
            elapsed = round(time.time() - start, 2)
            logger.exception(ex)
            return ExtractionResult(
                success=False,
                processing_time=elapsed,
                error=str(ex)
            )

    # ----------------------------------------------------
    # Private Methods
    def _log_document_analysis(
        self,
        analysis: DocumentAnalysis
    ):

        logger.info("=" * 60)
        logger.info("DOCUMENT ANALYSIS")
        logger.info(
            "Type      : %s",
            analysis.document_type
        )
        logger.info(
            "Language  : %s",
            analysis.language
        )
        logger.info(
            "Strategy  : %s",
            analysis.recommended_strategy
        )
        logger.info(
            "Confidence: %.2f",
            analysis.analysis_confidence
        )
        logger.info("Processing Notes:")
        for note in analysis.processing_notes:
            logger.info("  • %s", note)
        logger.info("=" * 60)


    def _build_prompt(
        self,
        analysis: DocumentAnalysis
    ) -> str:

        """
        Original placeholder to build the extraction prompt.
        """
        notes = "\n".join(
            f"- {note}"
            for note in analysis.processing_notes
        )

        prompt = f"""
You are an expert structured data extraction engine.
The document has ALREADY been analysed.
DO NOT analyse the document again.
Instead, use the analysis below to guide extraction.
====================================================
DOCUMENT ANALYSIS
====================================================
Document Type:
{analysis.document_type}

Language:
{analysis.language}

Estimated Tables:
{analysis.estimated_tables}

Repeated Schema:
{analysis.repeated_schema}

Multi-page Tables:
{analysis.multi_page_tables}

Recommended Strategy:
{analysis.recommended_strategy}

Processing Notes:
{notes}

====================================================
YOUR TASK
====================================================
Process the uploaded PDF page by page.

For EACH page:

1. Identify every table.
2. Extract every table.
3. Continue until every page has been processed.

Do not stop after extracting the first product family.

A page may contain multiple unrelated tables.
All must be returned.


The document may contain:
- multiple tables
- multi-page tables
- repeated schemas
- merged headers
- hierarchical headers
Preserve the document structure exactly.

Do NOT summarise.
Do NOT omit rows.
Do NOT invent values.
Do NOT translate headers.
Return ONLY valid JSON.
Do not wrap the JSON in markdown.
Do not include explanations.
Do not include comments.
Do not include code fences.

The response must be directly parsable by json.loads().

====================================================
OUTPUT SCHEMA
====================================================
{{
    "tables": [
        {{
            "sheet_name": "Section name or worksheet",
            "header": [
                "Column 1",
                "Column 2"
            ],
            "rows": [
                {{
                    "Column 1": "...",
                    "Column 2": "..."
                }}
            ]
        }}
    ]
}}

Return JSON only.
"""

        logger.info("=" * 60)
        logger.info("PROMPT SENT TO OPENAI")
        logger.info("=" * 60)
        logger.info(prompt)
        logger.info("=" * 60)
        logger.info("Extraction prompt built successfully.")
        return prompt

    def _load_sections(
        self,
        file_id: int
    ):
        rows = (
            self.db.query(DocumentSection)
            .filter(DocumentSection.file_id == file_id)
            .order_by(DocumentSection.section_number)
            .all()
        )
        return rows
    
    def _extract_tables(
        self,
        path: Path,
        prompt: str,
        section
    ) -> dict:

        logger.info("STEP 4 - Uploading document...")

        section_prompt = f"""
====================================================
EXTRACTION CONTEXT
====================================================
Section:
{section.title}

Expected Tables:
{section.expected_tables}

Planner Notes:
{chr(10).join(section.notes)}

====================================================
YOUR TASK
====================================================
The uploaded PDF contains only this logical section.
Extract every table.
Do not omit rows.
Do not merge columns.
Preserve headers exactly.
Return valid JSON only.
"""

        full_prompt = prompt + "\n\n" + section_prompt

        with open(path, "rb") as f:
            uploaded_file = client.files.create(
                file=f,
                purpose="user_data"
            )

        logger.info(
            "OpenAI File ID: %s",
            uploaded_file.id
        )
        logger.info("STEP 5 - Sending extraction request...")

        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "system",
                    "content": full_prompt
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
                            "text": "Extract the requested document section."
                        }
                    ]
                }
            ]
        )

        logger.info("=" * 60)
        logger.info("RAW OPENAI RESPONSE")
        logger.info("=" * 60)
        logger.info(response.output_text)
        logger.info("=" * 60)

        return {
            "response_text": response.output_text
        }

    def _validate_output(
        self,
        raw_output: dict
    ) -> bool:
        """
        Validate AI response before sending to the normaliser.
        TODO
        """
        pass


    def _create_section_pdf(
        self,
        source_pdf: Path,
        section
    ) -> Path:

        reader = PdfReader(source_pdf)
        writer = PdfWriter()

        logger.info("=" * 60)
        logger.info("Creating temporary section PDF")
        logger.info("Section : %s", section.title)
        logger.info(
            "Pages   : %d - %d",
            section.page_start,
            section.page_end
        )

        #for page in range(section.page_start, section.page_end + 1):
        for page in range(section.page_start - 1, section.page_end):

            logger.info("Adding original page %d", page)

            writer.add_page(reader.pages[page])

        # --------------------------------------------------------
        # Create debug folder
        output_dir = Path("debug_sections")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / (
            f"file_{section.file_id}_"
            f"section_{section.section_number:02d}.pdf"
        )
        with open(output_file, "wb") as f:
            writer.write(f)
        logger.info("Section PDF saved to: %s", output_file)
        logger.info("=" * 60)
        return output_file




    def _save_raw_extraction(
        self,
        file_id: int,
        raw_output: dict
    ):
        logger.info("=" * 60)
        logger.info("SAVING RAW EXTRACTION")
        logger.info("=" * 60)
        response_text = raw_output["response_text"]
        logger.info(
            "OpenAI response length: %d characters",
            len(response_text)
        )
        self.db.query(ExtractedContent).filter(
            ExtractedContent.file_id == file_id
        ).delete() 
        # Save returned JSON extract
        extracted = ExtractedContent(
            file_id=file_id,
            raw_tables=response_text,
            raw_text=None,
            raw_images=[],

            extraction_metadata={
                "extractor": "Extractor III",
                "strategy": "section_by_section",
                "response_length": len(response_text)
            },
            extraction_status="success"
        )
        self.db.add(extracted)
        self.db.commit()
        self.db.refresh(extracted)
        logger.info(
            "Saved ExtractedContent ID %d",
            extracted.id
        )
        logger.info("=" * 60)

        return extracted
    




