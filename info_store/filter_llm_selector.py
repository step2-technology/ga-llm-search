# File: info_store/filter_llm_selector.py

"""
FilterLLMSelector
-----------------
Uses an LLM to select which InfoItems from a candidate list should be retained,
based on their relevance to the user's query and the overall search objective.
"""

import json
import re
from typing import List, Callable

from info_store.information_store import InformationStore


FILTER_PROMPT_TEMPLATE = """
You are an expert information analyst.

Below is a numbered list of search result entries, each including a title, snippet, and URL.
Your task is to select the entries that are clearly relevant and valuable in response to the user query below.
Once you have selected the relevant entries, reorder them by their relevance to the user query (from most relevant to least relevant).

## User Query:
{user_query}

## Search Results:
{numbered_list}

## Instructions:
- Return ONLY the numbers of the entries that should be kept, in a **sorted order** by relevance (1 being the most relevant).
- **Limit the number of selected results to {num_results}**.
- Format: a JSON array of integers, like: [1, 3, 4]
- Do NOT include explanations or comments.
- The list must be valid JSON parsable by `json.loads()`.

Respond with the JSON list ONLY.
""".strip()


def filter_info_items_via_llm(user_query: str, llm_fn: Callable[[str], str], num_results: int = 5) -> List[int]:
    """
    Use LLM to filter current InfoItems in InformationStore and return kept indices.

    Args:
        user_query (str): The original user query to evaluate against.
        llm_fn (Callable): Function to call LLM with a string prompt.
        num_results (int): Number of results to return after filtering. Default is 5.

    Returns:
        List[int]: List of selected InfoItem indices (1-based).
    """
    # Build numbered list from InfoItems
    numbered = InformationStore.as_numbered_list()

    if not numbered.strip():
        return []

    prompt = FILTER_PROMPT_TEMPLATE.format(
        user_query=user_query.strip(),
        numbered_list=numbered,
        num_results=num_results
    )

    try:
        raw_response = llm_fn(prompt)
        response_str = raw_response.strip()

        # Try strict parsing first
        selected = json.loads(response_str)

        if isinstance(selected, list) and all(isinstance(x, int) for x in selected):
            return selected[:num_results]  # Ensure only the top 'num_results' are returned

    except Exception:
        pass

    # Try extracting with regex fallback
    try:
        match = re.search(r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]", response_str)
        if match:
            nums = [int(x.strip()) for x in match.group(1).split(",")]
            return nums[:num_results]  # Ensure only the top 'num_results' are returned
    except Exception:
        pass

    print("[WARNING] Failed to parse LLM response for filtering. Returning full list as fallback.")
    return list(range(1, InformationStore.count() + 1))[:num_results]  # Fallback to returning only 'num_results' items
