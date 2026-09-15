from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import ingest, ask, documents, chat

app = FastAPI(
    title="TrackFlow RAG API",
    description="PDF/DOCX/TXT/Image upload karo, sawaal poocho - RAG + General Chat dono support ke saath.",
    version="3.0.0",
)

# Router registration - har feature ka apna router file
app.include_router(ingest.router)
app.include_router(ask.router)
app.include_router(documents.router)
app.include_router(chat.router)

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "TrackFlow RAG API chal raha hai! /ui/ pe UI dekho ya /docs pe API test karo."}