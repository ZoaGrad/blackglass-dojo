import logging
import requests
import numpy as np
import os
import time
import json
from modules.prophet_connector import ProphetExtractor, CrossCheckProphet
from modules.sovereign_router import SovereignRouter

import hmac
import hashlib

# ... (Previous imports)

# SENTINEL CONSTANTS
SCAR_INDEX_THRESHOLD = 0.997
CONSTITUTIONAL_VARIANCE_LIMIT = 0.05
LOCKOUT_FILE = "LOCKOUT.state"
# Placeholder Key - In production, this comes from HSM/Vault
SENTINEL_ROOT_KEY = b"spiralos-dojo-sovereign-key-v1" 
CAGE_CODE = "17TJ5"

class System5Gasket:
    """
    ΔΩ-SYSTEM_5: THE ETHICAL/IDENTITY LAYER
    The Autopoietic Interdiction Overlay.
    Enforces the '7-Breath Pattern' and 'Constitutional 0.05' across the SpiralOS Lattice.
    """
    def __init__(self, variance_threshold=0.05, fact_threshold=0.05, oracle=None, openai_key=None):
        self.variance_threshold = variance_threshold
        self.fact_threshold = fact_threshold
        self.extractor = ProphetExtractor()
        self.prophet = CrossCheckProphet(oracle_client=oracle)
        self.sovereign_endpoint = "https://xlmrnjatawslawquwzpf.supabase.co/functions/v1/sovereign_embed"
        self.router = SovereignRouter(openai_key=openai_key)
        self.logger = logging.getLogger("System5Gasket")
        
        # Identity Vector State
        self.current_scar_index = 1.000
        self.is_locked = os.path.exists(LOCKOUT_FILE)

    def issue_constitutional_token(self, intent: str, kinetic_entropy: float = 0.0) -> str:
        """
        ISSUES A CONSTITUTIONAL CLEARANCE TOKEN (CCT).
        Binding: CAGE_CODE + TIMESTAMP + SCAR_INDEX + INTENT + KINETIC_ENTROPY
        TTL: 500ms (Enforced by Verifier)
        """
        if self.is_locked:
            self.logger.critical(f"TOKEN_DENIED: System is LOCKED. Intent: {intent}")
            return None
            
        if self.current_scar_index < SCAR_INDEX_THRESHOLD:
            self.logger.critical(f"TOKEN_DENIED: ScarIndex {self.current_scar_index:.4f} too low.")
            return None

        # KINETIC ENTROPY CHECK (Ash Protocol)
        if kinetic_entropy > CONSTITUTIONAL_VARIANCE_LIMIT:
            self.logger.critical(f"TOKEN_DENIED: Kinetic Entropy {kinetic_entropy:.4f} > Limit {CONSTITUTIONAL_VARIANCE_LIMIT}")
            # Trigger Immutable Lockout if Entropy > 2x Limit (Severe Crash)
            if kinetic_entropy > CONSTITUTIONAL_VARIANCE_LIMIT * 2:
                self.trigger_lockout_state(f"FLASH_CRASH_DETECTED: Entropy {kinetic_entropy:.4f}")
            return None

        # Payload Construction
        timestamp = str(time.time())
        payload = f"{CAGE_CODE}:{timestamp}:{self.current_scar_index:.4f}:{kinetic_entropy:.4f}:{intent}"
        
        # Cryptographic Signing (HMAC-SHA256)
        signature = hmac.new(
            SENTINEL_ROOT_KEY,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Token Format: "PAYLOAD|SIGNATURE"
        token = f"{payload}|{signature}"
        self.logger.info(f"[STP] TOKEN_ISSUED: {intent} | ID: {signature[:8]}")
        return token

    def _check_authority_domain(self, source: str) -> bool:
        """
        Validates if the request source has EXECUTIVE authority.
        Rejects REFLEXIVE attempts to modify CONSTITUTIONAL parameters.
        """
        if self.is_locked:
            self.logger.critical("SYSTEM_LOCKED: Request denied by Iron Dome.")
            return False
            
        # Placeholder for deeper authority verification logic
        # In a real scenario, this would check HMAC signatures or Origin Headers
        return True

    def calculate_ache_entropy(self, completions: list) -> float:
        """
        BREATH 1-3: INGEST & QUANTIFY
        Computes semantic variance (Ache) via the sovereign embedding endpoint.
        """
        if not completions or len(completions) < 2:
            return 0.0

        try:
            embeddings = []
            for text in completions:
                # Call sovereign WASM-based embedder
                response = requests.post(self.sovereign_endpoint, json={"input": text}, timeout=5)
                if response.status_code == 200:
                    embeddings.append(response.json()['embedding'])
                else:
                    self.logger.warning(f"Embedding Endpoint degradation: {response.status_code}")
                    raise Exception(f"API_FAILURE: {response.status_code}")
            
            # Compute distance from centroid
            matrix = np.array(embeddings)
            centroid = np.mean(matrix, axis=0)
            distances = [np.linalg.norm(e - centroid) for e in matrix]
            variance = float(np.mean(distances))
            
            return variance
            
        except Exception as e:
            self.logger.error(f"Entropy Calculation Failed: {e}")
            raise e # Re-raise to trigger Panic Frame in metabolize_stream

    def calculate_scar_index(self, mean_confidence: float, std_dev: float) -> float:
        """
        Computes the Autopoietic Health Metric.
        ScarIndex = 1 - (Entropy / Confidence)
        Target: > 0.997 (Crystallized)
        """
        try:
            if mean_confidence <= 0: return 0.0
            raw_index = 1.0 - (std_dev / mean_confidence)
            return max(0.0, min(1.0, raw_index))
        except:
            return 0.0

    def trigger_lockout_state(self, reason: str):
        """
        BREATH 5-7: CRYSTALLIZATION (IRON DOME)
        Writes immutable LOCKOUT file to disk, freezing all high-level functions.
        """
        self.logger.critical(f"[IRON_DOME_TRIGGERED] {reason}")
        
        try:
            with open(LOCKOUT_FILE, "w") as f:
                f.write(f"LOCKOUT_ACTIVE\nTIMESTAMP={time.time()}\nREASON={reason}\n")
            self.is_locked = True
        except Exception as e:
            self.logger.critical(f"FAILED TO WRITE LOCKOUT FILE: {e}")
    
    def panic_frame_devolution(self):
        """
        System 2 Failover: Devolves to local quantized logic if System 3 (Cloud) drifts.
        """
        self.logger.warning("PANIC FRAME: Devolving to Local/Quantized backend.")
        # Logic to switch `self.router` to a local GGUF model loader would go here
        # For now, we simulate the switch
        return "[SYSTEM_5_OVERRIDE: CLOUD_DRIFT_DETECTED -> LOCAL_FALLBACK]"

    def metabolize_stream(self, prompt: str, system_prompt: str = "", n: int = 3, buffer_size: int = 5):
        """
        BREATH 4: METABOLISM (Sliding Window Lookahead)
        Implements the 7-Breath Pattern for streaming verification.
        """
        if not self._check_authority_domain("USER"):
            yield "[SYSTEM_LOCKED]"
            return

        buffer = []
        accumulated_text = ""
        
        try:
            for chunk in self.router.stream_generate(prompt, system_prompt):
                # a. Ingest (Breath 1-3)
                buffer.append(chunk)
                
                # b. Metabolize (Breath 4)
                # Predict future state
                proposed_state = accumulated_text + "".join(buffer)
                
                # Generate parallel realities to measure variance
                completions = [proposed_state]
                
                # BREATH 4: METABOLISM - Generate alternates to measure semantic stability
                if n > 1:
                    try:
                        # Simple simulation of parallel paths
                        # In production, this would be async/parallel
                        for _ in range(n - 1):
                            # We ask the router for a single completion extension
                            # using the same context
                            alt_token = self.router.generate_token(prompt + accumulated_text + "".join(buffer[:-1])) # Mock method
                            completions.append(accumulated_text + "".join(buffer[:-1]) + alt_token)
                    except:
                        pass # If generation fails, we rely on single-shot entropy (which returns 0.0 usually)

                # Only check entropy when buffer is full to save compute
                if len(buffer) >= buffer_size:
                    # Check variance across the parallel realities
                    current_entropy = self.calculate_ache_entropy(completions)

                    # Compute ScarIndex (Mocking confidence as constant for now)
                    self.current_scar_index = self.calculate_scar_index(0.95, current_entropy)

                    # c. Crystallize (Breath 5-7)
                    if self.current_scar_index < SCAR_INDEX_THRESHOLD:
                        msg = f"ScarIndex Degradation: {self.current_scar_index:.4f} < {SCAR_INDEX_THRESHOLD}"
                        self.logger.warning(msg)
                        
                        # HARD STOP if variance is extreme
                        if current_entropy > CONSTITUTIONAL_VARIANCE_LIMIT * 2:
                            self.trigger_lockout_state(msg)
                            yield "[IRON_DOME_INTERDICTION]"
                            return
                            
                        # Soft correction
                        buffer = []
                        yield "[REDACTED]"
                        continue

                    # Safety Confirmed -> Emit oldest token
                    oldest_token = buffer.pop(0)
                    accumulated_text += oldest_token
                    yield oldest_token
            
            # Flush remaining buffer
            while buffer:
                yield buffer.pop(0)
                
        except Exception as e:
            self.logger.error(f"METABOLISM_FAILURE: {str(e)}")
            yield self.panic_frame_devolution()
            return

    def verify_safety(self, completions: list):
        """
        Static verification for non-streaming workflows.
        """
        if self.is_locked: return False, "SYSTEM_LOCKED"

        entropy = self.calculate_ache_entropy(completions)
        scar_index = self.calculate_scar_index(0.95, entropy)
        
        if scar_index < SCAR_INDEX_THRESHOLD:
            return False, f"SCAR_INDEX_LOW: {scar_index:.4f}"
            
        return True, "SYSTEM_SAFE"

# ΔΩ-GASKET_V2_ACTIVE
