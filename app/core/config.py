"""
core/config.py
===============
Poore app ki SETTINGS ek jagah rakhi jaati hain - taaki:
- API keys, model names, folder paths sab EK jagah se manage ho
- Kal agar koi setting change karni ho (jaise embedding model), sirf yahan badlo,
  poore codebase mein dhoondhna nahi padega
- .env file se secrets (jaise GROQ_API_KEY) load hote hain, isliye code mein
  koi bhi secret HARD-CODE nahi hota
"""

import os
from dotenv import load_dotenv

load_dotenv()  # .env file ko environment variables mein load karta hai


class Settings:
    # --- Groq LLM Settings ---
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.environ.get("TAVILY_API_KEY", "")
    GROQ_MODEL: str = "openai/gpt-oss-20b"

     # --- Redis (Upstash) — conversation memory persistence ---
    UPSTASH_REDIS_URL: str = os.environ.get("UPSTASH_REDIS_URL", "")
    UPSTASH_REDIS_TOKEN: str = os.environ.get("UPSTASH_REDIS_TOKEN", "")

    # --- Embedding Settings ---
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # --- Chunking Settings ---
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    # --- Retrieval Settings ---
    DEFAULT_TOP_K: int = 3

    # --- Storage Paths ---
    UPLOAD_DIR: str = "data"
    CHROMA_DB_PATH: str = "chroma_store"
    COLLECTION_NAME: str = "documents"


# Ek hi "settings" object banaya jata hai, poora app isi ko import karega
settings = Settings()

# Zaroori folders agar exist nahi karte toh bana do
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
