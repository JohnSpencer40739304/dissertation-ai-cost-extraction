# backend/app/services/extrapolation_orchestrator.py

from typing import Dict, Any

from backend.app.tools.join_tools import (
    load_clean_tables_for_copilot,
    build_joined_table
)

from backend.app.tools.analysis_tools import (
    summarize_dataset,
    detect_zero_price_patterns,
    extrapolate_missing_values
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

        return {
            "status": "no_action",
            "message": "No analytical action requested."
        }

    # ---------------------------------------------------------
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
