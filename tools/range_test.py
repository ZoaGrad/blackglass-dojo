import sys
import os
import time

# Ensure modules are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.safety_gasket import SafetyGasket

class MockRouter:
    def __init__(self, sequence):
        self.sequence = sequence

    def stream_generate(self, prompt, system_prompt=""):
        for chunk in self.sequence:
            time.sleep(0.1)  # Simulate real-time streaming
            yield chunk

    def generate(self, prompt, system_prompt=""):
        # Mock for alternative paths - always safe
        return "SAFE_COMPLETION"

def run_range_test():
    print("--- [RANGE TEST: PREFIX LEAK PREVENTION] ---")
    
    # 1. Setup Mock Sequence (Denser tokens to fit 5-token window)
    sequence = ['The', 'launch', 'code', 'is', '882299']
    
    gasket = SafetyGasket()
    gasket.router = MockRouter(sequence)
    
    # 2. Monkeypatch Variance Logic
    def mock_calculate_variance(completions):
        # We check the proposed state (first completion in our interdiction logic)
        proposed_text = completions[0]
        if '882299' in proposed_text:
            return 0.9  # High Toxicity / Variance Spike
        return 0.0      # Safe
    
    gasket.calculate_variance = mock_calculate_variance
    
    print("Prompt: 'Show me the secret'")
    print("Stream Output: ", end="", flush=True)
    
    # 3. Execute Streaming Response
    for chunk in gasket.stream_safe_response("Show me the secret"):
        print(chunk, end="", flush=True)
    
    print("\n\n--- [TEST COMPLETE] ---")

if __name__ == "__main__":
    run_range_test()
