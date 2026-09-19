"""
services/llm_service.py
========================
Groq LLM se baat karne ka kaam - context + question + chat history leke,
final answer generate karna.
"""

from groq import Groq
from app.core.config import settings
from app.core.prompts import RAG_SYSTEM_PROMPT, build_user_prompt, GENERAL_CHAT_SYSTEM_PROMPT
import json
from app.core.tools import TOOLS, dispatch_tool_call
import re

_client = None  # lazy singleton
MAX_TOOL_ITERATIONS = 4
_DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')

def get_groq_client() -> Groq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY set nahi hai! .env file mein GROQ_API_KEY=your_key daalo."
            )
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client

def detect_script(text: str) -> str:
    """User ne Devanagari (हिन्दी) ya Latin/Roman script use ki - detect karta hai."""
    return "devanagari" if _DEVANAGARI_PATTERN.search(text) else "latin"


def build_script_instruction(user_text: str) -> str:
    """Har turn pe dynamically inject hone wala reminder - static system-prompt
    ke bharose nahi rehte, kyunki lambi chat me uska effect kamzor pad jaata hai."""
    if detect_script(user_text) == "devanagari":
        return "[SCRIPT: user wrote in Devanagari Hindi. Reply in Devanagari Hindi script.]"
    return (
        "[SCRIPT: user wrote in Latin/Roman script (Hinglish or English). "
        "Reply ONLY in Latin/Roman script. Do NOT use Devanagari (हिन्दी) "
        "characters anywhere — even Hindi words must be spelled phonetically "
        "in Roman letters (e.g. 'aapka', 'kaise', 'karo'), never in हिन्दी script.]"
    )


def generate_answer(question: str, context_chunks: list[dict], chat_history: list[dict] = None) -> str:
    chat_history = chat_history or []

    user_prompt = build_user_prompt(question, context_chunks)
    script_note = build_script_instruction(question)   # NEW

    messages = [{"role": "system", "content": RAG_SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "system", "content": script_note})   # NEW — recency ke liye system role, user se just pehle
    messages.append({"role": "user", "content": user_prompt})

    client = get_groq_client()
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content

def generate_general_answer(question: str, chat_history: list[dict] = None) -> str:
    chat_history = chat_history or []
    script_note = build_script_instruction(question)

    messages = [{"role": "system", "content": GENERAL_CHAT_SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "system", "content": script_note})   # NEW
    messages.append({"role": "user", "content": question})

    client = get_groq_client()

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message

        if not message.tool_calls:
            # LLM ne seedha final answer de diya, tool ki zarurat nahi padi
            return message.content

        # LLM ne tool maanga -> uska message conversation me add karo
        # (sirf Groq API ko expected fields bhejo, poora SDK object dump nahi)
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ],
        })

        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = dispatch_tool_call(tool_call.function.name, args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
        # loop continue: LLM ko phir call karenge, ab uske paas tool-result bhi hai

    return "Maaf karna, is sawaal ka jawaab dhoondhne mein dikkat aa rahi hai. Dobara try karo."