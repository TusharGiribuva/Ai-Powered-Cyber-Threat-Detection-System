from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    text: str
    type: Optional[str] = "auto"


class ChatRequest(BaseModel):
    message: str