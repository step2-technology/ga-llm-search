# File: ga_llm/constraints.py
# Author: Jonas Lin, Jacky Cen
# Version: 0.2
# Description: Abstract constraint checker for hard rule enforcement

from abc import ABC, abstractmethod
from .base_gene import BaseGene

class ConstraintValidator(ABC):
    """Abstract interface for constraint validation."""

    @abstractmethod
    def is_valid(self, gene: BaseGene) -> bool:
        """Return True if gene meets all hard constraints."""
        pass


class AlwaysPassValidator(ConstraintValidator):
    """Default validator that accepts everything (for testing)."""

    def is_valid(self, gene: BaseGene) -> bool:
        return True
