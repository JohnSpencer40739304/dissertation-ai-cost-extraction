# backend/app/services/extrapolation_orchestrator_ii.py

"""
==========================================================
Extrapolation Orchestrator II
==========================================================

Purpose
-------
Coordinates deterministic analytical tools.

The orchestrator does not perform mathematics and does not
make AI decisions.

It simply executes the prediction model chosen during the
AI conversation.

Workflow
--------
User
   │
AI Recommendation
   │
User Selection
   │
Orchestrator
   │
Prediction Model
   │
Results
"""

from typing import Dict, Any

from backend.app.tools.join_tools import (
    load_clean_tables_for_copilot,
    build_joined_table
)

from backend.app.tools.analysis_tools_ii import (
    summarize_dataset,
    detect_zero_price_patterns,
    extrapolate_missing_values,
    SUPPORTED_MODELS
)


class ExtrapolationOrchestratorII:

    # ---------------------------------------------------------
    # Constructor
    # ---------------------------------------------------------

    def __init__(self, file_id: int):

        df_main, df_attr = load_clean_tables_for_copilot(file_id)

        self.df = build_joined_table(
            df_main,
            df_attr
        )

        self.file_id = file_id

    # ---------------------------------------------------------
    # Main entry point
    # ---------------------------------------------------------

    def run(
        self,
        instruction: Dict[str, Any]
    ) -> Dict[str, Any]:

        action = instruction.get(
            "action",
            "none"
        )

        if action == "summarize":
            return self._run_summary()

        elif action == "detect_zero_prices":
            return self._run_zero_price_detection()

        elif action == "extrapolate":
            return self._run_extrapolation(instruction)

        return {

            "status": "no_action",

            "message":
                "No analytical action requested."

        }

    # ---------------------------------------------------------
    # Dataset summary
    # ---------------------------------------------------------

    def _run_summary(self):

        summary = summarize_dataset(self.df)

        return {

            "status": "success",

            "type": "summary",

            "summary": summary

        }

    # ---------------------------------------------------------
    # Zero-price analysis
    # ---------------------------------------------------------

    def _run_zero_price_detection(self):

        patterns = detect_zero_price_patterns(self.df)

        return {

            "status": "success",

            "type": "zero_price_analysis",

            "patterns": patterns

        }

    # ---------------------------------------------------------
    # Extrapolation
    # ---------------------------------------------------------

    def _run_extrapolation(
        self,
        instruction: Dict[str, Any]
    ) -> Dict[str, Any]:

        target = instruction.get(
            "target",
            "unit_price"
        )

        attribute = instruction.get(
            "attribute"
        )

        group_field = instruction.get(
            "group_field"
        )

        prediction_model = instruction.get(
            "prediction_model",
            "linear"
        )

        if not attribute or not group_field:

            return {

                "status": "error",

                "message":
                    "Missing attribute or group_field."

            }

        if prediction_model not in SUPPORTED_MODELS:

            return {

                "status": "error",

                "message":
                    f"Unsupported prediction model: "
                    f"{prediction_model}",

                "supported_models":
                    list(SUPPORTED_MODELS.keys())

            }

        result = extrapolate_missing_values(

            df=self.df,

            target=target,

            attribute=attribute,

            group_field=group_field,

            prediction_model=prediction_model

        )

        return {

            "status": "success",

            "type": "extrapolation",

            "prediction_model":
                prediction_model,

            "reply":
                f"{SUPPORTED_MODELS[prediction_model]} "
                f"prediction completed.",

            "result": result

        }