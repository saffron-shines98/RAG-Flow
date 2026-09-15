"""
services/loaders/image_loader.py
==================================
Images (JPG, PNG, etc.) se text nikalna - OCR (Optical Character Recognition) se.
"""

from PIL import Image
import pytesseract
import platform

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(file_path: str) -> str:
    image = Image.open(file_path)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text