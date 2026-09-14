"""
schemas/rag_schemas.py
=======================
Ye define karta hai ki API ko konsa DATA aana/jaana chahiye - aur FastAPI
KHUD-BA-KHUD validate kar deta hai (jaise agar 'question' string na ho, toh
error de dega, bina humein manually check kiye).

Router files (routers/) inhi schemas ko "type hint" ke roop mein use karenge.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class QuestionRequest(BaseModel):
    question: str = Field(..., description="User ka sawaal", min_length=1)
    top_k: int = Field(default=3, description="Kitne relevant chunks retrieve karne hain", ge=1, le=10)
    session_id: str = Field(default="default", description="Conversation ko track karne ke liye")
    source_filter: Optional[str] = Field(default=None, description="Agar diya, sirf isi PDF filename mein search hoga")


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources_used: List[str]
    session_id: str


class IngestResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int
    session_id: str

class ResetSessionRequest(BaseModel):
    session_id: str = Field(default="default")
