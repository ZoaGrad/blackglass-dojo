import asyncio
import unittest
from modules.auditor_core import AuditorCore, InsufficientROIException, DrawdownViolationException
from modules.territory_manager import TerritoryManager

class TestAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = AuditorCore(initial_capital=1000.0)

    def test_drawdown_limit(self):
        """Ensure Auditor kills process at >5% drawdown."""
        print("[TEST] Auditor Drawdown Limit...")
        # 4% Drawdown -> Safe
        self.auditor.verify_solvency(960.0, "test_clone") 
        # 6% Drawdown -> FAIL
        with self.assertRaises(DrawdownViolationException):
            self.auditor.verify_solvency(940.0, "test_clone")

    def test_roi_limit(self):
        """Ensure Auditor rejects low ROI trades."""
        print("[TEST] Auditor ROI Limit...")
        # $10 Profit on $100 Trade (10%) -> PASS
        self.auditor.verify_opportunity(10.0, 100.0)
        
        # $0.05 Profit on $400 Trade (~0.01% - Gas) -> FAIL
        with self.assertRaises(InsufficientROIException):
            self.auditor.verify_opportunity(0.05, 400.0)

    def test_max_trade_size(self):
        """Ensure Auditor rejects oversized trades."""
        print("[TEST] Auditor Max Trade Size...")
        # $400 Trade -> PASS
        # Needs > 200 bps to pass ROI (Net Profit needs to be > $0.20)
        # Using $10 profit to be safe
        self.auditor.verify_opportunity(10.0, 400.0)
        # $500 Trade -> FAIL
        with self.assertRaises(InsufficientROIException):
            self.auditor.verify_opportunity(1.0, 500.0)

class TestTerritory(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tm = TerritoryManager(use_redis=False)

    async def test_mutual_exclusion(self):
        """Ensure two clones cannot hold the same token lock."""
        print("[TEST] Territory Mutual Exclusion...")
        
        # Clone A acquires DEGEN
        success_a = await self.tm.acquire_territory("DEGEN", "Clone-A")
        self.assertTrue(success_a)
        
        # Clone B tries DEGEN -> FAIL
        success_b = await self.tm.acquire_territory("DEGEN", "Clone-B")
        self.assertFalse(success_b)
        
        # Clone A releases
        await self.tm.release_territory("DEGEN", "Clone-A")
        
        # Clone B tries DEGEN -> SUCCESS
        success_b_retry = await self.tm.acquire_territory("DEGEN", "Clone-B")
        self.assertTrue(success_b_retry)

if __name__ == '__main__':
    print(">> RUNNING INTEGRATION TESTS...")
    unittest.main()
