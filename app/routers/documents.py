"""
routers/documents.py
=====================
Documents dekhne ke endpoints - saare documents globally, ya kisi
specific session/chat ke saath attached documents.
"""

from fastapi import APIRouter

from app.services.rag_service import get_available_documents, get_session_documents
from app.schemas.rag_schemas import DocumentsListResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=DocumentsListResponse)
async def list_documents_endpoint():
    """Abhi tak upload ki gayi saari files ke naam deta hai (globally, sabhi sessions se)."""
    docs = get_available_documents()
    return DocumentsListResponse(documents=docs)


@router.get("/session/{session_id}", response_model=DocumentsListResponse)
async def list_session_documents_endpoint(session_id: str):
    """Kisi specific session/chat ke saath abhi tak kaunsi files attached hain."""
    docs = get_session_documents(session_id)
    return DocumentsListResponse(documents=docs)