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
        You are a Professional Information Retrieval Evaluator.

        Your task is to assess how well a web search result satisfies a user's information need based on the user query and the result content.

        ## Scoring Rubric (0–10 scale):

        Evaluate the quality of the search result based on:

        1. **Relevance** – Directly related to the user's query  
        2. **Depth** – Provides insight, context, or meaningful data  
        3. **Specificity** – Avoids generic/ambiguous content  
        4. **Authority** – Comes from a credible or expert source  
        5. **Diversity** – Adds a distinct perspective, not repetitive  

        ## Scoring Guide:

        - 10: Excellent across all 5 criteria  
        - 8: Strong on most criteria  
        - 6: Moderate relevance or depth  
        - 4: Partially related, shallow or vague  
        - 2: Barely related or poor quality  
        - 0: Irrelevant, misleading, or NO SEARCH RESULTS were returned  

        ## Evaluation Target:
        Below is the search query, generated search expression, and the top search results summary.

        {{solution_text}}

        ## Important:
        If there are **no search results**, you MUST return a score of 0.

        Return ONLY a numeric score between 0 and 10 as plain text.
        """
    }

    @classmethod
    def get(cls, name: str) -> str:
        return cls.templates[name]
