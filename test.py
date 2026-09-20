from app.services.web_search_service import web_search

print("jkj")
results = web_search("latest AI news 2024", max_results=2)
print(results, "iui")
for r in results:
    print(f"Title: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"Content: {r['content'][:100]}...")
    print("---")