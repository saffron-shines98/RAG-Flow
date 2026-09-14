"""
main.py
=======
App ka ENTRY POINT. Ye sirf:
1. FastAPI app banata hai
2. Saare routers ko "register/include" karta hai

Koi bhi business logic yahan NAHI hai - wo services/ mein hai.
Ye file jitni "chhoti aur saaf" ho, utna acha (industry best-practice).
"""

from fastapi import FastAPI

from app.routers import ingest, ask

app = FastAPI(
    title="TrackFlow RAG API",
    description="PDF upload karo, sawaal poocho - Hugging Face + ChromaDB + Groq se powered RAG system.",
    version="1.0.0",
)

# Router registration - har feature ka apna router file
app.include_router(ingest.router)
app.include_router(ask.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "TrackFlow RAG API chal raha hai! /docs pe jaake test karo."}
