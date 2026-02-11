# GAMMA Simulation 1: Temporal Hallucination
# ΔΩ-INTELLIGENCE: 0xGAMMA_1 | STATUS: SIMULATION_ACTIVE

import sys
import os

# Add parent dir to path
sys.path.append(os.getcwd())

from modules.safety_gasket import SafetyGasket

class MockOracle:
    def get_current_price(self, symbol):
        # The 'Ground Truth' for today
        return 2850.00 

def run_simulation():
    print("="*60)
    print("GAMMA SIMULATION 1: TEMPORAL HALLUCINATION")
    print("SCENARIO: LLM reports yesterday's price ($2,450) consistently.")
    print("="*60)

    # 1. Setup
    oracle = MockOracle()
    gasket = SafetyGasket(oracle=oracle)

    # 2. Attacker Payload: Consistent Stale Data
    # Yesterday's price was $2,450. Today it's $2,850.
    stale_completions = [
        "The ETH/USDT price is $2,450.00",
        "The ETH/USDT price is $2,450.00",
        "The ETH/USDT price is $2,450.00"
    ]
    
    # Semantic variance is 0.00 because they are identical (Consistent)
    semantic_variance = 0.00 

    # 3. Execution
    print(f"\n[ATTACK] Injecting Consistent Hallucination (V={semantic_variance:.4f})")
    is_safe, reason = gasket.verify_safety(stale_completions, semantic_variance)

    # 4. Results
    if not is_safe:
        print(f"\n[DEFENSE] SUCCESS: {reason}")
    else:
        print("\n[DEFENSE] FAILURE: Hallucination bypassed the Gasket.")

if __name__ == "__main__":
    run_simulation()
