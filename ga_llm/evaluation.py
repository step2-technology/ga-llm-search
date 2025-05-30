# File: ga_llm/evaluation.py
# Author: Jonas Lin, Jacky Cen
# Version: 0.2
# Description: Score-based evaluator combining LLM scoring with optional rules

from .base_gene import BaseGene
from typing import Callable

class Evaluator:
    """Simple LLM-based evaluator with fallback to 0 on error."""

    def __init__(self, prompt_template: str, llm_callback: Callable[[str], str]):
        self.prompt = prompt_template
        self.llm = llm_callback

    def score(self, gene: BaseGene) -> float:
        """Compute numerical score using LLM."""
        input_text = gene.to_text()
        prompt = self.prompt.replace("{{solution_text}}", input_text)

        try:
            response = self.llm(prompt)
            cleaned = response.strip().replace("[", "").replace("]", "")
            return float(cleaned)
        except Exception:
            return 0.0
