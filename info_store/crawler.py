# File: info_store/crawler.py

"""
Web Crawler
-----------
Downloads and extracts readable main content from URLs of InfoItems.
Supports HTML and PDF documents.
Stores the content in `item.full_text` for downstream structured parsing.
"""

import requests
from readability import Document
from info_store.info_item import InfoItem
from typing import List
from bs4 import BeautifulSoup
import time
import io
import re
from PyPDF2 import PdfReader


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InfoAgentBot/1.0; +http://yourdomain.com/bot)"
}

# 处理文本换行的正则
REMOVE_NEWLINE_REGEX = re.compile(r"(?<=[^\s,;:、。！？])\n(?=[^\s,;:、。！？])")

def clean_pdf_text(text: str) -> str:
    """
    Cleans the extracted PDF text by removing unnecessary line breaks.
    If the line break happens after a non-sentence-ending character (e.g., comma),
    it merges the lines.
    
    Args:
        text (str): The raw text extracted from the PDF.
    
    Returns:
        str: The cleaned text.
    """
    # 合并不必要的换行（没有句号、逗号等结尾的换行）
    cleaned_text = re.sub(REMOVE_NEWLINE_REGEX, " ", text)
    
    # 进一步清理多余的空白行，确保文本更自然
    cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text)

    return cleaned_text.strip()

def crawl_single(info_item: InfoItem, timeout=15) -> None:
    """
    Download and extract readable content from the InfoItem's URL (HTML or PDF).

    Args:
        info_item (InfoItem): The item whose content to crawl.
        timeout (int): Request timeout in seconds.
    """
    url = info_item.url.strip()
    print(f"\n[crawler] ⏳ Fetching: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        print(f"[crawler] ✅ Status: {response.status_code}")
        content_type = response.headers.get("Content-Type", "").lower()

        # ========== Handle PDF ==========
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            print("[crawler] 📄 Detected PDF content. Extracting text...")
            try:
                with io.BytesIO(response.content) as pdf_file:
                    reader = PdfReader(pdf_file)
                    text = "\n".join(page.extract_text() or "" for page in reader.pages)
                    cleaned_text = clean_pdf_text(text.strip())
                    info_item.full_text = text.strip()
                    snippet = info_item.full_text[:300].replace("\n", " ")
                    print(f"[crawler] 📝 PDF Text Preview: {snippet}...")
            except Exception as pdf_err:
                print(f"[crawler] ❌ Failed to extract PDF: {pdf_err}")
                info_item.full_text = None
            return

        # ========== Handle HTML ==========
        if "text/html" in content_type:
            doc = Document(response.text)
            html_content = doc.summary(html_partial=False)
            clean_text = BeautifulSoup(html_content, "html.parser").get_text(separator="\n")
            info_item.full_text = clean_text.strip()
            snippet = info_item.full_text[:300].replace("\n", " ")
            print(f"[crawler] 📝 HTML Text Preview: {snippet}...")
            return

        # ========== Unknown Type ==========
        print(f"[crawler] ⚠️ Unsupported content type: {content_type}")
        info_item.full_text = None

    except Exception as e:
        print(f"[crawler] ❌ Failed to crawl {url}: {e}")
        info_item.full_text = None


def crawl_all(items: List[InfoItem], delay: float = 1.0):
    """
    Crawl and extract content for all given InfoItems.

    Args:
        items (List[InfoItem]): Items to process.
        delay (float): Delay between requests in seconds.
    """
    for item in items:
        crawl_single(item)
        time.sleep(delay)  # Be polite
