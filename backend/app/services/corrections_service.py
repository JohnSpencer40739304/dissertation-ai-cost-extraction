from pydantic import BaseModel
from typing import Any, List, Optional

class Correction(BaseModel):
    file_id: int
    source_row_id: int
    field_type: str
    field_name: Optional[str] = None
    attribute_name: Optional[str] = None
    old_value: Any = None
    new_value: Any
    user: str

class CorrectionBatch(BaseModel):
    corrections: List[Correction]
