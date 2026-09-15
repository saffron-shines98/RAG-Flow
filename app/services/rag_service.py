import os
import uuid
from app.core.config import settings
from app.services import document_loader_service
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_texts
from app.services.vector_store_service import store_chunks, search_similar_chunks, list_all_sources
from app.services.llm_service import generate_answer, generate_general_answer
from app.services import memory_service


def ingest_document(file_path: str, session_id: str = None) -> dict:
    """
    Koi bhi supported file (PDF/DOCX/TXT/Image) -> text -> chunks -> embeddings -> ChromaDB store
    Fir is document ko session_id ke saath "attach" kar deta hai.

    Agar session_id nahi diya gaya, ek NAYA unique session_id khud generate hota hai.

    Returns: {"chunks_created": int, "session_id": str}
    """
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    source_filename = os.path.basename(file_path)

    # DISPATCHER decide karta hai kaunsa loader use karna hai (extension ke hisaab se)
    raw_text = document_loader_service.extract_text(file_path)

    chunks = chunk_text(raw_text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    embeddings = embed_texts(chunks)
    store_chunks(chunks, embeddings, source_filename)

    memory_service.add_document_to_session(session_id, source_filename)

    return {"chunks_created": len(chunks), "session_id": session_id}


def ask_question(question: str, top_k: int = None, session_id: str = "default", source_filter=None) -> dict:
    """
    Question -> embed -> retrieve similar chunks -> chat history ke saath LLM ko diya -> answer

    IMPORTANT: Agar 'source_filter' khud nahi diya (None), toh system AUTOMATICALLY
    us session ke saath jo bhi PDFs attach hain, unhi mein search karega.
    Yehi wo mechanism hai jo decide karta hai "kaunsi PDF ki baat ho rahi hai".
    """
    top_k = top_k or settings.DEFAULT_TOP_K

    # 1. Pichli conversation history nikalo
    chat_history = memory_service.get_history(session_id)

    # 2. Agar user ne manually source_filter nahi diya, session ke apne documents use karo
    if source_filter is None:
        session_docs = memory_service.get_session_documents(session_id)
        source_filter = session_docs if session_docs else None

    # 3. RETRIEVAL
    question_embedding = embed_texts([question])[0]
    relevant_chunks = search_similar_chunks(question_embedding, top_k, source_filter)

    # 4. GENERATION
    answer = generate_answer(question, relevant_chunks, chat_history)

    # 5. Memory update
    memory_service.add_turn(session_id, question, answer)

    return {
        "question": question,
        "answer": answer,
        "sources_used": [c["source"] for c in relevant_chunks],
        "session_id": session_id,
    }


def get_available_documents() -> list[str]:
    return list_all_sources()


def reset_conversation(session_id: str) -> None:
    """Session ki history AUR attached documents, dono clear karta hai."""
    memory_service.clear_session(session_id)


def general_chat(question: str, session_id: str = "default") -> dict:
    """
    Document-free general conversation - jaise normal ChatGPT/Claude chat.
    Same memory_service use hoti hai, isliye ek hi session mein user
    kabhi document ke baare mein poochh sakta hai, kabhi general baat.
    """
    chat_history = memory_service.get_history(session_id)
    answer = generate_general_answer(question, chat_history)
    memory_service.add_turn(session_id, question, answer)

    return {
        "question": question,
        "answer": answer,
        "session_id": session_id,
    }

def get_session_documents(session_id: str) -> list[str]:
    """Kisi specific session/chat ke saath abhi tak kaunsi files attached hain."""
    return memory_service.get_session_documents(session_id)