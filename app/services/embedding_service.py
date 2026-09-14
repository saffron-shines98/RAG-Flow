"""
services/embedding_service.py
==============================
Hugging Face embedding model ko load karna aur text -> vectors banana.

IMPORTANT: Model sirf EK BAAR load hota hai (module-level variable _model),
server start pe. Har request pe dobara load NAHI hota - warna API bahut slow ho jayegi.
"""

from sentence_transformers import SentenceTransformer
from app.core.config import settings

_model = None  # lazy singleton


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"[embedding_service] Loading model: {settings.EMBEDDING_MODEL_NAME} ...")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Ek ya kai texts ko embeddings (vectors) mein convert karta hai."""
    model = get_embedding_model()
    return model.encode(texts).tolist()
