import json
from sqlalchemy.orm import Session

from openai import OpenAI
ai_client = OpenAI()

from backend.modules.db import SessionLocal, get_db
from backend.modules.models import (
    CleanCostData,
    CleanCostDataAttributes,
    NormalisedContent
)

from backend.app.tools.cleaning import clean_numeric

def is_numeric(v):
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        try:
            float(v)
            return True
        except:
            return False
    return False



class NormalisationService:

    def __init__(self, raw_extraction: dict):
        self.raw = raw_extraction
        self.file_id = raw_extraction.get("file_id")
        self.db = SessionLocal()

    # ---------------------------------------------------------
    # Simple Currency inference (could be made better)
    def infer_currency(self, attrs: dict) -> str:
        text = " ".join(str(v) for v in attrs.values() if v)

        if "£" in text or "GBP" in text or "UK" in text:
            return "GBP"
        if "€" in text or "EUR" in text or "EU" in text:
            return "EUR"
        if "$" in text or "USD" in text or "US" in text:
            return "USD"

        return "USD"

    # ---------------------------------------------------------
    # Main Pipeline
    def run(self):
        print("\n\n================ RAW EXTRACTION ================\n")
        print(json.dumps(self.raw, indent=2, ensure_ascii=False)[:5000])
        print("\n================================================\n\n")

        # Always read raw_tables first
        tables = self.raw.get("raw_tables") or self.raw.get("tables") or []

        print("TABLES SOURCE:", "raw_tables" if self.raw.get("raw_tables") else "tables")

        if not tables:
            return {"tables": [], "document_explanation": "", "clarifying_questions": []}

        merged_tables = []

        # --------------------------------------------------
        # For handling multiple tables
        for table_index, table in enumerate(tables):
            header = table.get("header") or table.get("headers") or []
            rows = table.get("rows", [])

            if not header or not rows:
                continue

            # Safety: skip malformed rows
            if not isinstance(rows[0], (dict, list)):
                continue

            # 1. Clean rows (support both dict and list formats)
            cleaned_rows = []

            # Case A: rows are already dicts (file 55)
            if isinstance(rows[0], dict):
                for r in rows:
                    mapped = {}
                    for h in header:
                        v = r.get(h)
                        mapped[str(h)] = clean_numeric(v)
                    cleaned_rows.append(mapped)

            # Case B: rows are lists (file 52)
            else:
                for r in rows:
                    mapped = {}
                    for i, h in enumerate(header):
                        if i < len(r):
                            mapped[str(h)] = clean_numeric(r[i])
                        else:
                            mapped[str(h)] = None
                    cleaned_rows.append(mapped)

            # 2. CLASSIFY BEFORE BUILDING final_rows
            table_type = self.classify_table_ai(header, cleaned_rows)

            # 3. If matrix → explode first
            #if table_type == "matrix_table":
            if table_type and table_type.strip().lower() == "matrix_table":
                cleaned_rows = self.explode_matrix_table(header, cleaned_rows)
            elif table_type == "garbage_table":
                continue

            # 4. Build final_rows AFTER classification/explosion
            final_rows = []
            for row_index, r in enumerate(cleaned_rows):
                final_rows.append({
                    "row_index": row_index,
                    "attributes": r,
                    "confidence": 1.0
                })

            merged_tables.append({
                "sheet_name": table.get("sheet_name", "sheet"),
                "table_index": table_index,
                "title": None,
                "rows": final_rows
            })

        merged_output = {
            "tables": merged_tables,
            "document_explanation": "Direct normalisation from extractor output.",
            "clarifying_questions": []
        }

        # Save raw normalised rows (debug)
        self.save_to_normalised_content(self.file_id, merged_output)

        # Route into universal schema
        core_rows, attribute_rows = self.route_core_and_attributes(merged_output)
        self.save_to_clean_cost_data(core_rows, attribute_rows)

        return merged_output


    # ----------------------------------------------------
    # Week 8  save method
    def save_to_normalised_content(self, file_id: int, ai_output: dict):
        db: Session = next(get_db())
        tables = ai_output.get("tables", [])

        for table in tables:
            rows = table.get("rows", [])
            source_format = table.get("sheet_name")
            for row_index, row in enumerate(rows):
                entry = NormalisedContent(
                    file_id=file_id,
                    row_index=row_index,
                    attributes=row.get("attributes", {}),
                    confidence=row.get("confidence"),
                    source_format=source_format
                )
                db.add(entry)

        db.commit()

    # ---------------------------------------------------------
    # route to the universal schema

    def route_core_and_attributes(self, merged_output):
        core_rows = []
        attribute_rows = []

        for table in merged_output.get("tables", []):
            rows = table.get("rows", [])
            table_index = table.get("table_index")
            sheet_name = table.get("sheet_name")

            for idx, row in enumerate(rows):

                attrs = row.get("attributes") or row

                # -----------------------------------------
                #   Matrix logic (Dimension + Value) as country is a common value

                if "Dimension" in attrs and "Value" in attrs:
                    item_description = attrs.get("Country") or attrs.get("ISO Ctry Code")
                    v = attrs.get("Value")
                    unit_price = float(v) if is_numeric(v) else None
                    quantity = 1

                # -----------------------------------------
                # Generic  (non-matrix rows)
                else:
                    # 1. Item description
                    item_description = next(
                        (v for v in attrs.values() if isinstance(v, str) and v.strip()),
                        "Item"
                    )

                    # 2. Unit price
                    unit_price = None
                    for v in attrs.values():
                        if is_numeric(v):
                            unit_price = float(v)
                            break
                        if isinstance(v, str) and any(sym in v for sym in ["$", "€", "£"]):
                            cleaned = v.replace("$", "").replace("€", "").replace("£", "").replace(",", "")
                            try:
                                unit_price = float(cleaned)
                                break
                            except:
                                pass

                    # 3. Quantity
                    quantity = None
                    for v in attrs.values():
                        if isinstance(v, int) and (unit_price is None or v != unit_price):
                            quantity = v
                            break

                    if quantity is None:
                        quantity = 1
                # ----------------------------
                # Row to go into core cost data sheet
                core = {
                    "file_id": self.file_id,
                    "sheet_name": sheet_name,
                    "table_index": table_index,
                    "row_index": idx,
                    "item_description": item_description,
                    "unit_price": unit_price,
                    "currency": self.infer_currency(attrs),
                    "quantity": quantity,
                    "ai_confidence_overall": row.get("confidence", 1.0)
                }
                core_rows.append(core)

                # -------------------------
                # Rows for extended attributs

                cost_item_id = len(core_rows)
                for name, value in attrs.items():
                    attribute_rows.append({
                        "cost_item_id": cost_item_id,
                        "attribute_name": name,
                        "attribute_value": value,
                        "extraction_method": "extractor",
                        "confidence_score": row.get("confidence", 1.0)
                    })
                # ----------------------------------
                # Price type  tagging
                if "price_type" in attrs and attrs["price_type"]:
                    attribute_rows.append({
                        "cost_item_id": cost_item_id,
                        "attribute_name": "price_type",
                        "attribute_value": attrs["price_type"],
                        "extraction_method": "ai",
                        "confidence_score": 1.0
                    })

        return core_rows, attribute_rows


    # ----------------------------------------
    # Save to tables 
    def save_to_clean_cost_data(self, core_rows, attribute_rows):
        db = SessionLocal()

        try:
            # Remove previous results
            db.query(CleanCostDataAttributes).filter(
                CleanCostDataAttributes.cost_item_id.in_(
                    db.query(CleanCostData.id).filter(CleanCostData.file_id == self.file_id)
                )
            ).delete(synchronize_session=False)

            db.query(CleanCostData).filter(
                CleanCostData.file_id == self.file_id
            ).delete(synchronize_session=False)

            db.flush()
            id_map = {}

            # Insert core rows
            for idx, core in enumerate(core_rows):
                obj = CleanCostData(**core)
                db.add(obj)
                db.flush()
                id_map[idx + 1] = obj.id

            # Insert attributes
            for attr in attribute_rows:
                local_id = attr["cost_item_id"]
                attr["cost_item_id"] = id_map[local_id]
                db.add(CleanCostDataAttributes(**attr))

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()


    def classify_table_ai(self, headers, sample_rows):
        # --- HARD RULE 1: Numeric headers (bandwidth matrices) ---
        numeric_headers = 0
        for h in headers:
            try:
                float(h)
                numeric_headers += 1
            except:
                pass

        if numeric_headers >= 3:
            return "matrix_table"

        # --- HARD RULE 2: 1 descriptive + many numeric columns (BVPN region matrices) ---
        numeric_cols = []
        for h in headers:
            values = [row.get(h) for row in sample_rows if isinstance(row, dict)]
            if not values:
                continue
            numeric_count = sum(1 for v in values if isinstance(v, (int, float)))
            if numeric_count >= 1:
                numeric_cols.append(h)

        descriptive_cols = [h for h in headers if h not in numeric_cols]

        if len(descriptive_cols) == 1 and len(numeric_cols) >= 2:
            return "matrix_table"

        # --- Otherwise fall back to AI ---
        prompt = f"""
        You are a table classification engine.

        Given the following table headers and sample rows,
        classify the table into one of these types:

        - simple_cost_table
        - lookup_table
        - matrix_table
        - garbage_table

        HEADERS:
        {headers}

        SAMPLE ROWS:
        {sample_rows[:5]}

        Rules:
        - If the table has 1 descriptive column and many numeric columns → matrix_table
        - If the table has 2 columns and the second looks like a price → lookup_table
        - If the table has columns like description/price/quantity → simple_cost_table
        - If the table is empty or meaningless → garbage_table

        Respond with ONLY the type name.
        """

        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return response.choices[0].message.content.strip()


    def explode_matrix_table(self, headers, rows):
        """
        Fully agnostic matrix explosion.
        Works for ANY matrix classified by AI.
        rows: list of dicts (each dict is a row mapping header -> value)
        """

        descriptive_cols = []
        dimension_cols = []

        # 1. Identify descriptive vs numeric columns
        for h in headers:
            values = [r.get(h) for r in rows]
            numeric_count = sum(1 for v in values if isinstance(v, (int, float)))
            string_count = sum(1 for v in values if isinstance(v, str) and v.strip())

            if numeric_count > string_count:
                dimension_cols.append(h)
            else:
                descriptive_cols.append(h)

        if not dimension_cols:
            return rows

        # 2. Build exploded atomic rows
        exploded = []

        for r in rows:
            desc_values = {col: r.get(col) for col in descriptive_cols}

            for dim in dimension_cols:
                val = r.get(dim)

                if isinstance(val, (int, float)):
                    exploded.append({
                        **desc_values,
                        "Dimension": dim,
                        "Value": val
                    })

        return exploded

