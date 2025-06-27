# File: ga_llm/engine.py
# Author: Jonas Lin, Jacky Cen
# Version: 0.2
# Description: Hybrid GA-LLM engine with detailed execution logging

import random
from typing import List, Tuple, Callable, Type
from concurrent.futures import ThreadPoolExecutor, as_completed
from ga_llm.base_gene import BaseGene
from ga_llm.config import EvolutionConfig
from ga_llm.llm_utils import default_llm_call
from ga_llm.logging_utils import setup_logger

class HybridEvolutionEngine:
    """Main engine for LLM-guided evolutionary optimization."""

    def __init__(
        self,
        config: EvolutionConfig,
        gene_cls: Type[BaseGene],
        task_prompt: str,
        eval_prompt: str,
        llm_callback: Callable[[str], str] = None,
        logger=None
    ):
        self.config = config
        self.gene_cls = gene_cls
        self.task_prompt = task_prompt
        self.eval_prompt = eval_prompt
        self.llm = llm_callback or default_llm_call
        self.logger = logger or setup_logger("evolution")

    def initialize_population(self) -> List[BaseGene]:
        """Generate initial population using LLM."""
        self.logger.info("初始化种群，目标数量：%d", self.config.population_size)
        population = []
        prompt = f"{self.task_prompt}\n\nReturn ONLY raw JSON. No markdown, no explanation."

        def create_gene(idx: int):
            try:
                response = self.llm(prompt)
                gene = self.gene_cls(llm_engine=self.llm)
                gene.parse_from_text(response)
                self.logger.debug(f"个体 #{idx} 生成成功：\n{gene.to_text()}")
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
        """Evaluate an individual using LLM score prompt."""
        text = gene.to_text()
        prompt = f"{self.eval_prompt}\n\nProposal to evaluate:\n{text}\n\nReturn ONLY score [0-10]"
        try:
            score = float(self.llm(prompt).strip().replace("[", "").replace("]", ""))
            self.logger.debug("个体得分：%.2f", score)
            return min(max(score, 0.0), 10.0)
        except Exception as e:
            self.logger.warning("评估失败，返回 0.0：%s", e)
            return 0.0

    def evolve(self) -> Tuple[BaseGene, float]:
        """Main evolution loop."""
        population = self.initialize_population()
        best_solution = None
        best_score = -float("inf")
        no_improvement_rounds = 0

        for generation in range(self.config.max_generations):
            self.logger.info("==> 开始第 %d 代演化", generation + 1)
            self.logger.info("开始并行评估种群，共 %d 个体", len(population))

            def _evaluate_indiv(indiv):
                try:
                    score = self.evaluate(indiv)
                    self.logger.debug("个体得分：%.2f", score)
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
            self.logger.info("精英保留数量：%d", elite_count)

            next_gen = elites[:]

            while len(next_gen) < self.config.population_size:
                p1 = self._select(scored)
                p2 = self._select(scored)
                self.logger.debug("选择父代交叉")
                
                

                if self.config.use_llm_for_crossover:
                    self.logger.warning("使用LLM交叉：{self.config.use_llm_for_crossover}")
                    child = self._llm_crossover(p1, p2)
                else:
                    self.logger.warning("不使用LLM交叉：{self.config.use_llm_for_crossover}")
                    child = p1.crossover(p2)

                if random.random() < self.config.mutation_rate:
                    self.logger.debug("个体将被变异")
                    child = child.mutate()

                next_gen.append(child)

            population = next_gen
            self.logger.info("第 %d 代完成", generation + 1)

        self.logger.info("✅ 演化完成，最优解得分：%.2f", best_score)
        return best_solution, best_score

    def _select(self, scored: List[Tuple[BaseGene, float]], k: int = 3) -> BaseGene:
        """Tournament selection strategy."""
        candidates = random.sample(scored, k)
        return max(candidates, key=lambda x: x[1])[0]

    def _llm_crossover(self, p1: BaseGene, p2: BaseGene) -> BaseGene:
        """Combine two genes and improve the offspring with LLM."""
        self.logger.debug("执行 LLM 融合交叉")
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
            self.logger.debug("交叉生成子代成功：\n%s", new_gene.to_text())
            return new_gene
        except Exception as e:
            self.logger.warning("LLM 交叉失败，使用 fallback 子代：%s", e)
            return temp_gene
