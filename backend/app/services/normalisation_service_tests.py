# our first major attempt at normalisation involved using Pandas and dataframes and classic normalisation techniques.
# this failed as even our test documents were very wide in style and variety. The real world would be tougher still.

# Open AI would have to kick in sooner, and standard normalisation stripped back to something simple.
# This does prove why AI style document processing was needed



import pandas as pd
import numpy as np
import re
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

class ClassicNormaliser:

    def __init__(self, table):
        self.rows = self._normalise_rows(table)

    def _normalise_rows(self, table):
        cleaned = []
        for item in table:
            # Case 1: look for nested tables that are a featured of word docs and PDFs
            if isinstance(item, list):
                for sub in item:
                    if isinstance(sub, list):
                        cleaned.append([str(x) for x in sub])
                    else:
                        cleaned.append([str(sub)])
            # Case 2: looking for rows that are basically a very long string
            elif isinstance(item, str):
                cleaned.append([item])
            # Case 3:  other cases
            else:
                cleaned.append([str(item)])

        # Case 4 - delete all  empty rows
        cleaned = [row for row in cleaned if any(cell.strip() for cell in row)]

        return cleaned

    def run(self):
        return self.rows

"""
# Using pandas and numpy to do relatively simple cleaning tasks such as removing empty rows determining column type etc.
# Based on extracted data but creates another table to allow for comparison
# DUE TO ADHOC AND VERY MESSY STRUCTURE OF SOURCE FILES - the below classic normaliser failed constrantly against real world data - replaced with simple version above

class ClassicNormaliser:

    # def __init__(self, table: List[Dict[str, Any]]): # correction for array padding to ensure all rows have the same number of units
    # table = data extracted from PDF/DOCX/Excel
    #   self.df = pd.DataFrame(table)

    # correction to above - find and then pad the rest to the longest row
    # further corrections to remove empty lines
    #def __init__(self, table: List[List[Any]]):
    def __init__(self, table: List[Any]):
        cleaned = []
        for row in table:
            if row is None:
                cleaned.append([])
            elif isinstance(row, list):
                cleaned.append(row)
            elif isinstance(row, str):
                cleaned.append([row])
            else:
                cleaned.append([str(row)])
        if not cleaned:
            cleaned = [[]]


        max_len = max(len(row) for row in table)
        padded = [
            row + [None] * (max_len - len(row))
            for row in table
        ]
        self.df = pd.DataFrame(padded)

       

    def run(self) -> pd.DataFrame:
        
        # Executes full normalisation cleaning via python
        self._remove_empty_rows()
        self._remove_empty_columns()
        self._clean_text_cells()
        self._convert_dates()   # moving dates to a seperate parsing tool
        self._detect_column_types()
        return self.df

    def _remove_empty_rows(self):
        self.df.replace("", np.nan, inplace=True)
        self.df.dropna(how="all", inplace=True)

    def _remove_empty_columns(self):
        self.df.dropna(axis=1, how="all", inplace=True)

    def _clean_text_cells(self):
        for col in self.df.columns:
            self.df[col] = self.df[col].apply(self._clean_cell)

    def _clean_cell(self, value):
        if pd.isna(value):
            return None
        text = str(value)
        text = text.replace("\n", " ").strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _detect_column_types(self):
        # Creates a dictionary mapping each column to:
        # numeric, date, currency, text, mixed
        self.column_types = {}

        """ """date format checker moved to a seperate date parsing checker
        date_patterns = [
            r"^\d{4}-\d{2}-\d{2}$",                     # 2026-05-10
            r"^\d{2}/\d{2}/\d{4}$",                     # 10/05/2026
            r"^\d{2}-\d{2}-\d{4}$",                     # 10-05-2026
            r"^\d{2}/\d{2}/\d{2}$",                     # 10/05/26
            r"^\d{1,2} [A-Za-z]{3,9} \d{4}$",           # 10 May 2026
            r"^[A-Za-z]{3,9} \d{1,2}, \d{4}$",          # May 10, 2026
            r"^\d{8}$",                                 # 20260515 Legacy system style dates
        ]
        """ """
        def _convert_dates(self):
            for col, col_type in self.column_types.items():
                if col_type == "date":
                    self.df[col] = self.df[col].apply(normalise_date)
        
        def looks_like_date(value: str) -> bool:
            for pattern in date_patterns:
                if re.match(pattern, value):
                    return True
            return False
    
        for col in self.df.columns:
            series = self.df[col]
            numeric_count = 0
            currency_count = 0
            date_count = 0
            total = len(series)

            for val in series:
                if val is None:
                    continue
                s = str(val).strip()
                # Numeric detection tests
                if re.match(r"^[€$£]?\s*\d+([.,]\d+)?$", s):
                    numeric_count += 1
                # for currency
                if re.match(r"^[€$£]", s):
                    currency_count += 1
                # Date detection tests
                if looks_like_date(s):
                    date_count += 1

            #determine what type of  column it was
            if date_count / max(total, 1) > 0.6:
                self.column_types[col] = "date"
            elif numeric_count / max(total, 1) > 0.7:
                self.column_types[col] = "numeric"
            elif currency_count / max(total, 1) > 0.5:
                self.column_types[col] = "currency"
            else:
                self.column_types[col] = "text"

"""


# --------------------------------------------------------------------------------
# AI normalisation
# Uses AI to normalise data
# Based on normalised table above but creates another table to allow for comparison


class AINormaliser:



    # replace dataframe with rows
    #def __init__(self, df: pd.DataFrame):
    #    self.df = df.copy()
    def __init__(self, rows):
        self.rows = rows

    def run(self) -> pd.DataFrame:
        enriched_rows = []

        #for _, row in self.df.iterrows(): # was for data frame, now a list
        for row in self.rows:
            ai_attrs = self._extract_ai_attributes(row)
            enriched_rows.append({
                **row.to_dict(),
                "ai_attributes": ai_attrs
            })

        return pd.DataFrame(enriched_rows)

    def _extract_ai_attributes(self, row: pd.Series) -> dict:
        # Sends each row to OpenAI and extracts structured attributes.
        from openai import OpenAI
        client = OpenAI()  

        prompt = f"""
        These inputs are generally for telecom, networking, IT infrastructure and commercial proposals.
        But could be for other cost files using a different structure such as material (steel, wood etc) and measures (2 metres high, 5mm deep..)

        Please extract structured attributes from this row of a network/telecom cost table.
        The row may contain product descriptions, service names, bandwidth, SLAs,
        hardware models, software licences, installation fees, recurring charges, etc.

        Please Return ONLY valid JSON with keys such as:
        - product_type
        - category
        - material
        - bandwidth
        - capacity
        - model
        - vendor
        - service_type
        - recurring_cost
        - one_time_cost
        - unit_of_measure
        - inferred_quantity
        - inferred_unit_price
        - inferred_total_price

        If a field is not present, omit it.
        If there are other attributes, please name appropriately.

        Row: {row.to_dict()}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print("AI extraction error:", e)
            return {}


# -----------------------------------------------------------------------
# merges 2 above into a single call

"""
# produced only resulting dataframes
class NormalisationService:

    def __init__(self):
        pass

    def normalise(self, table: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
        
        # Runs both classic and AI normalisation layers.
        #Returns two DataFrames:
        # 1 - classic_clean_df
        #2- ai_enriched_df
        
        # 1 - Python normalisation
        classic = ClassicNormaliser(table)
        classic_clean_df = classic.run()

        # 2 - AI enrichment
        ai = AINormaliser(classic_clean_df)
        ai_enriched_df = ai.run()

        return {
            "classic_clean_df": classic_clean_df,
            "ai_enriched_df": ai_enriched_df
        }
"""

# above modified to store data
class NormalisationService:

    def normalise(self, table: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
        
        # 1 — Classic Python normalisation
        classic = ClassicNormaliser(table)
        #classic_clean_df = classic.run() # for DF
        rows = classic.run()

        # 2 — AI enrichment - all DF lines below replace by rows 
        #ai = AINormaliser(classic_clean_df) 
        #ai_enriched_df = ai.run()
        ai = AINormaliser(rows)
        ai_rows = ai.run()

        """return {
            "classic_clean_df": classic_clean_df,
            "ai_enriched_df": ai_enriched_df
        }"""
        return {
            "classic_clean": rows,
            "ai_enriched": ai_rows
        }

    def save_to_db(self, file_id: int, df, ai_df):
        db = SessionLocal()

        try:
            for idx, row in ai_df.iterrows():
                record = CleanCostData(
                    file_id=file_id,
                    row_number=idx,

                    # Classic fields
                    description=row.get("description"),
                    quantity=row.get("quantity"),
                    unit_price=row.get("unit_price"),
                    total_price=row.get("total_price"),
                    currency=row.get("currency"),

                    # Dates (already ISO)
                    start_date=row.get("start_date"),
                    end_date=row.get("end_date"),
                    renewal_date=row.get("renewal_date"),

                    # AI attributes
                    ai_attributes=row.get("ai_attributes", {}),

                    # Metadata
                    source_format=row.get("source_format"),
                    page_number=row.get("page_number"),
                )

                db.add(record)

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

        finally:
            db.close()



