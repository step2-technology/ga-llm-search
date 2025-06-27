# File: search_query/search_api_test.py

from search_query.search_api import search
import json

def test_query(query: str):
    print(f"\n🧪 Testing query: {query}\n")
    results = search(query, max_results=5)

    print(f"✅ Number of results: {len(results)}")
    for idx, item in enumerate(results, 1):
        print(f"\n--- Result #{idx} ---")
        print("Title   :", item.get("title", ""))
        print("Snippet :", item.get("snippet", ""))
        print("Link    :", item.get("link", ""))

    print("\n📦 Full structured results:")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_query('"高胆固醇"^2.0 "科研资金"^1.5 Cardiovascular disease epidemiology trends')


