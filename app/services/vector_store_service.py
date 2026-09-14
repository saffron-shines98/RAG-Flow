"""
services/vector_store_service.py
=================================
ChromaDB ke saath saara interaction yahan handle hota hai.

Har chunk ke saath uska SOURCE (kaunsi file se aaya) METADATA mein store hota hai.
Naya PDF aane pe PURANA DATA DELETE NAHI hota - sirf naya ADD hota hai,
isliye multiple PDFs ek saath ChromaDB mein reh sakte hain.
"""

import uuid
import chromadb
from app.core.config import settings

_client = None  # lazy singleton


def get_chroma_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    return _client


def get_or_create_collection():
    """
    Collection SIRF EK BAAR banti hai (agar exist nahi karti), fir usi mein
    naye documents ADD hote jaate hain - DELETE nahi hota.
    """
    client = get_chroma_client()
    try:
        return client.get_collection(name=settings.COLLECTION_NAME)
    except Exception:
        return client.create_collection(name=settings.COLLECTION_NAME)


def store_chunks(chunks: list[str], embeddings: list[list[float]], source_filename: str) -> None:
    """
    Chunks + embeddings ko store karta hai, HAR CHUNK ke saath uska
    'source' (filename) bhi metadata mein tag karta hai.
    Purana data DELETE nahi hota - naya document sirf ADD hota hai.
    """
    collection = get_or_create_collection()

    # Har chunk ke liye GLOBALLY UNIQUE id (uuid se), taaki alag PDFs ke IDs clash na karein
    ids = [f"{source_filename}_{uuid.uuid4().hex[:8]}_{i}" for i in range(len(chunks))]

    metadatas = [{"source": source_filename} for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search_similar_chunks(query_embedding: list[float], top_k: int, source_filter=None) -> list[dict]:
    """
    Query embedding ke sabse "close" chunks dhoondta hai.

    source_filter:
        - None                -> SAARI uploaded PDFs mein search
        - "a.pdf"              -> SIRF ek specific PDF mein search
        - ["a.pdf", "b.pdf"]   -> in DONO PDFs mein search

    Returns: list of {"text": chunk_text, "source": filename}
    """
    collection = get_or_create_collection()

    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
    }

    if source_filter:
        if isinstance(source_filter, str):
            query_kwargs["where"] = {"source": source_filter}
        elif isinstance(source_filter, list) and len(source_filter) > 0:
            query_kwargs["where"] = {"source": {"$in": source_filter}}

    results = collection.query(**query_kwargs)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    return [
        {"text": doc, "source": meta.get("source", "unknown")}
        for doc, meta in zip(documents, metadatas)
    ]


def list_all_sources() -> list[str]:
    """ChromaDB mein abhi tak kaunsi-kaunsi PDFs upload ki gayi hain, unki list deta hai."""
    collection = get_or_create_collection()
    all_data = collection.get()
    sources = {meta.get("source", "unknown") for meta in all_data["metadatas"]}
    return sorted(sources)