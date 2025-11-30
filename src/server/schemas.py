from pydantic import BaseModel
from typing import Optional

class AnalyzeRequest(BaseModel):
    code: str
    procedure_name: Optional[str] = None
