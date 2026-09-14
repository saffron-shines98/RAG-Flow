"""
routers/ask.py
===============
Question-answering endpoints - session-aware, multi-document support ke saath.
"""

from fastapi import APIRouter, HTTPException

from app.services.rag_service import ask_question, reset_conversation
from app.schemas.rag_schemas import QuestionRequest, AnswerResponse, ResetSessionRequest

router = APIRouter(prefix="/ask", tags=["Question Answering"])


@router.post("", response_model=AnswerResponse)
async def ask_endpoint(request: QuestionRequest):
    """
    Question bhejo -> RAG pipeline chalega -> answer milega.

    Follow-up sawaal poochne ke liye, SAME session_id bhejo jo /ingest se mila tha -
    isse model ko pichli baatcheet yaad rahegi aur sahi PDF mein search hoga.
    """
    try:
        result = ask_question(
            question=request.question,
            top_k=request.top_k,
            session_id=request.session_id,
            source_filter=request.source_filter,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")

    return AnswerResponse(**result)


@router.post("/reset")
async def reset_session_endpoint(request: ResetSessionRequest):
    """Kisi session ki conversation memory aur attached documents clear karta hai."""
    reset_conversation(request.session_id)
    return {"message": f"Session '{request.session_id}' ki history clear ho gayi."}