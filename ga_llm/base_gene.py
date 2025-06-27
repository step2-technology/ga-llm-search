# File: ga_llm/base_gene.py
# Author: Jonas Lin, Jacky Cen
# Version: 0.3
# Description: Abstract base class for problem-specific gene representation

from abc import ABC, abstractmethod
from typing import Callable, Optional


class BaseGene(ABC):
    """Abstract base class for GA-LLM gene representations."""

    def __init__(self, llm_engine: Callable[[str], str] = None):
        self.llm_engine = llm_engine
        self._score: Optional[float] = None  # ✅ 评分属性
        self.metadata: dict = {}             # ✅ 扩展元数据容器

    def set_llm_engine(self, llm_engine: Callable[[str], str]):
        self.llm_engine = llm_engine

    def set_score(self, score: float):
        """Set evaluation score for this gene."""
        self._score = score

    def get_score(self) -> Optional[float]:
        """Get previously evaluated score if available."""
        return self._score

    @abstractmethod
    def parse_from_text(self, text: str) -> None:
        pass

    @abstractmethod
    def to_text(self) -> str:
        pass

    @abstractmethod
    def crossover(self, other: 'BaseGene') -> 'BaseGene':
        pass

    @abstractmethod
    def mutate(self) -> 'BaseGene':
        pass
