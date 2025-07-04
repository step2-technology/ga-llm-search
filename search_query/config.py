# File: search_query/config.py
# Description: Centralized configuration for GA-LLM search task


# === Google Search API ===
google_search_domain = 'https://cn2us02.opapi.win'
google_search_api_key = 'sk-mEFyLY3vMhbrVERtVkgWlrCDuA5jUslFxKbTIi80mUBdDhEY'
search_max_results = 5


# === Evolution Strategy ===
evolution_config = {
    "population_size": 5,
    "max_generations": 5,
    "elite_ratio": 0.3,
    "mutation_rate": 0.3,
    "early_stopping_rounds": 5,
    "use_llm_for_crossover": False
}


# === LLM Parameters ===
llm_model = "qwen-max"
llm_temperature = 0.3
llm_timeout = 120


# === Initial Dimensions and Keywords ===
default_dimensions = [
    "Trade Policy",
    "Export Data",
    "Industry Impact"
]

default_keywords = {
    "Trade Policy": ["tariff reform", "import duty policy", "bilateral agreement"],
    "Export Data": ["export volume", "trade balance statistics", "export index"],
    "Industry Impact": ["manufacturing slowdown", "supply chain impact", "technology sector decline"]
}
