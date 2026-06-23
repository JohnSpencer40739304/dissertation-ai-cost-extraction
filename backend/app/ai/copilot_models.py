from pydantic import BaseModel
from typing import List, Any

class CopilotRequest(BaseModel):
    message: str
    headers: List[str]
    sample_rows: List[List[Any]]

class CopilotResponse(BaseModel):
    reply: str
    fields: List[str] | None = None
    method: str | None = None
    notes: str | None = None
