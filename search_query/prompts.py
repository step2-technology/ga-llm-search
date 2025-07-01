# File: search_query/prompts.py
# Description: Prompt templates for keyword generation, mutation, and evaluation in search query optimization

class SearchQueryPrompts:
    """
    Contains all task-specific prompt templates used for LLM interactions in the search query optimization task.
    """

    templates = {
        "dimension_to_keywords": """
        You are a Semantic Search Keyword Engineer.

        Your task is to generate relevant search keywords for a given semantic dimension.

        ## Target Dimension:
        "{dimension}"

        ## Requirements:
        - Provide 3 to 5 concise and domain-relevant keywords or phrases.
        - Use vocabulary that is common in expert-level publications or authoritative news sources.
        - Each keyword should be suitable for use in modern web search engines.

        ## Output Format:
        Return ONLY a JSON array of strings. For example:
        [
        "tariff reform",
        "import-export policy",
        "US-China trade war"
        ]

        ## Constraints:
        - Do NOT include any explanation or markdown
        - Do NOT use bullets or numbered lists
        - Use only plain JSON arrays compatible with Python's json.loads()
        """,

        "initial_gene_generation": """
        You are a Search Strategy Constructor.

        Your task is to generate a set of diverse dimensions and meaningful keywords that will be used to form effective search queries **in response to the user's question**.

        ## User Query:
        "{user_query}"

        ## Sample Reference (for inspiration only):
        {dimension_keywords_json}

        ## Your Task:
        1. Based on the user query, create **5–7 distinct dimensions** that capture different angles, contexts, or subtopics.
        2. For each dimension, generate **3–5 high-quality, non-overlapping keywords or phrases**.
        3. Ensure diversity across dimensions and semantic richness in keywords.

        ## Output Format:
        Return ONLY a JSON object like:
        {{
        "user_query": User Query,
        "dimensions": ["Dimension A", "Dimension B", ...],
        "keywords": {{
            "Dimension A": ["keyword1", "keyword2", "keyword3"],
            "Dimension B": ["keyword1", "keyword2", "keyword3"]
        }}
        }}

        ## Constraints:
        - Use double quotes only
        - No markdown or comments
        - Return valid JSON parsable by `json.loads()`
        - Output must only contain the JSON object
        """,

       "search_result_evaluation": """
        You are an expert Information Relevance Evaluator.

        Your task is to evaluate how well the following set of search results satisfies the user's information need.

        ⚠️ Important Scoring Principle:
        - If **at least one** of the results is **highly relevant and informative**, the overall score should be high.
        - You do **not** need all results to be good; one strong result is enough.

        ## Scoring Criteria (0–10):

        Evaluate based on the following:

        1. **Relevance** — At least one result directly addresses the user's query  
        2. **Usefulness** — Provides factual information, data, or context  
        3. **Authority** — Comes from expert or credible sources  
        4. **Clarity** — Avoids vague or promotional content  

        ## Score Guide:

        - 9–10: At least one result is highly relevant and valuable  
        - 7–8: Some partial matches, one may be moderately useful  
        - 5–6: Mostly weak, but something is loosely connected  
        - 3–4: Only vague or tangential mentions  
        - 1–2: Barely related, poor content  
        - 0: Completely irrelevant or no results at all

        ## Evaluation Target:
        Below is the user query, generated search string, and the list of retrieved results.

        {{solution_text}}

        ## Instructions:
        - If there are **no search results**, return a score of 0.
        - Return ONLY a number between 0 and 10.
        - Do not include any explanation, formatting, or notes.
        """
    }

    @classmethod
    def get(cls, name: str) -> str:
        return cls.templates[name]
