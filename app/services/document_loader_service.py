"""
services/document_loader_service.py
=====================================
Dispatcher - file ka extension dekh ke, sahi loader ko call karta hai.
"""

import os
from app.services.loaders import pdf_loader, docx_loader, txt_loader, image_loader

SUPPORTED_LOADERS = {
    ".pdf": pdf_loader.extract_text,
    ".docx": docx_loader.extract_text,
    ".txt": txt_loader.extract_text,
    ".png": image_loader.extract_text,
    ".jpg": image_loader.extract_text,
    ".jpeg": image_loader.extract_text,
}


def is_supported(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_LOADERS


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in SUPPORTED_LOADERS:
        supported = ", ".join(SUPPORTED_LOADERS.keys())
        raise ValueError(f"'{ext}' format supported nahi hai. Supported formats: {supported}")

    loader_function = SUPPORTED_LOADERS[ext]
    return loader_function(file_path)