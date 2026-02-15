import requests
import time
import logging
from typing import Dict, Optional

# BASE TOKEN ADDRESSES
TOKENS = {
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "CBETH": "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22"
}

class MarketOracle:
    """
    ΔΩ-SYSTEM_4: THE SENSOR ARRAY
    Fetches Kinetic Entropy (Price/Volatility) from the Real World.
    Phase I: Uses DexScreener API (Public) for Base Mainnet Data.
    """
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex/chains/base/tokens"
        self.logger = logging.getLogger("MarketOracle")
        self.cache = {}
        self.cache_ttl = 5 # seconds

    def get_market_data(self, token_symbol: str) -> Optional[Dict]:
        """
        Fetches live market data for a token on Base.
        """
        address = TOKENS.get(token_symbol)
        if not address:
            self.logger.error(f"Token {token_symbol} not mapped.")
            return None

        # Check Cache
        if token_symbol in self.cache:
            data, timestamp = self.cache[token_symbol]
            if time.time() - timestamp < self.cache_ttl:
                return data

        try:
            url = f"{self.base_url}/{address}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("pairs"):
                    # Get the most liquid pair
                    best_pair = data["pairs"][0] 
                    self.cache[token_symbol] = (best_pair, time.time())
                    return best_pair
            
            self.logger.warning(f"Oracle Fetch Failed: {response.status_code}")
            return None

        except Exception as e:
            self.logger.error(f"Oracle Error: {e}")
            return None

    def get_price(self, token_symbol: str) -> float:
        """
        Returns the current USD price of the token.
        """
        data = self.get_market_data(token_symbol)
        if data:
            return float(data.get("priceUsd", 0.0))
        return 0.0

    def get_kinetic_entropy(self, token_symbol: str) -> float:
        """
        Calculates Kinetic Entropy based on 1h and 6h price changes.
        Returns a value between 0.0 (Stable) and 1.0 (Chaos).
        """
        data = self.get_market_data(token_symbol)
        if not data:
            return 0.0
            
        try:
            # Extract Volatility Metrics
            price_change = data.get("priceChange", {})
            h1 = abs(float(price_change.get("h1", 0.0)))
            h6 = abs(float(price_change.get("h6", 0.0)))
            
            # Simple Entropy Formula for Phase I
            # High volatility (>5% move) increases entropy
            # 5% move = 0.05 * 10 = 0.5 entropy (Normalized)
            entropy = (h1 + (h6 / 6)) / 100.0 * 5.0
            
            # Clamp to [0, 1]
            return min(max(entropy, 0.0), 1.0)
            
        except Exception as e:
            self.logger.error(f"Entropy Calculation Error: {e}")
            return 0.0

if __name__ == "__main__":
    # Test the Oracle
    logging.basicConfig(level=logging.INFO)
    oracle = MarketOracle()
    price = oracle.get_price("WETH")
    entropy = oracle.get_kinetic_entropy("WETH")
    print(f"WETH Price: ${price:.2f}")
    print(f"WETH Kinetic Entropy: {entropy:.4f}")
