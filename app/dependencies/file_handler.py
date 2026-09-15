"""
dependencies/file_handler.py
=============================
Uploaded file ko disk pe save karta hai - PDF, DOCX, TXT, ya Image, sabke liye same.
"""

import os
import shutil
from fastapi import UploadFile
from app.core.config import settings


def save_uploaded_file(file: UploadFile) -> str:
    """Upload hui file ko data/ folder mein save karta hai, aur uska path return karta hai."""
    save_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return save_path