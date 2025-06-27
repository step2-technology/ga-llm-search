# File: search_query/search_api.py
# Description: Unified Google search wrapper with GA-compatible output

import json
import logging
import requests
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Any

from search_query import search_logger
from search_query.config import google_search_domain, google_search_api_key

# ============================
# Search data logger (for raw search content)
# ============================

search_data_logger = logging.getLogger("search_data_logger")
search_data_logger.setLevel(logging.DEBUG)

_log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(_log_dir, exist_ok=True)

_data_log_file = os.path.join(_log_dir, f"search_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
fh = logging.FileHandler(_data_log_file, encoding="utf-8")
fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
search_data_logger.addHandler(fh)

# ============================
# GoogleSearchAPI 封装类
# ============================

class GoogleSearchAPI:
    def __init__(self):
        self.domain = google_search_domain
        self.api_key = google_search_api_key
        self.search_url = f"{self.domain}/api/v1/openapi/search/serper/v1"

    def search(self, keyword: str, count: int = 10, page: int = 1) -> List[Dict[str, Any]]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'q': keyword,
            'page': page,
            'num': count
        }

        try:
            response = requests.post(self.search_url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                logging.error(f'谷歌搜索 API 调用失败: {response.status_code} - {response.text}')
                return []

            result_data = response.json()
            return self._parse_search_results(result_data, count)

        except requests.exceptions.RequestException as e:
            logging.error(f'谷歌搜索 API 请求异常: {str(e)}')
        except json.JSONDecodeError as e:
            logging.error(f'谷歌搜索 API 响应解析失败: {str(e)}')
        except Exception as e:
            logging.error(f'谷歌搜索 API 未知错误: {str(e)}')

        return []

    def _parse_search_results(self, data: Dict[str, Any], max_count: int) -> List[Dict[str, Any]]:
        results = []

        answer_box = data.get('answerBox')
        if answer_box and len(results) < max_count:
            results.append({
                'url': answer_box.get('link', ''),
                'title': answer_box.get('title', ''),
                'content': answer_box.get('snippet', '')
            })

        organic_results = data.get('organic', [])
        for item in organic_results:
            if len(results) >= max_count:
                break
            results.append({
                'url': item.get('link', ''),
                'title': item.get('title', ''),
                'content': item.get('snippet', '')
            })

        people_also_ask = data.get('peopleAlsoAsk', [])
        for item in people_also_ask:
            if len(results) >= max_count:
                break
            results.append({
                'url': item.get('link', ''),
                'title': item.get('title', ''),
                'content': item.get('snippet', '')
            })

        return results[:max_count]

# ============================
# 对 GA 引擎暴露的统一接口
# ============================

_google_search_api = GoogleSearchAPI()
_SEARCH_CACHE = {}

def search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    cache_key = _hash(query)
    if cache_key in _SEARCH_CACHE:
        search_logger.debug(f"[search] Cache hit for query: {query}")
        search_data_logger.info(f"[CACHE HIT] {query}")
        return _SEARCH_CACHE[cache_key]

    search_logger.info(f"[search] Executing real search: {query}")
    search_data_logger.info(f"[QUERY] {query}")

    try:
        raw_results = _google_search_api.search(query, count=max_results)
        search_data_logger.info(f"[RAW_RESULTS]\n{json.dumps(raw_results, ensure_ascii=False, indent=2)}")

        results = []
        for item in raw_results:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "link": item.get("url", "")
            })

        search_data_logger.info(f"[STRUCTURED_RESULTS]\n{json.dumps(results, ensure_ascii=False, indent=2)}")
        _SEARCH_CACHE[cache_key] = results
        return results

    except Exception as e:
        search_logger.error(f"[search] Real search failed: {e}")
        search_data_logger.error(f"[search] Search execution failed: {e}")
        return []

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
