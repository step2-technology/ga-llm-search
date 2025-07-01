# File: search_query/evaluator_with_info_store.py

"""
Evaluator with Information Store
--------------------------------
Custom Evaluator that not only scores a gene using an LLM, but also stores high-quality genes
into the information candidate store for later filtering and packaging.
"""

from typing import Callable
from search_query.search_gene import SearchQueryGene
from info_store.information_store import InformationStore  # will be implemented later
from search_query.prompts import SearchQueryPrompts

# Default score threshold to enter the info store
DEFAULT_SCORE_THRESHOLD = 7.0

class EvaluatorWithInfoStore:
    def __init__(
        self,
        llm_fn: Callable[[str], str],
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
        prompt_name: str = "search_result_evaluation"
    ):
        """
        Initialize the evaluator.

        Args:
            llm_fn (Callable): Function to call the LLM with a prompt.
            score_threshold (float): Score cutoff to store item into InformationStore.
            prompt_name (str): Name of the prompt to use from SearchQueryPrompts.
        """
        self.llm_fn = llm_fn
        self.score_threshold = score_threshold
        self.eval_prompt_template = SearchQueryPrompts.get(prompt_name)

    def score(self, gene: SearchQueryGene) -> float:
        """
        Score a search gene using the LLM, and store it if it's high-quality.

        Args:
            gene (SearchQueryGene): The gene to evaluate.

        Returns:
            float: Score between 0 and 10.
        """
        try:
            prompt = self.eval_prompt_template.replace("{{solution_text}}", gene.to_text())
            raw_score = self.llm_fn(prompt)

            score = float(raw_score.strip())

            if score >= self.score_threshold:
                # Convert to InfoItem and add to store
                from info_store.info_item import InfoItem  # import here to avoid circular import
                items = gene.to_info_items(score=score)
                for item in items:
                    InformationStore.add(item)

            return score

        except Exception as e:
            print(f"[EvaluatorWithInfoStore] Evaluation failed: {e}")
            return 0.0
