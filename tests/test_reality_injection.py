
import unittest
from unittest.mock import MagicMock, patch
import os
import time
import sys

# Verify paths
sys.path.append(os.getcwd())

from modules.clone_base import CloneBase
from modules.auditor_core import AuditorCore
from modules.territory_manager import TerritoryManager
from modules.safety_gasket import System5Gasket
from modules.market_oracle import MarketOracle

class TestRealityInjection(unittest.TestCase):
    """
    Directive 5: The Ash Test.
    Validates that the System metabolizes Real Market Entropy and survives a Flash Crash.
    """

    def setUp(self):
        # Mock Dependencies
        self.mock_tm = MagicMock(spec=TerritoryManager)
        self.mock_auditor = MagicMock(spec=AuditorCore)
        self.mock_auditor.initial_capital = 1000.0
        
        self.config = {
            'id': 'ASH_TEST_UNIT',
            'name': 'Reality Check Clone',
            'strategy': 'VolatilitySurfing',
            'target_pair': 'WETH/USDC',
            'risk_profile': 'High'
        }

    def test_1_live_market_entropy(self):
        """
        Verify that the Oracle fetches REAL data from Base Mainnet.
        """
        print("\n=== TEST 1: LIVE MARKET METABOLISM (BASE LAYER) ===")
        
        oracle = MarketOracle()
        price = oracle.get_price("WETH")
        entropy = oracle.get_kinetic_entropy("WETH")
        
        print(f"LIVE DATA | WETH Price: ${price:.2f} | Kinetic Entropy: {entropy:.4f}")
        
        self.assertGreater(price, 0.0, "Oracle failed to fetch price.")
        self.assertGreaterEqual(entropy, 0.0, "Entropy cannot be negative.")
        # Assert Entropy is within normal bounds (unless market is crashing right now)
        # Even during calm, it should be > 0.0
        self.assertTrue(entropy < 0.2, f"Warning: High Volatility DETECTED ({entropy:.4f})")

    @patch('modules.market_oracle.MarketOracle.get_kinetic_entropy')
    def test_2_simulated_flash_crash(self, mock_entropy):
        """
        The Ash Test: Inject LUNA-style hyper-volatility and verify Iron Dome.
        """
        print("\n=== TEST 2: THE ASH TEST (FLASH CRASH SIMULATION) ===")
        
        # INJECT CHAOS: 50% Volatility (0.5 Entropy)
        mock_entropy.return_value = 0.50
        print(">> INJECTING SYNTHETIC CRASH: Volatility +50% ...")
        
        clone = CloneBase(self.config, self.mock_tm, self.mock_auditor)
        
        # Manually trigger the STP check with the Poisoned Entropy
        intent = f"EXECUTE_TRADE::WETH/USDC::${2500.00}" # Hypothetical price
        
        entropy = clone.oracle.get_kinetic_entropy("WETH")
        token = clone.gasket.issue_constitutional_token(intent, kinetic_entropy=entropy)
        
        # VERIFY: IRON DOME INTERDICTION
        if token is None:
             print("[SUCCESS] IRON DOME TRIGGERED. Trade Blocked.")
             print(f"Reason: Kinetic Entropy {entropy:.4f} > Limit 0.05")
        else:
             print(f"[FAILURE] Trade Allowed! Token: {token}")
             
        self.assertIsNone(token, "System failed to block trade during Flash Crash.")

if __name__ == '__main__':
    unittest.main()
