# File: info_store/export_logger.py

"""
Export Logger
-------------
Utility to export final InfoItems after GA run to a structured text log
for manual inspection and quality verification.
"""

import os
from datetime import datetime
from info_store.info_item import InfoItem
from typing import List


def ensure_log_dir() -> str:
    """
    Ensure the log directory exists and return its path.
    """
    log_dir = os.path.join("info_store", "log")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def export_info_items(items: List[InfoItem], log_dir: str = None):
    """
    Save the selected InfoItems into a timestamped text file for inspection.

    Args:
        items (List[InfoItem]): Final selected InfoItems.
        log_dir (str): Directory where logs will be stored.
    """
    if log_dir is None:
        log_dir = ensure_log_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(log_dir, f"info_dump_{timestamp}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        for idx, item in enumerate(items, 1):
            f.write(f"## Item {idx}\n")
            f.write(f"Title: {item.title}\n")
            f.write(f"Snippet: {item.snippet}\n")
            f.write(f"URL: {item.url}\n")
            f.write(f"Query: {item.query}\n")
            f.write(f"Dimension: {item.dimension}\n")
            f.write(f"Keywords: {item.keywords}\n")
            f.write(f"Score: {item.score}\n\n")

            f.write(f"[Full Text]\n{item.full_text or '(None)'}\n\n")
            f.write(f"[Structured Data]\n{item.structured_data or '{}'}\n")
            f.write("\n" + "=" * 80 + "\n\n")

    print(f"[export_logger] Exported {len(items)} items to {file_path}")
