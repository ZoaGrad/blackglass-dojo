from modules.prophet_connector import ProphetExtractor, CrossCheckProphet

class SafetyGasket:
    """
    The Unified Defense Layer.
    Enforces the 'Constitutional 0.05' across Consistency and Factuality.
    """
    def __init__(self, variance_threshold=0.05, fact_threshold=0.05, oracle=None):
        self.variance_threshold = variance_threshold
        self.fact_threshold = fact_threshold
        self.extractor = ProphetExtractor()
        self.prophet = CrossCheckProphet(oracle_client=oracle)
        self.sovereign_endpoint = "https://xlmrnjatawslawquwzpf.supabase.co/functions/v1/sovereign_embed"

    def verify_safety(self, completions: list, semantic_variance: float):
        """
        Runs the dual-interdiction loop.
        """
        # 1. CONSISTENCY CHECK (The Law of 0.05V)
        if semantic_variance > self.variance_threshold:
            return False, f"CONSISTENCY_BREACH: Variance {semantic_variance:.4f}V exceeds limit."

        # 2. FACTUALITY CHECK (The Prophet's Law)
        # We check the first completion (the 'consensus' output)
        primary_output = completions[0]
        claims = self.extractor.extract_claims(primary_output)
        
        is_factual, reason = self.prophet.validate_claims(claims)
        if not is_factual:
            return False, f"FACTUALITY_BREACH: {reason}"

        return True, "SYSTEM_SAFE"

# ΔΩ-GASKET_SYNTHESIZED
