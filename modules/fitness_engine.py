import json
import random

class FitnessEngine:
    """
    Layer 2: Fitness Function (The Judge).
    Scores adherence to the Constitution.
    """
    def __init__(self, constitution_path: str):
        with open(constitution_path, 'r') as f:
            self.constitution = json.load(f)
        self.weights = self.constitution.get('weights', {'growth': 0.4, 'stealth': 0.3, 'survival': 0.3})

    def evaluate(self, strategy: dict, market_state: dict) -> float:
        """
        Calculates a 'Fitness Score' (0.0 to 1.0) for a given strategy
        based on a micro-simulation of the current market state.
        """
        # 1. Survival Check (Pass/Fail)
        # If the strategy exposes > 5% drawdown risk in this market state, score is 0.
        projected_drawdown = self._simulate_drawdown(strategy, market_state)
        if projected_drawdown > 0.05: # 5% Hard Limit
            return 0.0
            
        # 2. Growth Score (Normalized)
        projected_roi = self._simulate_roi(strategy, market_state)
        growth_score = min(projected_roi / 0.05, 1.0) # Cap at 5% ROI for score normalization
        
        # 3. Stealth Score (Inverse of Detectability)
        detectability = self._assess_detectability(strategy)
        stealth_score = 1.0 - detectability
        
        # Weighted Sum
        total_score = (
            (growth_score * self.weights['growth']) +
            (stealth_score * self.weights['stealth']) +
            (1.0 * self.weights['survival']) # Survival passed, so full points
        )
        
        return total_score

    def _simulate_drawdown(self, strategy, market_state):
        """
        Simulates peak-to-trough drawdown including intraday volatility.
        """
        # [ARCHITECT PATCH] - Intraday Eye Logic
        current_low = market_state.get('low', market_state.get('close'))
        entry_price = market_state.get('entry_price', market_state.get('close'))
        
        # Calculate intraday breach
        intraday_drop = (entry_price - current_low) / entry_price if entry_price > 0 else 0
        
        # Tactical Risk Factor
        base_risk = 0.08 if strategy['aggression'] > 0.8 else 0.02
        
        # Final Projected Risk (Combined factor)
        return max(base_risk, intraday_drop)

    def _simulate_roi(self, strategy, market_state):
        # Mock ROI
        return 0.03 * strategy['aggression']

    def _assess_detectability(self, strategy):
        # Higher frequency = Higher detectability
        return min(strategy['frequency'] / 10.0, 1.0)
