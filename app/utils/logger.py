"""
utils/logger.py
================
Chota helper - poore app mein consistent tareeke se print/log karne ke liye.
Jaise "utils/" mein chote, reusable, feature-independent functions rakhte hain.
"""

from datetime import datetime


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
