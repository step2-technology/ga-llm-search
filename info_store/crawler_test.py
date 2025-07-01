# File: crawler_test.py (enhanced)

import sys
from info_store.info_item import InfoItem
from info_store.crawler import crawl_single

def main():
    if len(sys.argv) != 2:
        print("Usage: python crawler_test.py <URL>")
        return

    url = sys.argv[1]
    print(f"\n[TEST] Crawling: {url}\n")

    dummy_item = InfoItem(
        title="Test",
        snippet="Test",
        url=url,
        query="Test",
        user_query="Test",
        dimension="Test",
        keywords={},
        score=10.0
    )

    crawl_single(dummy_item)

    print("\n====================== CRAWLED RESULT ======================\n")
    if dummy_item.full_text:
        print(dummy_item.full_text[:5000])
    else:
        print("(Nothing was extracted from the URL)")
        print(f"full_text = {dummy_item.full_text}")

if __name__ == "__main__":
    main()
