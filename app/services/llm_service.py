"""
services/llm_service.py
========================
Groq LLM se baat karne ka kaam - context + question + chat history leke,
final answer generate karna.
"""

from groq import Groq
from app.core.config import settings
from app.core.prompts import RAG_SYSTEM_PROMPT, build_user_prompt, GENERAL_CHAT_SYSTEM_PROMPT

_client = None  # lazy singleton


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY set nahi hai! .env file mein GROQ_API_KEY=your_key daalo."
            )
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def generate_answer(question: str, context_chunks: list[dict], chat_history: list[dict] = None) -> str:
    chat_history = chat_history or []

    user_prompt = build_user_prompt(question, context_chunks)

    messages = [{"role": "system", "content": RAG_SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_prompt})

    client = get_groq_client()
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content

def generate_general_answer(question: str, chat_history: list[dict] = None) -> str:
    """
    General conversation ke liye - koi document context NAHI, seedha LLM se
    baat (jaise ChatGPT). Sirf chat_history use hoti hai continuity ke liye.
    """
    chat_history = chat_history or []

    messages = [{"role": "system", "content": GENERAL_CHAT_SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": question})

    client = get_groq_client()
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.7,  # HIGH - general chat mein natural variety acchi lagti hai
    )
    return response.choices[0].message.content