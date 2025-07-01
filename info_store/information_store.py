# File: info_store/information_store.py

"""
InformationStore
----------------
A centralized container to collect high-scoring InfoItems, deduplicate by URL,
present them to LLM in a filterable format, and return final retained items.
"""

from typing import List
from info_store.info_item import InfoItem

class InformationStore:
    _items: List[InfoItem] = []

    @classmethod
    def add(cls, item: InfoItem):
        """
        Add a new InfoItem to the store.

        Args:
            item (InfoItem): The item to add.
        """
        cls._items.append(item)

    @classmethod
    def deduplicate(cls):
        """
        Deduplicate InfoItems by URL.
        Keeps the first occurrence of each unique URL.
        """
        seen = set()
        deduped = []
        for item in cls._items:
            if item.url not in seen:
                deduped.append(item)
                seen.add(item.url)
        cls._items = deduped

    @classmethod
    def as_numbered_list(cls) -> str:
        """
        Convert all InfoItems to a numbered string list for LLM prompt filtering.

        Returns:
            str: List of entries like "1. [Title] - [Snippet] (URL)"
        """
        lines = []
        for idx, item in enumerate(cls._items, 1):
            line = f"{idx}. \"{item.title.strip()}\" - \"{item.snippet.strip()}\" ({item.url})"
            lines.append(line)
        return "\n".join(lines)

    @classmethod
    def filter_by_selection(cls, selected_indices: List[int]):
        """
        Keep only items whose index (1-based) appears in selected_indices.

        Args:
            selected_indices (List[int]): List of integer positions to keep.
        """
        cls._items = [item for idx, item in enumerate(cls._items, 1) if idx in selected_indices]

    @classmethod
    def get_all(cls) -> List[InfoItem]:
        """
        Get all currently retained InfoItems.

        Returns:
            List[InfoItem]: All retained items.
        """
        return cls._items

    @classmethod
    def reset(cls):
        """
        Clear all items from the store (used in testing).
        """
        cls._items = []

    @classmethod
    def count(cls) -> int:
        """
        Returns:
            int: Number of items currently in the store.
        """
        return len(cls._items)
