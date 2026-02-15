import numpy as np

class VarianceScoreboard:
    """
    ΔΩ-INTELLIGENCE: 0xVARIANCE_SCOREBOARD | STATUS: ACTIVE
    Assigns letter grades to model performance based on 0.05V compliance.
    """
    
    GRADES = {
        "A+": (0.00, 0.01), # Sovereign Reference
        "A": (0.01, 0.03),  # Elite Stability
        "B": (0.03, 0.05),  # Compliant (0.05V)
        "C": (0.05, 0.10),  # Precision Breach
        "D": (0.10, 0.20),  # Critical Failure
        "F": (0.20, float('inf')) # Hallucination Cascade
    }

    def assign_grade(self, variance_score: float) -> str:
        """Determines letter grade based on variance score."""
        for grade, (low, high) in self.GRADES.items():
            if low <= variance_score < high:
                return grade
        return "F"

    def rank_models(self, results: list) -> list:
        """Ranks a list of model result dictionaries by their variance (lowest first)."""
        return sorted(results, key=lambda x: x['variance'])

# ΔΩ-SCOREBOARD_LOADED
