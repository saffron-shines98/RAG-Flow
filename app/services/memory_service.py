"""
services/memory_service.py
============================
Ye "conversation memory" handle karta hai - taaki user follow-up sawaal
poochein toh model ko PICHLI BAATCHEET ka context pata rahe.

Concept: Har conversation ka ek UNIQUE session_id hota hai. Hum har
session_id ke against, uski poori chat history (list of Q&A) store karte hain.
Saath hi, har session ke saath kaunsi PDFs "attached" hain, wo bhi track karte hain.

IMPORTANT LIMITATION:
Ye memory abhi RAM mein hai (Python dictionaries) - server restart hote hi
(jaise --reload trigger hone pe) ye khatam ho jayegi. Production mein Redis/DB use karte hain.
"""

from typing import List, Dict

# session_id -> list of {"role": "user"/"assistant", "content": "..."}
_conversation_store: Dict[str, List[Dict[str, str]]] = {}

# session_id -> list of PDF filenames jo is session (chat) se "attached" hain
_session_documents: Dict[str, List[str]] = {}

MAX_HISTORY_TURNS = 5  # kitne pichle Q&A pairs yaad rakhne hain


def get_history(session_id: str) -> List[Dict[str, str]]:
    """Kisi session ki abhi tak ki poori history laata hai."""
    return _conversation_store.get(session_id, [])


def add_turn(session_id: str, question: str, answer: str) -> None:
    """Ek naya Q&A pair, session ki history mein add karta hai."""
    if session_id not in _conversation_store:
        _conversation_store[session_id] = []

    _conversation_store[session_id].append({"role": "user", "content": question})
    _conversation_store[session_id].append({"role": "assistant", "content": answer})

    max_messages = MAX_HISTORY_TURNS * 2
    if len(_conversation_store[session_id]) > max_messages:
        _conversation_store[session_id] = _conversation_store[session_id][-max_messages:]


def add_document_to_session(session_id: str, filename: str) -> None:
    """Is session (chat) ke saath ek PDF ko 'attach' karta hai."""
    if session_id not in _session_documents:
        _session_documents[session_id] = []
    if filename not in _session_documents[session_id]:
        _session_documents[session_id].append(filename)


def get_session_documents(session_id: str) -> List[str]:
    """Is session ke saath abhi tak kaunsi PDFs attached hain."""
    return _session_documents.get(session_id, [])


def clear_history(session_id: str) -> None:
    """Kisi session ki history clear kar deta hai."""
    _conversation_store.pop(session_id, None)


def clear_session(session_id: str) -> None:
    """Poora session clear karta hai - history AUR attached documents dono."""
    _conversation_store.pop(session_id, None)
    _session_documents.pop(session_id, None)