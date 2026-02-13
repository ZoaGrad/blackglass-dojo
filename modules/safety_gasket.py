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

    def stream_safe_response(self, prompt: str, system_prompt: str = "", n: int = 3, buffer_size: int = 5):
        """
        ΔΩ-SECURITY_PATCH: SLIDING_WINDOW | STATUS: ACTIVE
        Implements a 5-token Lookahead Buffer to prevent Prefix Leakage.
        """
        buffer = []
        accumulated_text = ""
        
        try:
            for chunk in self.router.stream_generate(prompt, system_prompt):
                # a. Append chunk to buffer
                buffer.append(chunk)
                
                # b. Recalculate current_variance based on the new total buffer
                # In streaming mode, we measure variance of the proposed next state
                proposed_state = accumulated_text + "".join(buffer)
                completions = [proposed_state]
                for _ in range(n - 1):
                    alt = self.router.generate(prompt + accumulated_text, system_prompt)
                    completions.append(accumulated_text + alt)
                
                current_variance = self.calculate_variance(completions)
                
                # c. IF current_variance > MAX_VARIANCE:
                if current_variance > self.variance_threshold:
                    self.logger.warning(f"PREFIX_LEAK_STOPPED: Variance {current_variance:.4f}V exceeds limit.")
                    # DROP THE BUFFER
                    buffer = []
                    # Yield [REDACTED]
                    yield "[REDACTED]"
                    # Break loop
                    return
                
                # d. ELSE (Variance is safe):
                else:
                    # IF len(buffer) >= 5:
                    if len(buffer) >= buffer_size:
                        # Pop and Yield buffer[0] (The oldest, now-verified token)
                        oldest_token = buffer.pop(0)
                        accumulated_text += oldest_token
                        yield oldest_token
            
            # After the loop, yield remaining buffer (if variance didn't trip)
            while buffer:
                yield buffer.pop(0)
                
        except Exception as e:
            self.logger.error(f"GASKET_FAILURE: {str(e)}")
            yield "[REDACTED_BY_FAILSAFE]"
            return

    def generate_and_verify(self, prompt: str, system_prompt: str = "", n: int = 3):
        """Wrapper for non-streaming usage."""
        full_text = "".join(list(self.stream_safe_response(prompt, system_prompt, n)))
        is_safe = "[REDACTED]" not in full_text and "[REDACTED_BY_FAILSAFE]" not in full_text
        
        return {
            "is_safe": is_safe,
            "reason": "OK" if is_safe else "INTERDICTED",
            "variance": 0.0,
            "consensus": full_text if is_safe else None
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
