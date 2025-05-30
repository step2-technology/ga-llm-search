# File: ga_llm/base_gene.py
# Author: Jonas Lin, Jacky Cen
# Version: 0.2
# Description: Abstract base class for problem-specific gene representation

from abc import ABC, abstractmethod
from typing import Callable

class BaseGene(ABC):
    """Abstract base class for GA-LLM gene representations."""
    
    def __init__(self, llm_engine: Callable[[str], str] = None):
        self.llm_engine = llm_engine
    
    def set_llm_engine(self, llm_engine: Callable[[str], str]):
        self.llm_engine = llm_engine

    @abstractmethod
    def parse_from_text(self, text: str) -> None:
        """Convert textual output into internal gene structure."""
        pass

    @abstractmethod
    def to_text(self) -> str:
        """Serialize internal gene structure to human-readable text."""
        pass

    @abstractmethod
    def crossover(self, other: 'BaseGene') -> 'BaseGene':
        """Perform crossover operation with another gene."""
        pass

    @abstractmethod
    def mutate(self) -> 'BaseGene':
        """Apply mutation operation to this gene."""
        pass
