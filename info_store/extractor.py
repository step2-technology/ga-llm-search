# File: info_store/extractor.py

"""
Structured Extractor
--------------------
Uses LLM prompts to extract structured JSON information from raw full_text
based on semantic dimensions and keywords.
"""

import json
from typing import Callable, List
from info_store.info_item import InfoItem

EXTRACTION_PROMPT_TEMPLATE = """
You are a professional information extractor.

Below is a web page text. Your task is to extract relevant structured data based on the following dimension and keywords.

## Dimension:
"{dimension}"

## Related Keywords:
{keywords}

## Text:
{content}

## Instructions:
- Return only a JSON object containing relevant structured information.
- The JSON must be parseable by `json.loads()`.
- If no meaningful data exists, return an empty JSON object: {{}}
- Do NOT include explanation, formatting, or commentary.
""".strip()


def extract_structured_data(item: InfoItem, llm_fn: Callable[[str], str]) -> None:
    """
    Run LLM-based extraction for a single InfoItem.

    Args:
        item (InfoItem): The item to process.
        llm_fn (Callable): The LLM function that accepts a string and returns text.
    """
    if not item.full_text:
        item.structured_data = None
        return

    try:
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            dimension=item.dimension,
            keywords=list(item.keywords.values()),
            content=item.full_text[:6000]  # Limit to 6000 chars
        )
        response = llm_fn(prompt)
        parsed = json.loads(response.strip())

        if isinstance(parsed, dict):
            item.structured_data = parsed
            print(f"[extractor] Successfully extracted structured data from {item.url}")
        else:
            item.structured_data = None
            print(f"[extractor] No meaningful data found for {item.url}")

    except Exception as e:
        print(f"[extractor] Failed to extract for {item.url}: {e}")
        item.structured_data = None


def extract_all(items: List[InfoItem], llm_fn: Callable[[str], str]):
    """
    Run extraction for a list of InfoItems.

    Args:
        items (List[InfoItem]): Items to process.
        llm_fn (Callable): LLM call function.
    """
    total_items = len(items)
    # urls = [item.url for item in items]  # 获取所有 URL

    # 打印要处理的条目数量和 URL 清单
    print(f"[extractor] Total {total_items} items to process.")
    # print("[extractor] URLs to extract from:")
    # for url in urls:
    #     print(f"- {url}")
    
    # 对每个 item 执行抽取操作
    for item in items:
        extract_structured_data(item, llm_fn)
