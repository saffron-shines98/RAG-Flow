"""
services/memory_service.py
============================
Ye "conversation memory" handle karta hai - taaki user follow-up sawaal poochein
toh model ko PICHLI BAATCHEET ka context pata rahe.

Concept: Har conversation ka ek UNIQUE session_id hota hai. Hum har session_id
ke against, uski poori chat history (list of Q&A) Upstash Redis mein store
karte hain. Saath hi, har session ke saath kaunsi files "attached" hain,
wo bhi track karte hain.

Ab ye memory Redis (Upstash) mein persist hoti hai - server restart, redeploy,
ya multiple server instances ke beech bhi data safe rehta hai. Isse pehle
ye RAM (Python dict) mein thi, jo restart pe khatam ho jaati thi.
"""

import json
from typing import List, Dict

from upstash_redis import Redis
from app.core.config import settings

MAX_HISTORY_TURNS = 5  # kitne pichle Q&A pairs yaad rakhne hain
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 din baad session auto-expire (cleanup)

_redis_client = None  # lazy singleton


def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        if not settings.UPSTASH_REDIS_URL or not settings.UPSTASH_REDIS_TOKEN:
            raise ValueError(
                "UPSTASH_REDIS_URL / UPSTASH_REDIS_TOKEN set nahi hai! "
                ".env file mein daalo."
            )
        _redis_client = Redis(
            url=settings.UPSTASH_REDIS_URL,
            token=settings.UPSTASH_REDIS_TOKEN,
        )
    return _redis_client


def _history_key(session_id: str) -> str:
    return f"session:{session_id}:history"


def _documents_key(session_id: str) -> str:
    return f"session:{session_id}:documents"


def get_history(session_id: str) -> List[Dict[str, str]]:
    """Kisi session ki abhi tak ki poori history laata hai."""
    client = get_redis_client()
    raw = client.get(_history_key(session_id))
    if not raw:
        return []
    return json.loads(raw)


def add_turn(session_id: str, question: str, answer: str) -> None:
    """Ek naya Q&A pair, session ki history mein add karta hai."""
    client = get_redis_client()
    key = _history_key(session_id)

    history = get_history(session_id)
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})

    max_messages = MAX_HISTORY_TURNS * 2
    if len(history) > max_messages:
        history = history[-max_messages:]

    client.set(key, json.dumps(history), ex=SESSION_TTL_SECONDS)


def add_document_to_session(session_id: str, filename: str) -> None:
    """Is session (chat) ke saath ek file ko 'attach' karta hai."""
    client = get_redis_client()
    key = _documents_key(session_id)

    raw = client.get(key)
    docs = json.loads(raw) if raw else []

    if filename not in docs:
        docs.append(filename)

    client.set(key, json.dumps(docs), ex=SESSION_TTL_SECONDS)


def get_session_documents(session_id: str) -> List[str]:
    """Is session ke saath abhi tak kaunsi files attached hain."""
    client = get_redis_client()
    raw = client.get(_documents_key(session_id))
    return json.loads(raw) if raw else []


def clear_history(session_id: str) -> None:
    """Kisi session ki history clear kar deta hai."""
    client = get_redis_client()
    client.delete(_history_key(session_id))


def clear_session(session_id: str) -> None:
    """Poora session clear karta hai - history AUR attached documents dono."""
    client = get_redis_client()
    client.delete(_history_key(session_id))
    client.delete(_documents_key(session_id))