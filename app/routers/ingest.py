from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.dependencies.file_handler import save_uploaded_file
from app.services.rag_service import ingest_document
from app.services.document_loader_service import is_supported, SUPPORTED_LOADERS
from app.schemas.rag_schemas import IngestResponse

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("", response_model=IngestResponse)
async def ingest_file_endpoint(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(default=None),
):
    if not is_supported(file.filename):
        supported = ", ".join(SUPPORTED_LOADERS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Ye format supported nahi hai. Supported formats: {supported}",
        )

    save_path = save_uploaded_file(file)

    try:
        result = ingest_document(save_path, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    return IngestResponse(
        message="Document successfully processed aur session se jud gaya.",
        filename=file.filename,
        chunks_created=result["chunks_created"],
        session_id=result["session_id"],
    )