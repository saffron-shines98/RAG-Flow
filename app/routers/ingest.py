from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.dependencies.file_handler import save_uploaded_pdf
from app.services.rag_service import ingest_document
from app.schemas.rag_schemas import IngestResponse

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("", response_model=IngestResponse)
async def ingest_pdf_endpoint(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(default=None),
):
    """
    PDF upload karo.

    - session_id NAHI doge  -> NAYA chat/session ban jayega (naya unique ID milega response mein)
    - session_id DOGE       -> is PDF ko us EXISTING session/chat mein add kar diya jayega
                               (jaise ek chat mein doosri file attach karna)
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sirf PDF files allowed hain.")

    save_path = save_uploaded_pdf(file)

    try:
        result = ingest_document(save_path, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    return IngestResponse(
        message="PDF successfully processed aur session se jud gaya.",
        filename=file.filename,
        chunks_created=result["chunks_created"],
        session_id=result["session_id"],
    )