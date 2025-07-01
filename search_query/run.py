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
from search_query.evaluator_with_info_store import EvaluatorWithInfoStore
# 导入 InformationStore 和导出函数
from info_store.information_store import InformationStore
from info_store.export_logger import export_info_items
from info_store.filter_llm_selector import filter_info_items_via_llm
from info_store.crawler import crawl_all
from info_store.extractor import extract_all
from info_store.info_pack_builder import build_info_pack, save_info_pack

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
    InformationStore.reset()
    search_logger.info(f"🔍 Starting GA-LLM optimization for: {user_query_final}")

    # 1. 构造 GA 配置和评估器
    evo_cfg = EvolutionConfig(**evolution_config)
    evaluator = EvaluatorWithInfoStore(
        llm_fn=llm_callback,
        score_threshold=7.0
    )

    # 2. 启动遗传算法搜索
    engine = HybridEvolutionEngine(
        config=evo_cfg,
        gene_cls=SearchQueryGene,
        task_prompt=build_initial_prompt(user_query_final),
        eval_prompt=SearchQueryPrompts.get("search_result_evaluation"),
        evaluator=evaluator,
        llm_callback=llm_callback,
        logger=search_logger, 
        checkpoint_path="checkpoint.pkl",            # ✅ 保存路径
        resume_from_checkpoint=False                 # ✅ 是否开启断点续跑
    )
    best_gene, best_score = engine.evolve()

    # 3. 打印最佳基因信息
    print("=" * 60)
    print(f"⭐ Best query found (Score: {best_score:.2f}/10)")
    print("🔍 Optimized Search Query:\n", best_gene.to_text())
    print("\n🧬 Keyword Mapping:\n", json.dumps(best_gene.keywords, indent=2))
    print("=" * 60)

    # 4. 高分 InfoItem 二次筛选
    print(f"📊 Running second-stage filtering via LLM...")
    selected_ids = filter_info_items_via_llm(user_query_final, llm_callback, 20)
    print(f"✅ Selected {len(selected_ids)} items after LLM filtering: {selected_ids}")

    InformationStore.filter_by_selection(selected_ids)
    final_items = InformationStore.get_all()
    print(f"🧹 InfoStore now contains {len(final_items)} items after filtering:\n")
    for i, item in enumerate(final_items, 1):
        print(f"{i}. [{item.score:.2f}] {item.title}\n   URL: {item.url}\n")

    # 5. 网页爬取
    print(f"🌐 Crawling full content for {len(final_items)} items...")
    crawl_all(final_items)
    print("✅ Crawling complete.\n")

    # 6. 结构化抽取
    print(f"📐 Extracting structured data via LLM...")
    extract_all(final_items, llm_callback)  # 请确保你实现了这个函数
    print("✅ Structured extraction complete.\n")

    # 7. 导出记录
    export_info_items(final_items)
    print(f"📦 Exported {len(final_items)} InfoItems to info_store/log directory.")
    
    # 8. 构建 InfoPack（摘要 + 知识图谱）
    print(f"📦 Building final InfoPack...")
    info_pack = build_info_pack(user_query_final)
    save_info_pack(info_pack)

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
