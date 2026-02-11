import random
import copy
from typing import List, Dict
from .fitness_engine import FitnessEngine

class StrategyBreeder:
    """
    Layer 3: Strategy Breeder (The Evolution).
    Mutates parameters to create the next generation of logic.
    """
    def __init__(self, fitness_engine: FitnessEngine):
        self.engine = fitness_engine
        self.mutation_rate = 0.1
        self.base_strategy_template = {
            "name": "proto_strategy",
            "aggression": 0.5, # 0.0 to 1.0
            "frequency": 5,    # Trades per hour
            "slippage_tolerance": 0.005,
            "gas_priority": 1.0 # Gwei
        }

    def breed_generation(self, parent_strategy: Dict, generation_size: int, market_state: Dict) -> Dict:
        """
        Creates 'generation_size' variants, scores them, and returns the Alpha (Best).
        """
        population = []
        
        # 1. Mutate
        for i in range(generation_size):
            child = self._mutate(parent_strategy, i)
            population.append(child)
            
        # 2. Select (Score)
        scored_population = []
        for strat in population:
            score = self.engine.evaluate(strat, market_state)
            scored_population.append((score, strat))
            
        # 3. Evolve
        # Sort by score descending
        scored_population.sort(key=lambda x: x[0], reverse=True)
        
        best_score, best_strat = scored_population[0]
        print(f">> [BREEDER] Generation Complete. Alpha Score: {best_score:.4f} (Aggression: {best_strat['aggression']:.2f})")
        
        return best_strat

    def _mutate(self, parent: Dict, seed: int) -> Dict:
        """
        Applies random mutations to strategy genes.
        """
        child = copy.deepcopy(parent)
        child['name'] = f"{parent['name']}_v{seed}"
        
        # Gene: Aggression
        if random.random() < self.mutation_rate:
            child['aggression'] = max(0.0, min(1.0, child['aggression'] + random.uniform(-0.1, 0.1)))
            
        # Gene: Frequency
        if random.random() < self.mutation_rate:
            child['frequency'] = max(1, child['frequency'] + random.randint(-2, 2))
            
        # Gene: Gas Priority
        if random.random() < self.mutation_rate:
            child['gas_priority'] = max(0.1, child['gas_priority'] + random.uniform(-0.5, 0.5))
            
        return child
