import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

# Probably redendant as DF frame is sent the orchestrator. 
from backend.modules.db import get_db
from backend.modules.models import CleanCostData, CleanCostDataAttributes

# ---- Week 12 additional tools
from scipy.optimize import curve_fit
from scipy.interpolate import PchipInterpolator
import numpy as np
import pandas as pd

def log_function(x, a, b, c, d):
    result = (a * np.log(b * x + 1) + c) + d
    return np.where(np.isnan(result), np.nanmean(result), result)
# --- end of week 12 here but see below


# ------------------------------------------------ --
# Load dataset from PostgreSQL (raw tables)
# Probably redendant as DF frame is sent the orchestrator to be used below. 
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


# -------------------------------------- ---------------
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


# -------------------------------------------------------
# Regression helpers
def build_regression_model(degree: int = 1) -> Pipeline:
    return Pipeline([
        ("poly", PolynomialFeatures(degree=degree, include_bias=False)),
        ("lin", LinearRegression())
    ])


# -------------------------------------------
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


#------- NEW FEATURES WEEK 12 ------
# Breakdown by attribute 
def breakdown_by_attribute(df, attribute):
    if attribute not in df.columns:
        return {"error": f"Column '{attribute}' not found in dataset."}

    grouped = df.groupby(attribute)["unit_price"]
    result = []

    for value, series in grouped:
        total = len(series)
        zeros = int((series == 0).sum())
        nonzero_series = series[series > 0]

        result.append({
            "attribute_value": value,
            "total_rows": total,
            "zero_prices": zeros,
            "nonzero_prices": total - zeros,
            "mean_nonzero_price": float(nonzero_series.mean()) if len(nonzero_series) else None,
            "median_nonzero_price": float(nonzero_series.median()) if len(nonzero_series) else None,
            "min_nonzero_price": float(nonzero_series.min()) if len(nonzero_series) else None,
            "max_nonzero_price": float(nonzero_series.max()) if len(nonzero_series) else None
        })

    return result

# -------- derived from a real world dev I did for Gartner benchmark--- 
def calculus_curve(df, attribute, group_field):
    # Validate columns
    if attribute not in df.columns:
        return {"error": f"Column '{attribute}' not found."}
    if group_field not in df.columns:
        return {"error": f"Column '{group_field}' not found."}

    results = []

    # --- NUMERIC CLEANING (same as extrapolation) ---
    df = df.copy()
    df["_attr"] = pd.to_numeric(df[attribute], errors="coerce")
    df["_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # Drop rows where either attribute or price is not numeric
    df = df[df["_attr"].notnull() & df["_price"].notnull()]
    # --- SAFE LOG FUNCTION (no invalid domain) ---
    def safe_log_function(x, a, b, c, d):
        # Ensure x is non-negative
        x = np.maximum(x, 0)

        # Ensure log argument is positive
        bx1 = b * x + 1
        bx1 = np.maximum(bx1, 1e-9)

        return (a * np.log(bx1) + c) + d

    # Group by the chosen field (e.g., Country)
    for group_value, group in df.groupby(group_field):

        # Training data = rows with real prices
        train = group[group["_price"] > 0]

        # Need enough points to fit a curve
        if len(train) < 5:
            continue
        speeds_train = train["_attr"].values
        prices_train = train["_price"].values

        # Initial guess for curve_fit
        p0 = [1.0, 1e-3, 1.0, 1.0]

        # Parameter bounds to prevent explosion
        bounds = (
            [0.0, 0.0, -np.inf, -np.inf],   # lower bounds
            [np.inf, 1.0, np.inf, np.inf]   # upper bounds
        )

        # Fit calculus/logarithmic curve
        try:
            popt, _ = curve_fit(
                safe_log_function,
                speeds_train,
                prices_train,
                p0=p0,
                bounds=bounds,
                maxfev=5000
            )
        except Exception:
            continue

        # Predict only for missing (zero-price) rows
        missing = group[group["_price"] == 0]

        for _, row in missing.iterrows():
            speed = row["_attr"]
            curve_val = float(safe_log_function(speed, *popt))

            # --- leave blank if nonsense (negative values not possible)
            if not np.isfinite(curve_val):
                continue
            if curve_val <= 0:
                continue
            results.append({
                "cost_item_id": int(row["id"]),   # REAL Excel row ID
                "predicted_value": curve_val,
                "flag": "curve",
                "method": "calculus",
                "confidence": 1.0
            })

    return results




def spline_curve(df, attribute, group_field):
    # Validate columns
    if attribute not in df.columns:
        return {"error": f"Column '{attribute}' not found."}
    if group_field not in df.columns:
        return {"error": f"Column '{group_field}' not found."}

    results = []

    # --- NUMERIC CLEANING (same as extrapolation) ---
    df = df.copy()
    df["_attr"] = pd.to_numeric(df[attribute], errors="coerce")
    df["_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # Drop rows where either attribute or price is not numeric
    df = df[df["_attr"].notnull() & df["_price"].notnull()]

    # Group by the chosen field (e.g., Country)
    for group_value, group in df.groupby(group_field):
        # Training data = rows with real prices
        train = group[group["_price"] > 0]
        # Need enough points to fit a spline
        if len(train) < 5:
            continue
        speeds_train = train["_attr"].values
        prices_train = train["_price"].values
        # Fit monotonic PCHIP spline
        try:
            pchip = PchipInterpolator(speeds_train, prices_train)
        except Exception:
            continue
        # Predict only for missing (zero-price) rows
        missing = group[group["_price"] == 0]
        for _, row in missing.iterrows():
            speed = row["_attr"]
            curve_val = float(pchip(speed))
            # --- if nonsense leave blank
            if curve_val <= 0:
                continue
            results.append({
                "cost_item_id": int(row["id"]),   # REAL Excel row ID
                "predicted_value": curve_val,
                "flag": "curve",
                "method": "spline",
                "confidence": 1.0
            })

    return results

# week 12 experiment with advanced maths
"""
from sklearn.ensemble import HistGradientBoostingRegressor
import numpy as np
import pandas as pd

def monotonic_gb_curve(df, attribute, group_field):
    # Validate columns
    if attribute not in df.columns:
        return {"error": f"Column '{attribute}' not found."}
    if group_field not in df.columns:
        return {"error": f"Column '{group_field}' not found."}

    results = []

    # --- NUMERIC CLEANING (same as extrapolation) ---
    df = df.copy()
    df["_attr"] = pd.to_numeric(df[attribute], errors="coerce")
    df["_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df = df[df["_attr"].notnull() & df["_price"].notnull()]

    # Group by the chosen field (e.g., Country)
    for group_value, group in df.groupby(group_field):

        # Training data = rows with real prices
        train = group[group["_price"] > 0]

        # Need enough points for boosting
        if len(train) < 10:
            continue

        X_train = train[["_attr"]].values
        y_train = train["_price"].values

        # --- MONOTONIC GRADIENT BOOSTING ---
        # price must increase with speed → monotonic +1
        model = HistGradientBoostingRegressor(
            monotonic_cst=[1],
            max_iter=300,
            learning_rate=0.05,
            max_leaf_nodes=31,
            min_samples_leaf=5,
            l2_regularization=0.1
        )

        try:
            model.fit(X_train, y_train)
        except Exception:
            continue

        # Predict only for missing (zero-price) rows
        missing = group[group["_price"] == 0]

        for _, row in missing.iterrows():
            speed = row["_attr"]
            pred = float(model.predict(np.array([[speed]]))[0])

            # Skip invalid or negative predictions
            if not np.isfinite(pred):
                continue
            if pred <= 0:
                continue

            results.append({
                "cost_item_id": int(row["id"]),   # REAL Excel row ID
                "predicted_value": pred,
                "flag": "curve",
                "method": "monotonic_gb",
                "confidence": 1.0
            })

    return results
"""