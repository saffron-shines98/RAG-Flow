"""
dependencies/file_handler.py
=============================
"Dependencies" folder mein wo cheezein aati hain jo multiple routes mein
REUSE ho sakti hain (jaise DB connection, authentication check, etc).

Yahan hum ek simple dependency rakhte hain: uploaded file ko disk pe save karna.
"""

import os
import shutil
from fastapi import UploadFile
from app.core.config import settings


def save_uploaded_pdf(file: UploadFile) -> str:
    """Upload hui PDF ko data/ folder mein save karta hai, aur uska path return karta hai."""
    save_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return save_path
