"""
services/loaders/pdf_loader.py
================================
PDF files se text nikalna.
"""

from pypdf import PdfReader


def extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += (page.extract_text() or "") + "\n"
    return full_text