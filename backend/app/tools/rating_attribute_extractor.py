"""
Rating Attribute Extractor
--------------------------
Pattern classifier for rating attributes:

- categorical_label
- numeric_tier
- numeric_unit_tier
- range_label
- ordinal_label
- geographic_label
- temporal_label
- boolean_label
- unknown_label
"""

import re

class RatingAttributeExtractor:

    @staticmethod
    def classify_pattern(value):
         #Classifies a rating attribute into a universal pattern.
        if value is None:
            return "unknown_label"

        text = str(value).strip()

        # 1   Boolean labels
        if text.lower() in {"yes", "no", "true", "false", "included", "optional"}:
            return "boolean_label"

        # 2  Numeric tier (pure numbers)
        if re.fullmatch(r"\d+", text):
            return "numeric_tier"

        # 3    Numeric + unit (10 Mbps, 4 GB, 2 vCPU)
        if re.fullmatch(r"\d+(\.\d+)?\s*[A-Za-z]+", text):
            return "numeric_unit_tier"

        # 4  Ranges such as (20–30, 30-40, 1–3)
        if re.fullmatch(r"\d+\s*[-–]\s*\d+", text):
            return "range_label"

        # 5  Ordinal labels (Zone 1, Tier A, Level 3)
        if re.fullmatch(r"(zone|tier|level)\s*\w+", text.lower()):
            return "ordinal_label"

        # 6  Geographic labels (FR, GB, ES, IT, NAM, APAC)
        if re.fullmatch(r"[A-Z]{2,4}", text):
            return "geographic_label"

        # 7   Temporal labels (12M, 24M, 36M, 1Y, 3Y)
        if re.fullmatch(r"\d+\s*(m|y)", text.lower()):
            return "temporal_label"

        # 8  Categorical labels (Basic, Pro, Gold, Red, Large)
        if len(text.split()) == 1 and text.isalpha():
            return "categorical_label"

        # 9  Fallback
        return "unknown_label"

    @staticmethod
    def enrich_row(row):
        #Adds rating_pattern and rating_raw to a row.
        at_name = row["attributes"].get("rating_attribute_name")
        at_value = row["attributes"].get("rating_attribute_value")

        pattern = RatingAttributeExtractor.classify_pattern(at_value)
        row["attributes"]["rating_pattern"] = pattern
        row["attributes"]["rating_raw"] = at_value
        return row

    @staticmethod
    def process(rows):
        enriched = []
        for row in rows:
            enriched.append(RatingAttributeExtractor.enrich_row(row))
        return enriched
