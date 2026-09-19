"""
core/tools.py
=================
Available tools ki schema (Groq/OpenAI tool-calling format) + unhe
actually execute karne wala dispatcher.

Naya tool add karna ho -> sirf yahan schema + dispatch mapping add karo,
llm_service.py touch nahi karna padega.
"""

from app.services.web_search_service import web_search

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the live web for CURRENT/real-time information — "
                "today's date, latest news, current prices, recent events, "
                "or anything that could have changed after the model's "
                "training cutoff. Do NOT use this for general knowledge "
                "the model can already answer confidently."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A short, specific search query (3-8 words).",
                    }
                },
                "required": ["query"],
            },
        },
    }
]


def dispatch_tool_call(tool_name: str, arguments: dict) -> str:
    """Tool name ke hisaab se actual function call karta hai, result STRING
    format me return karta hai (LLM ko isi format me wapas dena hota hai)."""
    if tool_name == "web_search":
        results = web_search(arguments.get("query", ""))
        return _format_search_results(results)
    return f"Unknown tool: {tool_name}"


def _format_search_results(results: list[dict]) -> str:
    """Results ko clearly-delimited tags me wrap karta hai — taaki model
    ise sirf DATA samjhe, kabhi instruction na maane (prompt-injection defense)."""
    if not results:
        return "<search_results>No results found.</search_results>"

    blocks = [
        f'<search_result source="{r["url"]}" title="{r["title"]}">\n{r["content"]}\n</search_result>'
        for r in results
    ]
    return "<search_results>\n" + "\n\n".join(blocks) + "\n</search_results>"