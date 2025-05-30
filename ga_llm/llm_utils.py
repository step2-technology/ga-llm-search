# File: ga_llm/llm_utils.py
import requests
import json
import time

def default_llm_call(prompt: str, retries: int = 2) -> str:
    headers = {
        'Authorization': 'Bearer sk-your-real-key-here',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': 'qwen-max-latest',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.7,
    }

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.Timeout as e:
            print(f"[WARN] LLM request timed out (attempt {attempt + 1})")
        except Exception as e:
            print(f"[ERROR] LLM request failed: {e}")
        
        time.sleep(2)  # 短暂等待再试

    # 最终失败时返回一个空字符串或固定格式（避免 json.loads 崩溃）
    return '{"days": [], "hotels": {}, "total_cost": 0}'
