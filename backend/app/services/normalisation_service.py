

#import pandas as pd
#import numpy as np
#import re
import json
from typing import List, Dict, Any
from backend.app.tools.date_parser import looks_like_date, normalise_date # later added as dates are a complex subject


# Open AI nomrmaliser moved to below to within a function so it is not called before it is needed and to avoid fast API Startup issues
# from openai import OpenAI
# client = OpenAI() 

# originally result returned only a dataframe, these two lines added to store in database
from backend.modules.models import CleanCostData
from backend.modules.db import SessionLocal


# Week 7 addtions to the Classic Normaliser
from backend.app.tools.currency_tool import CurrencyTool
from backend.app.tools.matrix_normaliser import MatrixNormaliser
from backend.app.tools.rating_attribute_extractor import RatingAttributeExtractor
# Week 7 but for post normalisation cleaning
from backend.app.services.normalisation_service_post import PostProcessingNormaliser
from backend.app.services.memory_store import MemoryStore



#-------------------------------------------------------------------------------------
# Classic normalisation
# New light simple version - classic normalisation fails with adhoc files. Generative AI will be used instead.
# this will return a list of rows for AI instead of a dataframe


"""
class ClassicNormaliser:
    def __init__(self, extracted_tables):
        self.extracted_tables = extracted_tables

    def run(self):
        rows = []

        for item in self.extracted_tables:
            if isinstance(item, dict) and "row" in item:
                cells = [str(c) for c in item["row"] if c not in ("", None)]
                if cells:
                    rows.append({
                        "cells": cells,
                        "page": item.get("page"),
                        "sheet": item.get("sheet"),
                        "source_format": item.get("source_format")
                    })
        return rows
"""

#The rewrite of the extractor section  to include OpenAI to read tables that were not tables create 2 types of structure outputs. So it now needs to adapt.
class ClassicNormaliser:

    def __init__(self, extracted_tables):
        self.tables = extracted_tables

    def run(self):
        normalised_rows = []

        for table in self.tables:

            #    ------------------------------------------
            #  WEEK 7 - New seperate step  for sorting out headers from rows
            headers = None
            rows = None

            if isinstance(table, dict) and "headers" in table and "rows" in table: # already existed in previous week but moved in week 7
                headers = [str(h).strip() for h in table["headers"]] # already existed in previous week but moved in week 7
                rows = table["rows"]
            elif isinstance(table, dict) and "row" in table:
                headers = None
                rows = [table["row"]]
            elif isinstance(table, list):
                headers = None
                rows = [table]
            else:
                continue

            # ------------------------------------------
            # Week 7 — Currency cleaning step - returns a currency value AND removes them from numeric fields
            if headers and rows:
                cleaned_rows, currency_context = CurrencyTool.process_table(
                    headers, rows, surrounding_text=table.get("text", "")
                )
            else:
                # No headers → clean row-by-row
                cleaned_rows = []
                currency_context = {"cell_level": [], "header_level": [], "document_level": None, "default": "USD"}

                for r in rows:
                    cleaned_row = []
                    for cell in r:
                        numeric, _ = CurrencyTool.process_cell(cell)
                        cleaned_row.append(numeric if numeric is not None else cell)
                    cleaned_rows.append(cleaned_row)

            #  ------- ---------------------------------
            # Week 7 — Matrix detection - this failed to be recognised by AI 
            if headers:
                matrix_result = MatrixNormaliser.normalise(headers, cleaned_rows, {
                    "page": table.get("page"),
                    "sheet": table.get("sheet")
                })
            else:
                matrix_result = None

            if matrix_result:
                # Add currency context
                for r in matrix_result:
                    r["attributes"]["currency_context"] = currency_context
                normalised_rows.extend(matrix_result)
                continue

            # -------------------------------
            # End of Week 7 additions above 
            # Fallback to previous week logic

            if headers:
                # CASE 1 — AI fallback table
                for row in cleaned_rows:
                    cells = [str(c).strip() if c is not None else "" for c in row]
                    row_dict = dict(zip(headers, cells))

                    normalised_rows.append({
                        "cells": cells,
                        "attributes": row_dict,
                        "page": table.get("page"),
                        "sheet": table.get("sheet"),
                        "source_format": table.get("source_format", "ai_fallback"),
                        "currency_context": currency_context
                    })

            elif isinstance(table, dict) and "row" in table:
                # CASE 2 — Deterministic extractors
                cells = [str(c).strip() for c in cleaned_rows[0] if c not in ("", None)]
                if cells:
                    normalised_rows.append({
                        "cells": cells,
                        "attributes": {},
                        "page": table.get("page"),
                        "sheet": table.get("sheet"),
                        "source_format": table.get("source_format"),
                        "currency_context": currency_context
                    })

            else:
                # CASE 3 — Unexpected format
                cells = [str(c).strip() for c in cleaned_rows[0]]
                normalised_rows.append({
                    "cells": cells,
                    "attributes": {},
                    "page": None,
                    "sheet": None,
                    "source_format": "unknown",
                    "currency_context": currency_context
                })

        #  ---------- ------------ ---------
        # Week 7  — Rating attribute patterns
        normalised_rows = RatingAttributeExtractor.process(normalised_rows)
        # ---------------end of ----------------
        return normalised_rows



# --------------------------------------------------------------------------------
# AI normalisation
# Uses AI to normalise data
# Based on normalised table above but creates another table to allow for comparison


from backend.app.tools.adaptive_batch_size import get_adaptive_batch_size
from backend.app.tools.batch_overlap import create_overlapping_batches
from backend.app.services.memory_store import MemoryStore
from backend.app.tools.prompt_templates import BATCH_PROMPT_TEMPLATE
from openai import OpenAI

class AINormaliser:
    def __init__(self, rows, file_metadata, memory_store):
        self.rows = rows
        self.file_metadata = file_metadata
        self.memory = memory_store
        self.client = OpenAI()

    def run(self, file_id):
        total = len(self.rows)
        batch_size = get_adaptive_batch_size(total)
        batch_size = max(1, batch_size or 1)
        batches = create_overlapping_batches(self.rows, batch_size)



        enriched = []

        for idx, batch in enumerate(batches):
            prev_summary = self.memory.get_previous_summary(file_id, idx)
            result, summary = self._process_batch(batch, prev_summary)
            enriched.extend(result)
            self.memory.save_summary(file_id, idx, summary)

        return enriched

    def _process_batch(self, batch, prev_summary):


        prompt = BATCH_PROMPT_TEMPLATE.format(
            user_instruction="We have recieved a messy costing file. Please normalise and extarct extract structured cost attributes.",
            source_format=self.file_metadata.get("source_format"),
            page_numbers=list({r.get("page") for r in batch}),
            sheet_names=list({r.get("sheet") for r in batch}),
            previous_summary=prev_summary or "None",
            batch_rows=batch
        )
        
       
        # first prompt attempt
        #prompt = f"""
        #User instruction: Extract structured cost attributes.
        #File type: {self.file_metadata.get('source_format')}
        #Previous batch summary:
        #{prev_summary or "None"}
        #Current batch rows:
        #{batch}
        #Return JSON:
        #{{
        #    "rows": [...],
        #    "summary": {{...}}
        #}}
        #"""
        

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = json.loads(response.choices[0].message.content)
        return content["rows"], content["summary"]
 

# -----------------------------------------------------------------------
# merges 2 above into a single call


# above modified to store data
class NormalisationService:

    def normalise(self, table, file_metadata):
        # step 0 stops the program from bugging if nothing is returned
        if not table or len(table) == 0:
            return {
                "status": "no_pricing_found",
                "classic_clean": [],
                "ai_enriched": []
            }
        all_empty = True
        for t in table:
            if isinstance(t, dict):
                if t.get("rows") or t.get("row"):
                    all_empty = False
            elif isinstance(t, list) and len(t) > 0:
                all_empty = False
        if all_empty:
            return {
                "status": "no_pricing_found",
                "classic_clean": [],
                "ai_enriched": []
            }
        

        # 1 — Classic normalisation
        classic = ClassicNormaliser(table)
        #rows = classic.run()    # Week 7 correction
        classic_rows = classic.run()

        # 2 — AI enrichment
        memory = MemoryStore(db_session_factory=SessionLocal)
        # ai = AINormaliser(rows, file_metadata, memory) # Week 7 change
        ai = AINormaliser(classic_rows, file_metadata, memory)
        ai_rows = ai.run(file_metadata["file_id"])

        # 3 — Week 7  addition -- Semantic AI + schema validation 
        post = PostProcessingNormaliser(ai_rows)
        final_rows = post.run()

        """ replaced in Week 7 by below
        return {
            "classic_clean": rows,
            "ai_enriched": ai_rows
        }
        """

        # Week 7 modification for Post normalisation service
        return {
            "classic_clean": classic_rows,
            "ai_enriched": final_rows
        }

    def save_to_db(self, file_id: int, ai_rows):
        db = SessionLocal()

        try:
            for idx, row in enumerate(ai_rows):
                record = CleanCostData(
                    file_id=file_id,
                    row_number=idx,
                    ai_attributes=row.get("attributes", {}),
                    source_format=row.get("source_format"),
                    page_number=row.get("page"),
                    sheet_number=row.get("sheet"),
                )
                db.add(record)

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

        finally:
            db.close()


