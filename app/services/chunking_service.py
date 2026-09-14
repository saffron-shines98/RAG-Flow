"""
services/chunking_service.py
=============================
Sirf ek kaam: bade text ko chote overlapping chunks mein todna.
"""

from typing import List


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks
