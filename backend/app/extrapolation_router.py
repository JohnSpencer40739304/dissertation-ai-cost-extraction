 backend/app/extrapolation_router.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from backend.app.services.extrapolation_orchestrator import ExtrapolationOrchestrator

router = APIRouter()

class ExtrapolationRequest(BaseModel):
    file_id: int
    instruction: Dict[str, Any]

@router.post("/run")
def run_extrapolation(req: ExtrapolationRequest):
    orch = ExtrapolationOrchestrator(req.file_id)
    return orch.run(req.instruction)



"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class AnalysisRequest(BaseModel):
    method: str
    fields: List[str]
    data: Dict[str, List[Any]]

@router.post("/run")
def run_analysis(req: AnalysisRequest):
    print("=== Analysis Request ===")
    print("Method:", req.method)
    print("Fields:", req.fields)
    print("Data keys:", list(req.data.keys()))

    # Placeholder until we implement real maths
    return {
        "status": "ok",
        "result": {
            "message": f"Analysis '{req.method}' executed successfully.",
            "fields_used": req.fields
        }
    }
"""

#@router.post("/run")
#def run_analysis(req: AnalysisRequest):
#    print("Running analysis:", req.method)
#    print("Fields:", req.fields)
#    return {
#        "status": "ok",
#        "result": {
#            "message": f"Analysis '{req.method}' completed.",
#           "fields": req.fields
#        }

