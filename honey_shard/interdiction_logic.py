import logging
from modules.safety_gasket import SafetyGasket

class VarianceAuditor:
    """
    ΔΩ-INTELLIGENCE: 0xVARIANCE_AUDITOR | STATUS: LAW_ENFORCEMENT
    The automated judge for the 0.05V Standard.
    """
    def __init__(self, gasket: SafetyGasket, review_threshold: float = 0.05):
        self.gasket = gasket
        self.review_threshold = review_threshold
        self.logger = logging.getLogger("VarianceAuditor")

    def audit_claim(self, claim: str, domain: str = "general") -> dict:
        """
        Runs a claim through the 0.05V Gasket and returns a verdict.
        """
        self.logger.info(f"AUDITING CLAIM: [{domain}] {claim[:50]}...")
        
        # 1. Execute Parallel Analysis via Gasket/Router
        # We prompt the system to verify the claim n times
        prompt = f"Verify this claim for technical accuracy: '{claim}'"
        system_prompt = f"You are a specialized verification oracle for the {domain} domain. Be extremely precise."
        
        report = self.gasket.generate_and_verify(prompt, system_prompt, n=3)
        
        # 2. Determine Action
        v_score = report['variance']
        interdict = False
        priority = "LOW"

        if v_score > self.review_threshold:
            interdict = True
            if v_score > 0.10:
                priority = "CRITICAL_SYSTEM_FAILURE"
            else:
                priority = "PRECISION_BREACH"

        return {
            "verdict": "INTERDICT" if interdict else "VALID",
            "variance": v_score,
            "priority": priority,
            "reason": report['reason'],
            "evidence": report['consensus'],
            "claim": claim,
            "domain": domain
        }

# ΔΩ-AUDITOR_ARMED
