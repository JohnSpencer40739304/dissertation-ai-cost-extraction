#def adapt_unified_extractor_output(raw):
#    if isinstance(raw, dict) and "tables" in raw:
#        return raw

#    if isinstance(raw, list) and len(raw) > 0 and "rows" in raw[0]:
#        adapted = {"tables": []}

#        for idx, table in enumerate(raw):
#            adapted["tables"].append({
#                "sheet_name": f"Sheet{idx+1}",
#                "table_index": idx,
#                "title": None,
#                "header": table.get("headers", []),   # <-- IMPORTANT
#                "rows": table.get("rows", [])
#            })

#        return adapted

#    return {"tables": []}


def adapt_unified_extractor_output(raw):

    # If unified extractor already returned a dict with tables, adapt them
    if isinstance(raw, dict) and "tables" in raw:
        adapted_tables = []

        for idx, t in enumerate(raw["tables"]):
            adapted_tables.append({
                "sheet_name": t.get("sheet_name", f"Sheet{idx+1}"),
                "table_index": t.get("table_index", idx),
                "title": t.get("title"),
                "header": t.get("headers", []),   # <-- FIX: normalisation expects "header"
                "rows": t.get("rows", [])
            })

        return {
            "tables": adapted_tables,
            "text": raw.get("text_blocks", []),
            "images": raw.get("images", []),
            "metadata": raw.get("metadata", {})
        }

    # Legacy fallaback for a table list
    if isinstance(raw, list) and len(raw) > 0 and "rows" in raw[0]:
        adapted = {"tables": []}

        for idx, table in enumerate(raw):
            adapted["tables"].append({
                "sheet_name": f"Sheet{idx+1}",
                "table_index": idx,
                "title": None,
                "header": table.get("headers", []),
                "rows": table.get("rows", [])
            })

        return adapted

    return {"tables": []}

