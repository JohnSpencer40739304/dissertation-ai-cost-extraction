

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


            # CASE 1 — AI fallback table
            if isinstance(table, dict) and "headers" in table and "rows" in table:
                headers = [str(h).strip() for h in table["headers"]]

                for row in table["rows"]:
                    if not row:
                        continue

                    cells = [str(c).strip() if c is not None else "" for c in row]
                    row_dict = dict(zip(headers, cells))

                    normalised_rows.append({
                        "cells": cells,
                        "attributes": row_dict,
                        "page": table.get("page"),
                        "sheet": table.get("sheet"),
                        "source_format": table.get("source_format", "ai_fallback")
                    })

            # CASE 2 — Deterministic extractors 
            elif isinstance(table, dict) and "row" in table:
                cells = [str(c).strip() for c in table["row"] if c not in ("", None)]

                if cells:
                    normalised_rows.append({
                        "cells": cells,
                        "attributes": {},
                        "page": table.get("page"),
                        "sheet": table.get("sheet"),
                        "source_format": table.get("source_format")
                    })

            # CASE 3 — Unexpected format (fail-safe) interpreting as a simple list
            else:
                if isinstance(table, list):
                    cells = [str(c).strip() for c in table]
                    normalised_rows.append({
                        "cells": cells,
                        "attributes": {},
                        "page": None,
                        "sheet": None,
                        "source_format": "unknown"
                    })

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
        # 1 — Classic normalisation
        classic = ClassicNormaliser(table)
        rows = classic.run()

        # 2 — AI enrichment
        memory = MemoryStore(db_session_factory=SessionLocal)
        ai = AINormaliser(rows, file_metadata, memory)
        ai_rows = ai.run(file_metadata["file_id"])

        return {
            "classic_clean": rows,
            "ai_enriched": ai_rows
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



