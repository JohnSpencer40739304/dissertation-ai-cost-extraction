#backend/app/summary_router.py

# REDUNDANT AND NOT USED INCLUDED WITHIN extrapoloation_orchestrator.py

from fastapi import APIRouter
from backend.app.tools.analysis_tools import (
    load_clean_tables,
    summarize_dataset,
    detect_zero_price_patterns
)

router = APIRouter()

@router.get("/{file_id}")
def get_summary(file_id: int):
    df_main, df_attr = load_clean_tables(file_id)

    summary_text = summarize_dataset(df_main)
    zero_patterns = detect_zero_price_patterns(df_main)

    return {
        "summary": summary_text,
        "zero_patterns": zero_patterns,
        "columns": list(df_main.columns),
        "total_rows": len(df_main)
    }
