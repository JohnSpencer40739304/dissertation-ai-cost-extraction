# backend/app/services/final_schema.py

import copy

FINAL_ATTRIBUTE_SCHEMA = {
    "unit_price": float,
    "currency": str,
    "confidence": float,
    "extra": dict,
    "*": (str, float, int, dict, list)
}


class FinalSchemaEnforcer:
    def __init__(self, rows):
        self.rows = rows

    def run(self):
        final = []
        for row in self.rows:
            final.append(self._enforce_row(row))
        return final

    def _enforce_row(self, row):
        attrs = row.get("attributes", {})
        cleaned = {}
        extra = attrs.get("extra", {})

        # 1. Enforce required universal fields
        for key, expected_type in FINAL_ATTRIBUTE_SCHEMA.items():
            if key == "*":
                continue

            value = attrs.get(key)

            if value is None:
                cleaned[key] = None
                continue

            if expected_type == float:
                try:
                    cleaned[key] = float(value)
                except:
                    cleaned[key] = None
                continue

            if expected_type == dict:
                cleaned[key] = value if isinstance(value, dict) else {}
                continue

            cleaned[key] = value

        # 2. Dynamic attributes
        for k, v in attrs.items():
            if k not in FINAL_ATTRIBUTE_SCHEMA:
                cleaned[k] = v

        # 3. Merge extra
        cleaned["extra"] = extra if isinstance(extra, dict) else {}

        row["attributes"] = cleaned
        return row
