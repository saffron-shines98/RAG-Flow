"""
services/pdf_service.py
========================
Sirf ek kaam: PDF file se raw text nikalna.
"""

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += (page.extract_text() or "") + "\n"
    return full_text
