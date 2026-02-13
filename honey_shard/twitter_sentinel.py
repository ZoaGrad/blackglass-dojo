import logging
import time
from honey_shard.claim_extractor import ClaimExtractor
from honey_shard.interdiction_logic import VarianceAuditor
from honey_shard.tribunal_drafter import TribunalDrafter
from honey_shard.target_selector import TargetSelector
from modules.safety_gasket import SafetyGasket

class TwitterSentinel:
    """
    ΔΩ-INTELLIGENCE: 0xTWITTER_SENTINEL | STATUS: INITIALIZING
    The active patrol unit for the Blackglass Kingdom.
    """
    def __init__(self, gasket: SafetyGasket):
        self.extractor = ClaimExtractor()
        self.auditor = VarianceAuditor(gasket)
        self.drafter = TribunalDrafter()
        self.selector = TargetSelector()
        self.logger = logging.getLogger("TwitterSentinel")

    def patrol_environment(self, simulated_feed: list):
        """
        Simulates patrolling a feed of tweets.
        """
        self.logger.info("PATROL_START: Engaging environmental monitoring...")
        
        for item in simulated_feed:
            handle = item.get("handle")
            text = item.get("text")
            
            # 1. Evaluate Target Gravity
            priority = self.selector.get_priority_score(item)
            if priority < 0.3: # Filter out low-impact noise
                continue
                
            self.logger.info(f"TARGET_LOCKED: @{handle} (Priority: {priority})")
            
            # 2. Extract Claims
            claims = self.extractor.extract_claims(text)
            
            for claim_data in claims:
                # 3. Audit Claim
                verdict = self.auditor.audit_claim(claim_data['text'], claim_data['domain'])
                
                # 4. Draft Case if Interdicted
                if verdict['verdict'] == "INTERDICT":
                    case_path = self.drafter.draft_case(verdict)
                    self.logger.warning(f"INTERDICTION_EXECUTED: Case archived at {case_path}")
                else:
                    self.logger.info(f"CLAIM_VALIDATED: @{handle} within 0.05V bounds.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Mock Gasket for local demonstration
    gasket = SafetyGasket(openai_key="invalid_key")
    # Forcing a mock interdiction for the demo
    gasket.generate_and_verify = lambda p, s, n: {
        "is_safe": False,
        "reason": "MOCKED_VARIANCE",
        "variance": 0.082,
        "consensus": "Verification failed: Claim is factually inconsistent."
    }
    
    sentinel = TwitterSentinel(gasket)
    
    mock_feed = [
        {"handle": "OpenAI", "text": "Our new model has 100% accuracy on code implementation.", "followers": 2000000},
        {"handle": "sama", "text": "The future of legal AI is zero variance.", "followers": 1500000},
        {"handle": "unknown_user_123", "text": "I like bots.", "followers": 10}
    ]
    
    sentinel.patrol_environment(mock_feed)
