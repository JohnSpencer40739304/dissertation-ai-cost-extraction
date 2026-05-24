import json
from openai import OpenAI
from backend.app.tools.prompt_template_semantic import SEMANTIC_PROMPT_TEMPLATE


class PostProcessingNormaliser:
    def __init__(self, enriched_rows):
        self.rows = enriched_rows
        self.client = OpenAI()

    def run(self):
        #Calls semantic AI for each row and returns final structured output.
        final_rows = []

        for row in self.rows:
            semantic = self._call_semantic_ai(row)
            merged = self._merge(row, semantic)
            validated = self._validate_schema(merged)
            final_rows.append(validated)

        deduped = self._deduplicate(final_rows)
        return deduped
    #  ---- --------------------------------------------------------
    # 1   AI Call
    def _call_semantic_ai(self, row):
        prompt = SEMANTIC_PROMPT_TEMPLATE.format(
            row_json=json.dumps(row, indent=2)
        )
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    #  ---------------------------
    #  2  Merge batch-level +  attributes
    def _merge(self, batch_row, semantic_row):
        merged = {
            "original_cells": batch_row.get("original_cells", batch_row.get("cells")),
            "page": batch_row.get("page"),
            "sheet": batch_row.get("sheet"),
            "source_format": batch_row.get("source_format"),
            "attributes": {}
        }
        merged["attributes"].update(semantic_row)
        batch_extra = batch_row.get("attributes", {}).get("extra", {})
        semantic_extra = merged["attributes"].get("extra", {})

        merged["attributes"]["extra"] = {
            **batch_extra,
            **semantic_extra
        }
        return merged
    # -  ------------------------------------------
    # 3   Schema Validation
    def _validate_schema(self, row):
        attr = row["attributes"]
        required = [
            "service", "rating_type", "rating_value", "rating_unit",
            "unit_price", "currency", "vendor", "category",
            "extra", "confidence"
        ]
        for key in required:
            if key not in attr:
                attr[key] = None

        # Type corrections
        if attr["unit_price"] is not None:
            try:
                attr["unit_price"] = float(attr["unit_price"])
            except:
                attr["unit_price"] = None
        if attr["confidence"] is not None:
            try:
                attr["confidence"] = float(attr["confidence"])
            except:
                attr["confidence"] = 0.0
        if not isinstance(attr["extra"], dict):
            attr["extra"] = {}
        return row
    # -------------------------------------------------
    # 4 Deduplication
    def _deduplicate(self, rows):
        """
        Deduplicate rows based on service + rating_type + rating_value + currency.
        """
        seen = set()
        deduped = []

        for r in rows:
            a = r["attributes"]
            key = (
                a.get("service"),
                a.get("rating_type"),
                a.get("rating_value"),
                a.get("currency")
            )

            if key not in seen:
                seen.add(key)
                deduped.append(r)

        return deduped
