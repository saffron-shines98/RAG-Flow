"""
services/web_search_service.py
===================================
Tavily API se live web search - LLM-agents ke liye purpose-built,
raw HTML nahi, clean summarized content deta hai.
"""

from tavily import TavilyClient
from app.core.config import settings

_client = None  # lazy singleton — llm_service.py ke pattern jaisa hi


def get_tavily_client() -> TavilyClient:
    global _client
    if _client is None:
        if not settings.TAVILY_API_KEY:
            raise ValueError(
                "TAVILY_API_KEY set nahi hai! .env file mein TAVILY_API_KEY=your_key daalo."
            )
        _client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    return _client


def web_search(query: str, max_results: int = 4) -> list[dict]:
    """Query leke top N results deta hai: [{title, url, content}]"""
    if not query.strip():
        return []

    client = get_tavily_client()
    try:
        response = client.search(query=query, max_results=max_results, search_depth="basic")
    except Exception as e:
        # FAILURE HANDLING: search fail ho jaaye to crash nahi, LLM ko pata chal jaaye
        return [{"title": "Search unavailable", "url": "", "content": f"Search failed: {e}"}]

    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
        for r in response.get("results", [])
    ]