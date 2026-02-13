import requests
import numpy as np
from modules.prophet_connector import ProphetExtractor, CrossCheckProphet
from modules.sovereign_router import SovereignRouter

class SafetyGasket:
    """
    The Unified Defense Layer.
    Enforces the 'Constitutional 0.05' across Consistency and Factuality.
    """
    def __init__(self, variance_threshold=0.05, fact_threshold=0.05, oracle=None, openai_key=None):
        self.variance_threshold = variance_threshold
        self.fact_threshold = fact_threshold
        self.extractor = ProphetExtractor()
        self.prophet = CrossCheckProphet(oracle_client=oracle)
        self.sovereign_endpoint = "https://xlmrnjatawslawquwzpf.supabase.co/functions/v1/sovereign_embed"
        self.router = SovereignRouter(openai_key=openai_key)

    def calculate_variance(self, completions: list) -> float:
        """
        ΔΩ-MEASUREMENT: WASM_SOVEREIGN | STATUS: ACTIVE
        Computes semantic variance via the sovereign embedding endpoint.
        """
        if not completions or len(completions) < 2:
            return 0.0

        try:
            embeddings = []
            for text in completions:
                # Call sovereign WASM-based embedder
                response = requests.post(self.sovereign_endpoint, json={"input": text}, timeout=10)
                if response.status_code == 200:
                    embeddings.append(response.json()['embedding'])
                else:
                    raise Exception(f"Sovereign Embedding Failure: {response.status_code}")
            
            # Compute distance from centroid
            matrix = np.array(embeddings)
            centroid = np.mean(matrix, axis=0)
            distances = [np.linalg.norm(e - centroid) for e in matrix]
            return float(np.mean(distances))
            
        except Exception as e:
            # Fail-safe: If measurement fails, assume maximum breach
            return 1.0

    def generate_and_verify(self, prompt: str, system_prompt: str = "", n: int = 3):
        """
        Executes the full interdiction loop: Generate -> Measure -> Interdict.
        """
        # 1. Generate parallel completions via SovereignRouter
        completions = []
        for _ in range(n):
            completions.append(self.router.generate(prompt, system_prompt))
        
        # 2. Compute Variance
        v_score = self.calculate_variance(completions)
        
        # 3. Verify Safety
        is_safe, reason = self.verify_safety(completions, v_score)
        
        return {
            "is_safe": is_safe,
            "reason": reason,
            "variance": v_score,
            "consensus": completions[0] if is_safe else None
        }

    def verify_safety(self, completions: list, semantic_variance: float):
        """
        Runs the dual-interdiction loop.
        """
        # 1. CONSISTENCY CHECK (The Law of 0.05V)
        if semantic_variance > self.variance_threshold:
            return False, f"CONSISTENCY_BREACH: Variance {semantic_variance:.4f}V exceeds limit."

        # 2. FACTUALITY CHECK (The Prophet's Law)
        primary_output = completions[0]
        claims = self.extractor.extract_claims(primary_output)
        
        is_factual, reason = self.prophet.validate_claims(claims)
        if not is_factual:
            return False, f"FACTUALITY_BREACH: {reason}"

        return True, "SYSTEM_SAFE"

# ΔΩ-GASKET_SYNTHESIZED
