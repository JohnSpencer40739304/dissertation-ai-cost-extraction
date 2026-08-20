# backend/app/services/extrapolation_orchestrator.py

from typing import Dict, Any

from backend.app.tools.join_tools import (
    load_clean_tables_for_copilot,
    build_joined_table
)

from backend.app.tools.analysis_tools import (
    summarize_dataset,
    detect_zero_price_patterns,
    extrapolate_missing_values,
    # week 12 additional features added here
    breakdown_by_attribute, 
    spline_curve,
    calculus_curve
    #monotonic_gb_curve
)


class ExtrapolationOrchestrator:

    # Load data tables needed from backend 
    def __init__(self, file_id: int):
        df_main, df_attr = load_clean_tables_for_copilot(file_id)
        self.df = build_joined_table(df_main, df_attr)
        self.file_id = file_id

    # ---------------------------------------------------------
    # Main entry point
    def run(self, instruction: Dict[str, Any]) -> Dict[str, Any]:
        action = instruction.get("action", "none")

        if action == "summarize":
            return self._run_summary()

        if action == "detect_zero_prices":
            return self._run_zero_price_detection()

        if action == "extrapolate":
            return self._run_extrapolation(instruction)
        
        # week 12 additional functions
        if action == "spline_curve":
            return self._run_spline_curve(instruction)

        if action == "calculus_curve":
            return self._run_calculus_curve(instruction)

        if action == "breakdown":
            return self._run_breakdown(instruction)
        
        #if action == "monotonic_gb":
        #    return self._run_monotonic_gb_curve(instruction)
        # end of week 12 but see below

        return {
            "status": "no_action",
            "message": "No analytical action requested."
        }

    # --------------------------------
    # Tools
    def _run_summary(self) -> Dict[str, Any]:
        summary = summarize_dataset(self.df)
        return {
            "status": "success",
            "type": "summary",
            "summary": summary
        }

    def _run_zero_price_detection(self) -> Dict[str, Any]:
        patterns = detect_zero_price_patterns(self.df)
        return {
            "status": "success",
            "type": "zero_price_analysis",
            "patterns": patterns
        }

    def _run_extrapolation(self, instruction: Dict[str, Any]) -> Dict[str, Any]:
        target = instruction.get("target", "unit_price")
        attribute = instruction.get("attribute")
        group_field = instruction.get("group_field")

        if not attribute or not group_field:
            return {
                "status": "error",
                "message": "Missing attribute or group_field for extrapolation."
            }

        result = extrapolate_missing_values(
            df=self.df,
            target=target,
            attribute=attribute,
            group_field=group_field,
            degree=1
        )

        return {
            "status": "success",
            "type": "extrapolation",
            "reply": "I've generated a new extrapolation scenario for you.",
            "result": result
        }


# ----------------- Week 12 additional analytics Features ----------
# detailed breakdown on a chosen attribute

    def _run_breakdown(self, instruction):
        attribute = instruction.get("attribute")

        if not attribute:
            return {
                "status": "error",
                "message": "Missing attribute for breakdown."
            }

        result = breakdown_by_attribute(self.df, attribute)

        return {
            "status": "success",
            "type": "breakdown",
            "attribute": attribute,
            "result": result
        }

    """
    def _run_breakdown(self, instruction):
        attribute = instruction.get("attribute")
        target = instruction.get("target", "unit_price")

        if not attribute:
            return {
                "status": "error",
                "message": "Missing attribute for breakdown."
            }

        # Basic grouped stats
        df = self.df.copy()

        if attribute not in df.columns:
            return {
                "status": "error",
                "message": f"Column '{attribute}' not found."
            }
        results = {}
        for value, group in df.groupby(attribute):
            prices = group[target].astype(float)
            results[value] = {
                "attribute_value": value,
                "row_count": len(group),
                "zero_prices": int((prices == 0).sum()),
                "non_zero_prices": int((prices > 0).sum()),
                "min": float(prices.min()) if len(prices) else None,
                "max": float(prices.max()) if len(prices) else None,
                "mean": float(prices.mean()) if len(prices) else None,
                "median": float(prices.median()) if len(prices) else None
            }
        return {
            "status": "success",
            "type": "breakdown",
            "reply": f"I've generated a breakdown grouped by '{attribute}'.",
            "attribute": attribute,
            "result": results
        }
    """


    def _run_spline_curve(self, instruction):
        attribute = instruction.get("attribute")
        group_field = instruction.get("group_field")

        if not attribute or not group_field:
            return {"status": "error", "message": "Missing attribute or group_field for spline curve."}

        result = spline_curve(self.df, attribute, group_field)

        return {
            "status": "success",
            "type": "spline_curve",
            "reply": f"I've generated a spline curve grouped by '{group_field}'.",
            "attribute": attribute,
            "group_field": group_field,
            "result": result
        }



    def _run_calculus_curve(self, instruction):
        attribute = instruction.get("attribute")
        group_field = instruction.get("group_field")

        if not attribute or not group_field:
            return {"status": "error", "message": "Missing attribute or group_field for calculus curve."}

        result = calculus_curve(self.df, attribute, group_field)

        return {
            "status": "success",
            "type": "calculus_curve",
            "reply": f"I've generated a calculus curve grouped by '{group_field}'.",
            "attribute": attribute,
            "group_field": group_field,
            "result": result
        }

"""
    def _run_monotonic_gb_curve(self, instruction):
        attribute = instruction.get("attribute")
        group_field = instruction.get("group_field")

        if not attribute or not group_field:
            return {
                "status": "error",
                "message": "Missing attribute or group_field for monotonic gradient boosting curve."
            }

        result = monotonic_gb_curve(self.df, attribute, group_field)

        return {
            "status": "success",
            "type": "monotonic_gb_curve",
            "reply": f"I've generated a monotonic gradient boosting curve grouped by '{group_field}'.",
            "attribute": attribute,
            "group_field": group_field,
            "result": result
        }
"""