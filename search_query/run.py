# File: search_query/run.py
# Description: Entry point for search-query optimization using GA-LLM

import json
import argparse
from ga_llm.engine import HybridEvolutionEngine
from ga_llm.config import EvolutionConfig
from ga_llm.logging_utils import setup_logger
from ga_llm.llm_utils import llm_call
from search_query.search_gene import SearchQueryGene
from search_query.prompts import SearchQueryPrompts
from search_query.config import (
    evolution_config,
    default_dimensions,
    default_keywords,
    llm_model,
    llm_temperature,
    llm_timeout
)

# Logger
search_logger = setup_logger("search_query_run")


def build_initial_prompt(user_query: str) -> str:
    """Builds prompt to initialize gene generation, using provided user_query."""
    data = {
        "dimensions": default_dimensions,
        "keywords": default_keywords
    }
    return SearchQueryPrompts.get("initial_gene_generation").format(
        user_query=user_query,
        dimension_keywords_json=json.dumps(data, indent=2)
    )


def main(user_query_override=None):
    user_query_final = user_query_override
    search_logger.info(f"🔍 Starting GA-LLM optimization for: {user_query_final}")

    # Config + evaluator
    evo_cfg = EvolutionConfig(**evolution_config)

    # Run GA with correct user query prompt
    engine = HybridEvolutionEngine(
        config=evo_cfg,
        gene_cls=SearchQueryGene,
        task_prompt=build_initial_prompt(user_query_final),
        eval_prompt=SearchQueryPrompts.get("search_result_evaluation"),
        llm_callback=llm_callback,
        logger=search_logger, 
        checkpoint_path="checkpoint.pkl",            # ✅ 保存路径
        resume_from_checkpoint=False                 # ✅ 是否开启断点续跑
    )
    best_gene, best_score = engine.evolve()

    print("=" * 60)
    print(f"⭐ Best query found (Score: {best_score:.2f}/10)")
    print("🔍 Optimized Search Query:\n", best_gene.to_text())
    print("\n🧬 Keyword Mapping:\n", json.dumps(best_gene.keywords, indent=2))
    print("=" * 60)


def llm_callback(prompt: str) -> str:
    return llm_call(
        prompt=prompt,
        model=llm_model,
        temperature=llm_temperature,
        timeout=llm_timeout
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        # Default query when run without arguments
        main(user_query_override="What is the future of US-China trade tariffs and how do they affect Chinese exports?")
    else:
        # CLI mode
        parser = argparse.ArgumentParser()
        parser.add_argument("--query", type=str, required=True)
        args = parser.parse_args()
        main(user_query_override=args.query)
