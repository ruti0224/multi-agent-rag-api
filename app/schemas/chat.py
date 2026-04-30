from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None  # הכנה לפיצ'ר ה-Citations