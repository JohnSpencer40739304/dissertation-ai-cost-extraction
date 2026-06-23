import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

from backend.modules.db import get_db
from backend.modules.models import CleanCostData, CleanCostDataAttributes


# ---------------------------------------------------------
# Load dataset from PostgreSQL (raw tables)
def load_clean_tables(file_id: int):
    db: Session = next(get_db())
    rows_main = (
        db.query(CleanCostData)
        .filter(CleanCostData.file_id == file_id)
        .all()
    )
    rows_attr = (
        db.query(CleanCostDataAttributes)
        .filter(CleanCostDataAttributes.file_id == file_id)
        .all()
    )
    df_main = pd.DataFrame([r.to_dict() for r in rows_main])
    df_attr = pd.DataFrame([r.to_dict() for r in rows_attr])

    return df_main, df_attr


# ---------------------------------------------------------
# Basic diagnostics
def summarize_dataset(df: pd.DataFrame) -> str:
    if df.empty:
        return "Dataset is empty."
    summary = [
        f"Total rows: {len(df)}",
        f"Columns: {', '.join(df.columns)}",
    ]
    if "unit_price" in df.columns:
        zero_count = (df["unit_price"] == 0).sum()
        summary.append(f"Zero unit_price entries: {zero_count}")
    return "\n".join(summary)


def detect_zero_price_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    if "unit_price" not in df.columns:
        return {"error": "Missing unit_price field"}
    zeros = (df["unit_price"] == 0).sum()
    total = len(df)
    return {
        "total_rows": total,
        "zero_prices": zeros,
        "nonzero_prices": total - zeros
    }


# ---------------------------------------------------------
# Regression helpers
def build_regression_model(degree: int = 1) -> Pipeline:
    return Pipeline([
        ("poly", PolynomialFeatures(degree=degree, include_bias=False)),
        ("lin", LinearRegression())
    ])


# ---------------------------------------------------------
# Extrapolation engine (agnostic)
def extrapolate_missing_values(
    df: pd.DataFrame,
    target: str,
    attribute: str,
    group_field: str,
    degree: int = 1
) -> List[Dict[str, Any]]:
    df = df.copy()
    # Convert attribute to numeric where possible
    df["_attr"] = pd.to_numeric(df[attribute], errors="coerce")

    results = []

    # Loop over each group (e.g., Country)
    for group, gdf in df.groupby(group_field):
        # Training rows: non-zero prices AND numeric attribute
        train = gdf[(gdf[target] > 0) & (gdf["_attr"].notnull())]

        if len(train) < 3:
            continue
        # Fit regression model
        X = train["_attr"].values.reshape(-1, 1)
        y = train[target].values

        model = build_regression_model(degree)
        model.fit(X, y)

        # Missing rows: zero prices AND numeric attribute
        missing = gdf[(gdf[target] == 0) & (gdf["_attr"].notnull())]

        for _, row in missing.iterrows():
            #pred = float(model([[row["_attr"]]]))
            pred = float(model.predict([[row["_attr"]]])[0])

            results.append({
                "cost_item_id": int(row["id"]),   # Excel column name
                "predicted_value": pred,
                "flag": "predicted",
                "method": f"poly_degree_{degree}",
                "confidence": 0.9
            })
    return results



