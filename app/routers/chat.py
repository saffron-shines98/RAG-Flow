"""
routers/chat.py
================
General conversation endpoint - bina document context ke, seedha LLM se baat.
Jaise ChatGPT/Claude ka normal chat mode.
"""

import traceback

from fastapi import APIRouter, HTTPException

from app.services.rag_service import general_chat
from app.schemas.rag_schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["General Chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = general_chat(request.question, request.session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

    return ChatResponse(**result)