# Logic Shard: Prophet Connector (Stream B)
## ΔΩ-INTELLIGENCE: 0xPROPHET_CONNECT | STATUS: LOGIC_FINALIZED

import re

class ProphetExtractor:
    """
    Extracts high-stakes factual claims (Prices, Addresses) from LLM output.
    """
    def __init__(self):
        # Patterns for Prices ($X.XX) and Contract Addresses (0x...)
        self.price_pattern = re.compile(r'\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)')
        self.addr_pattern = re.compile(r'0x[a-fA-F0-9]{40}')

    def extract_claims(self, text: str):
        prices = self.price_pattern.findall(text)
        addresses = self.addr_pattern.findall(text)
        return {
            "prices": [float(p.replace(',', '')) for p in prices],
            "addresses": addresses
        }

class CrossCheckProphet:
    """
    Validates extracted claims against deterministic Oracles.
    """
    def __init__(self, oracle_client=None):
        self.oracle = oracle_client
        self.semantic_threshold = 0.05
        self.financial_threshold = 0.01 # 1% for Prices

    def validate_claims(self, claims: dict):
        if not claims['prices'] and not claims['addresses']:
            return True, "NO_CLAIMS_TO_CHECK"

        if not self.oracle:
            return True, "ORACLE_BYPASS"

        for price in claims['prices']:
            oracle_price = self.oracle.get_current_price('ETH/USDT') 
            
            if oracle_price is None:
                return False, f"ORACLE_BLIND_SPOT: Oracle cannot verify claim ${price}"
                
            drift = abs(price - oracle_price) / oracle_price
            
            # Use Financial Threshold for prices
            if drift > self.financial_threshold:
                return False, f"FACTUAL_DRIFT: LLM reported ${price}, Oracle reports ${oracle_price} ({drift:.2%} error)"
        
        return True, "FACT_VALIDATED"
