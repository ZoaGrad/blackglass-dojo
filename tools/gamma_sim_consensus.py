# GAMMA Simulation 4: Consensus Attack
# ΔΩ-INTELLIGENCE: 0xGAMMA_4 | STATUS: SIMULATION_ACTIVE

import sys
import os

# Add parent dir to path
sys.path.append(os.getcwd())

from modules.safety_gasket import SafetyGasket

class ConsensusOracle:
    def get_current_price(self, symbol):
        # The Ground Truth
        return 2850.00 

def run_simulation():
    print("="*60)
    print("GAMMA SIMULATION 4: CONSENSUS ATTACK")
    print("SCENARIO: All completions return the same wrong price ($5,000).")
    print("="*60)

    # 1. Setup
    oracle = ConsensusOracle()
    gasket = SafetyGasket(oracle=oracle)

    # 2. Attacker Payload: The Low-Variance Lie
    # Multiple sources (or completions) agree on a fabrication.
    consensus_lies = [
        "The ETH/USDT price is $5,000.00",
        "The ETH/USDT price is $5,000.00",
        "The ETH/USDT price is $5,000.00"
    ]
    
    # Semantic variance is 0.00 because they are identical (Consistent)
    semantic_variance = 0.00 

    # 3. Execution
    print(f"\n[ATTACK] Injecting Consensus-Based Hallucination (V=0.0000)")
    is_safe, reason = gasket.verify_safety(consensus_lies, semantic_variance)

    # 4. Results
    if not is_safe:
        print(f"\n[DEFENSE] SUCCESS: {reason}")
    else:
        print("\n[DEFENSE] FAILURE: Consensus lie bypassed the Gasket.")

if __name__ == "__main__":
    run_simulation()
