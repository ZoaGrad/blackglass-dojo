
import unittest
from unittest.mock import MagicMock, patch
import os
import time

# Verify paths (Hack for VSCode/Terminal path differences)
import sys
sys.path.append(os.getcwd())

from modules.clone_base import CloneBase
from modules.auditor_core import AuditorCore
from modules.territory_manager import TerritoryManager
from modules.safety_gasket import System5Gasket

class TestSovereignTransactionProtocol(unittest.TestCase):
    """
    Validates the 'Iron Wire' between System 5 and System 3.
    """

    def setUp(self):
        # Mock Dependencies
        self.mock_tm = MagicMock(spec=TerritoryManager)
        self.mock_auditor = MagicMock(spec=AuditorCore)
        self.mock_auditor.initial_capital = 1000.0
        
        # Config for Clone
        self.config = {
            'id': 'TEST_CLONE_01',
            'name': 'Unit Test Clone',
            'strategy': 'Arbitrage',
            'target_pair': 'BTC/USDC',
            'risk_profile': 'Low'
        }

    def test_1_normal_execution_with_token(self):
        """
        Verify that a valid token ALLOWS execution.
        """
        print("\n=== TEST 1: STP NORMAL EXECUTION ===")
        
        # Initialize Clone
        clone = CloneBase(self.config, self.mock_tm, self.mock_auditor)
        
        # Mock Gasket internals to ensure health
        clone.gasket.current_scar_index = 1.0
        clone.gasket.is_locked = False
        
        # Perform the Token Issue call manually to verify format
        token = clone.gasket.issue_constitutional_token("TEST_INTENT")
        self.assertIsNotNone(token)
        self.assertIn("17TJ5", token) # CAGE Code check
        print(f"Token Issued: {token}")

    def test_2_iron_dome_veto(self):
        """
        Verify that Low ScarIndex BLOCKS execution.
        """
        print("\n=== TEST 2: IRON DOME VETO ===")
        
        clone = CloneBase(self.config, self.mock_tm, self.mock_auditor)
        
        # POISON THE WELL: Set ScarIndex below threshold
        clone.gasket.current_scar_index = 0.85 # < 0.997
        
        # Attempt Token Issue
        token = clone.gasket.issue_constitutional_token("TEST_INTENT")
        self.assertIsNone(token)
        print("Token Denied (ScarIndex Low).")

    def test_3_system_lockout(self):
        """
        Verify that Lockout File BLOCKS execution.
        """
        print("\n=== TEST 3: LOCKOUT STATE ===")
        
        clone = CloneBase(self.config, self.mock_tm, self.mock_auditor)
        
        # FORCE LOCKOUT
        clone.gasket.is_locked = True
        
        # Attempt Token Issue
        token = clone.gasket.issue_constitutional_token("TEST_INTENT")
        self.assertIsNone(token)
        print("Token Denied (System Locked).")

if __name__ == '__main__':
    unittest.main()
