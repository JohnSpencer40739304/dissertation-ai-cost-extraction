# backend/app/tools/join_tools.py

import pandas as pd
from backend.modules.db import SessionLocal
from backend.modules.models import CleanCostData, CleanCostDataAttributes

# =====================================
# WEEK 10 — CLEAN TABLES FOR COPILOT  returns exactly TWO DataFrames.
def load_clean_tables_for_copilot(file_id: int):
    db = SessionLocal()
    # Load main rows and then Load attributes for those rows
    rows = (
        db.query(CleanCostData)
        .filter(CleanCostData.file_id == file_id)
        .all()
    )
    attrs = (
        db.query(CleanCostDataAttributes)
        .filter(CleanCostDataAttributes.cost_item_id.in_([r.id for r in rows]))
        .all()
    )
    # Convert to DataFrames
    df_main = pd.DataFrame([
        {
            "id": r.id,
            "file_id": r.file_id,
            "sheet_name": r.sheet_name,
            "table_index": r.table_index,
            "row_index": r.row_index,
            "item_description": r.item_description,
            "unit_price": r.unit_price,
            "currency": r.currency,
            "quantity": r.quantity,
            "ai_confidence_overall": r.ai_confidence_overall,
        }
        for r in rows
    ])
    df_attr = pd.DataFrame([
        {
            "id": a.id,
            "cost_item_id": a.cost_item_id,
            "attribute_name": a.attribute_name,
            "attribute_value": a.attribute_value,
            "extraction_method": a.extraction_method,
            "confidence_score": a.confidence_score,
        }
        for a in attrs
    ])
    return df_main, df_attr


# ============================================================
# WEEK 9 — Excel friendly format of lists (returns DICT for Excel)

def load_clean_tables_for_excel(file_id: int):
    df_main, df_attr = load_clean_tables_for_copilot(file_id)

    excel_main = [list(df_main.columns)] + df_main.values.tolist()
    excel_attr = [list(df_attr.columns)] + df_attr.values.tolist()

    return {
        "excel_main": excel_main,
        "excel_attr": excel_attr,
    }

# ============================================================
# Joined table (mimics joined table in excel and used by AI and extrapolation service

def build_joined_table(df_main: pd.DataFrame, df_attr: pd.DataFrame) -> pd.DataFrame:

    if df_main.empty:
        return pd.DataFrame()

    # Pivot attributes: cost_item_id → columns
    if not df_attr.empty:
        df_pivot = df_attr.pivot_table(
            index="cost_item_id",
            columns="attribute_name",
            values="attribute_value",
            aggfunc="first"
        ).reset_index()
    else:
        df_pivot = pd.DataFrame()

    # Merge main table with pivoted attributes
    if not df_pivot.empty:
        df_joined = pd.merge(
            df_main,
            df_pivot,
            left_on="id",
            right_on="cost_item_id",
            how="left"
        )
    else:
        df_joined = df_main.copy()

    return df_joined
