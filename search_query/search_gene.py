# File: search_query/search_gene.py

import json
import random
import copy
from typing import Dict, List, Optional
from ga_llm.base_gene import BaseGene
from search_query.search_api import search
from search_query import search_logger


class SearchQueryGene(BaseGene):
    def __init__(self, llm_engine=None):
        super().__init__(llm_engine)
        self.user_query: str = ""
        self.dimensions: List[str] = []
        self.keywords: Dict[str, str] = {}
        self.search_results: Optional[List[Dict]] = None
        self.query_string: Optional[str] = None

    def parse_from_text(self, text: str) -> None:
        """Parses LLM output JSON and constructs a complete gene including search."""
        try:
            data = json.loads(text)
            self.user_query = data["user_query"]
            self.dimensions = data["dimensions"]
            raw_keywords = data["keywords"]
            self.keywords = {}

            for dim in self.dimensions:
                candidates = raw_keywords[dim]
                if isinstance(candidates, list) and candidates:
                    self.keywords[dim] = random.choice(candidates)
                elif isinstance(candidates, str):
                    self.keywords[dim] = candidates
                else:
                    raise ValueError(f"Invalid keyword format for dimension '{dim}'")

            self.rebuild_from_keywords()

        except Exception as e:
            search_logger.error(f"[parse_from_text] Failed to parse gene or search: {e}")
            raise ValueError(f"Invalid gene format or search failed: {e}")

    def rebuild_from_keywords(self):
        """Constructs a weighted search query from keywords and performs Google search."""
        try:
            keyword_list = list(self.keywords.values())
            random.shuffle(keyword_list)
            keyword_list = keyword_list[:3]  # Use up to 3 keywords

            query_parts = []
            if len(keyword_list) >= 1:
                query_parts.append(f'"{keyword_list[0]}"^2.0')
            if len(keyword_list) >= 2:
                query_parts.append(f'"{keyword_list[1]}"^1.5')
            if len(keyword_list) >= 3:
                query_parts.append(f'{keyword_list[2]}')

            self.query_string = ' '.join(query_parts)
            self.search_results = search(self.query_string, max_results=5)

            search_logger.debug(f"[rebuild] Query: {self.query_string}")
            search_logger.debug(f"[rebuild] Search Results: {len(self.search_results)} found.")
        except Exception as e:
            search_logger.error(f"[rebuild_from_keywords] Search failed: {e}")
            self.search_results = []

    def to_text(self) -> str:
        """Convert gene contents into evaluation prompt."""
        if not self.search_results:
            return f"## User Query:\n{self.user_query}\n\n## Search Query:\n{self.query_string}\n\n## Search Results: null\n"

        entries = []
        for res in self.search_results:
            entries.append(f'Title: "{res.get("title", "")}"\nSnippet: "{res.get("snippet", "")}"')
        results_str = "\n\n".join(entries)

        return (
            f"## User Query:\n{self.user_query}\n\n"
            f"## Search Query:\n{self.query_string}\n\n"
            f"## Search Results:\n{results_str}"
        )

    def crossover(self, other: 'SearchQueryGene') -> 'SearchQueryGene':
        """Create child by randomly combining keyword choices from parents."""
        child = SearchQueryGene(llm_engine=self.llm_engine)
        child.user_query = self.user_query
        child.dimensions = copy.deepcopy(self.dimensions)
        child.keywords = {}

        for dim in self.dimensions:
            if dim in self.keywords and dim in other.keywords:
                child.keywords[dim] = random.choice([self.keywords[dim], other.keywords[dim]])
            elif dim in self.keywords:
                child.keywords[dim] = self.keywords[dim]
            elif dim in other.keywords:
                child.keywords[dim] = other.keywords[dim]

        child.rebuild_from_keywords()
        return child

    def mutate(self) -> 'SearchQueryGene':
        """Mutate by changing one keyword via LLM, then refresh search."""
        mutated = copy.deepcopy(self)
        if not mutated.dimensions:
            return mutated

        mutate_dim = random.choice(mutated.dimensions)
        current_keyword = mutated.keywords.get(mutate_dim, "")
        prompt = self._mutation_prompt(mutate_dim, current_keyword)

        try:
            response = self.llm_engine(prompt)
            result = json.loads(response)
            new_keyword = result.get("new_keyword", current_keyword)
            mutated.keywords[mutate_dim] = new_keyword
            search_logger.debug(f"[mutate] Mutated '{mutate_dim}': '{current_keyword}' -> '{new_keyword}'")
        except Exception as e:
            search_logger.error(f"[mutate] Mutation failed: {e}")

        mutated.rebuild_from_keywords()
        return mutated

    def _mutation_prompt(self, dimension: str, current_keyword: str) -> str:
        return f"""
        You are an Expert Information Retrieval Strategist.

        Your task is to optimize search performance by improving keyword selection within a specific semantic dimension.

        ## Target Dimension:
        "{dimension}"

        ## Current Keyword:
        "{current_keyword}"

        ## Goal:
        Suggest an improved keyword or phrase that:
        - Is semantically aligned with the target dimension
        - Has a higher likelihood of returning authoritative and comprehensive content
        - Is suitable for use in advanced internet search queries

        ## Output Requirements:
        Respond with a strict JSON object in the following format:
        {{
        "new_keyword": "..."
        }}

        ## Constraints:
        - Use only ASCII characters
        - Do NOT include any explanation, markdown, or commentary
        - Ensure the JSON can be parsed directly by Python's json.loads()
        """.strip()
