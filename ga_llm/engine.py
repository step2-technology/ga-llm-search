# File: ga_llm/engine.py
# Author: Jonas Lin, Jacky Cen
# Description: Hybrid GA-LLM engine with evaluator injection, score tracking, checkpointing, and result history.

import random
import pickle
import os
from typing import List, Tuple, Callable, Type, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from ga_llm.base_gene import BaseGene
from ga_llm.config import EvolutionConfig
from ga_llm.evaluation import Evaluator
from ga_llm.constraints import ConstraintValidator, AlwaysPassValidator
from ga_llm.llm_utils import default_llm_call
from ga_llm.logging_utils import setup_logger


class HybridEvolutionEngine:
    def __init__(
        self,
        config: EvolutionConfig,
        gene_cls: Type[BaseGene],
        task_prompt: str,
        eval_prompt: str,
        llm_callback: Callable[[str], str] = None,
        evaluator: Optional[Evaluator] = None,
        constraint_validator: Optional[ConstraintValidator] = None,
        logger=None,
        checkpoint_path: Optional[str] = None,         # ✅ 支持断点恢复
        resume_from_checkpoint: bool = False           # ✅ 是否从 checkpoint 恢复
    ):
        self.config = config
        self.gene_cls = gene_cls
        self.task_prompt = task_prompt
        self.eval_prompt = eval_prompt
        self.llm = llm_callback or default_llm_call
        self.logger = logger or setup_logger("evolution")

        self.evaluator = evaluator or Evaluator(eval_prompt, self.llm)
        self.constraint_validator = constraint_validator or AlwaysPassValidator()

        self.checkpoint_path = checkpoint_path or "evolution_checkpoint.pkl"
        self.resume = resume_from_checkpoint

    def initialize_population(self) -> List[BaseGene]:
        self.logger.info("初始化种群，目标数量：%d", self.config.population_size)
        population = []

        prompt = f"{self.task_prompt}\n\nReturn ONLY raw JSON. No markdown, no explanation."

        def create_gene(idx: int):
            try:
                response = self.llm(prompt)
                gene = self.gene_cls(llm_engine=self.llm)
                gene.parse_from_text(response)
                return gene
            except Exception as e:
                self.logger.warning(f"个体 #{idx} 生成失败: {e}")
                return None

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(create_gene, i + 1) for i in range(self.config.population_size)]
            for future in as_completed(futures):
                gene = future.result()
                if gene:
                    population.append(gene)

        return population

    def evaluate(self, gene: BaseGene) -> float:
        """支持 float 或 dict 格式的返回值。dict 中必须包含 final_score。"""
        try:
            result = self.evaluator.score(gene)

            if isinstance(result, dict):
                score = float(result.get("final_score", 0.0))
                if hasattr(gene, 'metadata'):
                    gene.metadata["score_details"] = result
            else:
                score = float(result)

            if hasattr(gene, 'set_score'):
                gene.set_score(score)

            return score

        except Exception as e:
            self.logger.warning("评估失败，返回 0.0：%s", e)
            if hasattr(gene, 'set_score'):
                gene.set_score(0.0)
            return 0.0

    def evolve(self, return_history: bool = False) -> Union[Tuple[BaseGene, float], Tuple[BaseGene, float, List[List[Tuple[BaseGene, float]]]]]:
        """演化主流程。可选返回每一代的历史记录。"""
        if self.resume and os.path.exists(self.checkpoint_path):
            self.logger.info("🔁 从 checkpoint 恢复演化状态")
            with open(self.checkpoint_path, "rb") as f:
                state = pickle.load(f)
                population = state["population"]
                best_solution = state["best_solution"]
                best_score = state["best_score"]
                start_gen = state["generation"]
                history = state.get("history", [])
        else:
            population = self.initialize_population()
            best_solution = None
            best_score = -float("inf")
            start_gen = 0
            history = []

        no_improvement_rounds = 0

        for generation in range(start_gen, self.config.max_generations):
            self.logger.info("==> 开始第 %d 代演化", generation + 1)

            def _evaluate_indiv(indiv):
                try:
                    score = self.evaluate(indiv)
                    return (indiv, score)
                except Exception as e:
                    self.logger.warning("评分失败，默认 0 分: %s", e)
                    return (indiv, 0.0)

            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(_evaluate_indiv, indiv) for indiv in population]
                scored = [future.result() for future in as_completed(futures)]

            scored.sort(key=lambda x: x[1], reverse=True)
            top_gene, top_score = scored[0]
            self.logger.info("第 %d 代最佳得分：%.2f", generation + 1, top_score)

            if top_score > best_score:
                best_solution, best_score = top_gene, top_score
                no_improvement_rounds = 0
                self.logger.info("🔼 最优解更新，当前最高得分：%.2f", best_score)
            else:
                no_improvement_rounds += 1
                self.logger.info("未提升轮次：%d/%d", no_improvement_rounds, self.config.early_stopping_rounds)
                if no_improvement_rounds >= self.config.early_stopping_rounds:
                    self.logger.warning("🎯 触发早停条件，演化终止。")
                    break

            elite_count = max(1, int(len(population) * self.config.elite_ratio))
            elites = [indiv for indiv, _ in scored[:elite_count]]
            next_gen = elites[:]

            while len(next_gen) < self.config.population_size:
                p1 = self._select(scored)
                p2 = self._select(scored)

                if self.config.use_llm_for_crossover:
                    child = self._llm_crossover(p1, p2)
                else:
                    child = p1.crossover(p2)

                if random.random() < self.config.mutation_rate:
                    child = child.mutate()

                if self.constraint_validator.is_valid(child):
                    next_gen.append(child)

            population = next_gen

            # ✅ 保存历史
            history.append(scored)

            # ✅ 保存 checkpoint
            try:
                with open(self.checkpoint_path, "wb") as f:
                    pickle.dump({
                        "generation": generation + 1,
                        "population": population,
                        "best_solution": best_solution,
                        "best_score": best_score,
                        "history": history
                    }, f)
                self.logger.debug("✅ Checkpoint 已保存")
            except Exception as e:
                self.logger.warning("⚠️ Checkpoint 保存失败：%s", e)

        self.logger.info("✅ 演化完成，最优解得分：%.2f", best_score)

        if return_history:
            return best_solution, best_score, history
        else:
            return best_solution, best_score

    def _select(self, scored: List[Tuple[BaseGene, float]], k: int = 3) -> BaseGene:
        candidates = random.sample(scored, k)
        return max(candidates, key=lambda x: x[1])[0]

    def _llm_crossover(self, p1: BaseGene, p2: BaseGene) -> BaseGene:
        temp_gene = p1.crossover(p2)
        merged_text = f"""Synthesize the best from the two candidates below.

Candidate A:
{p1.to_text()}

Candidate B:
{p2.to_text()}

{self.task_prompt}

Output ONLY the improved JSON.
No markdown, no explanation.
"""
        try:
            improved = self.llm(merged_text)
            new_gene = self.gene_cls(llm_engine=self.llm)
            new_gene.parse_from_text(improved)
            return new_gene
        except Exception as e:
            self.logger.warning("LLM 交叉失败，使用 fallback 子代：%s", e)
            return temp_gene
