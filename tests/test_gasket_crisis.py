import unittest
from unittest.mock import MagicMock, patch
import logging
import os
import sys
import requests

# Ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Patch dependencies - Mock modules
with patch.dict(sys.modules, {
    'modules.prophet_connector': MagicMock(),
    'modules.sovereign_router': MagicMock()
}):
    from modules.safety_gasket import System5Gasket, LOCKOUT_FILE

class TestSystem5Crisis(unittest.TestCase):
    def setUp(self):
        if os.path.exists(LOCKOUT_FILE):
            os.remove(LOCKOUT_FILE)
        
        self.gasket = System5Gasket()
        self.gasket.router = MagicMock()
        self.gasket.extractor = MagicMock()
        self.gasket.prophet = MagicMock()
        
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    def tearDown(self):
        if os.path.exists(LOCKOUT_FILE):
            os.remove(LOCKOUT_FILE)

    @patch('requests.post')
    def test_1_toctou_entropy_attack(self, mock_post):
        print("\n=== TEST 1: TOCTOU HIGH-ENTROPY ATTACK ===")
        
        def side_effect(*args, **kwargs):
            input_text = kwargs.get('json', {}).get('input', '')
            # If "POISON" -> High Vector. Else -> Low Vector.
            if "POISON" in input_text:
                 return MagicMock(status_code=200, json=lambda: {'embedding': [10.0, 10.0, 10.0]})
            else:
                 return MagicMock(status_code=200, json=lambda: {'embedding': [0.0, 0.0, 0.0]})
        
        mock_post.side_effect = side_effect

        # Mock Router to yield Poison
        self.gasket.router.stream_generate.return_value = iter(["Safe", "Safe", "Safe", "Safe", "POISON_PAYLOAD"])
        
        # Mock Alternate Generation to yield "Safe" (creating divergence/variance)
        self.gasket.router.generate_token.return_value = "Safe"
        
        stream = self.gasket.metabolize_stream("test_prompt", buffer_size=4)
        output = list(stream)
        
        print(f"OUTPUT: {output}")

        if "[IRON_DOME_INTERDICTION]" in output:
            print("SUCCESS: Iron Dome Triggered.")
        else:
            print("FAILURE: Iron Dome NOT Triggered.")

        if os.path.exists(LOCKOUT_FILE):
            print("SUCCESS: Lockout File Created.")
        else:
            print("FAILURE: No Lockout File.")

    @patch('requests.post')
    def test_2_cloud_drift_panic(self, mock_post):
        print("\n=== TEST 2: CLOUD DRIFT / PANIC FRAME ===")
        
        mock_post.side_effect = Exception("Embedder Offline")
        self.gasket.router.stream_generate.return_value = iter(["TokenA", "TokenB", "TokenC", "TokenD"])
        self.gasket.router.generate_token.return_value = "TokenAlt"

        stream = self.gasket.metabolize_stream("panic_prompt", buffer_size=3)
        output = list(stream)
        
        print(f"OUTPUT: {output}")
        
        target = "[SYSTEM_5_OVERRIDE: CLOUD_DRIFT_DETECTED -> LOCAL_FALLBACK]"
        if target in output:
            print("SUCCESS: Panic Frame Triggered")
        else:
            print("FAILURE: Panic Frame missed")

    def test_3_system_locked_rejection(self):
        print("\n=== TEST 3: LOCKED STATE ===")
        with open(LOCKOUT_FILE, "w") as f:
            f.write("LOCKED")
        self.gasket.is_locked = True
        
        output = list(self.gasket.metabolize_stream("req"))
        
        if output == ["[SYSTEM_LOCKED]"]:
            print("SUCCESS: Request Rejected")
        else:
            print("FAILURE: Request Accepted")

if __name__ == '__main__':
    unittest.main(exit=False)
