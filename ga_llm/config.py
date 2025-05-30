# File: ga_llm/config.py
# Author: Jonas Lin, Jacky Cen
# Version: 0.2
# Description: Configuration container for evolutionary search

class EvolutionConfig:
    """Container for all configurable parameters of the evolution engine."""
    
    def __init__(
        self,
        population_size: int = 30,
        elite_ratio: float = 0.2,
        mutation_rate: float = 0.3,
        max_generations: int = 20,
        llm_temperature: float = 0.7,
        use_llm_for_crossover: bool = True,
        early_stopping_rounds: int = 5
    ):
        self.population_size = population_size
        self.elite_ratio = elite_ratio
        self.mutation_rate = mutation_rate
        self.max_generations = max_generations
        self.llm_temperature = llm_temperature
        self.use_llm_for_crossover = use_llm_for_crossover
        self.early_stopping_rounds = early_stopping_rounds
