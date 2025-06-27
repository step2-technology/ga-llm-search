# File: ga_llm/llm_utils.py
# Description: LLM invocation utilities for GA-LLM framework

import requests
import json
import time


def llm_call(
    prompt: str,
    model: str = "qwen-max-latest",
    temperature: float = 0.7,
    timeout: int = 120,
    retries: int = 2,
    api_key: str = "sk-bd5e56115da24830b26fe4fdb637d7f4",
    api_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
) -> str:
    """
    General-purpose LLM call function with configurable parameters.

    Args:
        prompt (str): User prompt
        model (str): LLM model name
        temperature (float): Sampling temperature
        timeout (int): Timeout per request (seconds)
        retries (int): Retry count on failure
        api_key (str): LLM API key
        api_url (str): API endpoint URL

    Returns:
        str: LLM-generated content or fallback safe string
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': temperature,
    }

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.Timeout:
            print(f"[WARN] LLM request timed out (attempt {attempt + 1}/{retries})")
        except Exception as e:
            print(f"[ERROR] LLM request failed (attempt {attempt + 1}/{retries}): {e}")
        
        time.sleep(2)  # wait before retry

    # Fallback: ensure downstream JSON parsing won't crash
    return '{"error": "LLM call failed after retries."}'


def default_llm_call(prompt: str, retries: int = 2) -> str:
    """
    Default LLM call using fixed model and API setup.
    Used when no customization is needed.
    """
    return llm_call(
        prompt=prompt,
        model="qwen-max-latest",
        temperature=0.7,
        timeout=120,
        retries=retries,
        api_key="sk-your-real-key-here",  # override from config externally if needed
        api_url="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    )
