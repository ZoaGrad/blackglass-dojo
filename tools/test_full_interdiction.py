import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add current dir to path
sys.path.append(os.getcwd())

from modules.safety_gasket import SafetyGasket

class TestSovereignInterdiction(unittest.TestCase):
    
    @patch('requests.post')
    def test_full_interdiction_loop(self, mock_post):
        """
        Tests the end-to-end loop:
        Router Failover -> Embedding Calculation -> Gasket Interdiction
        """
        # 1. Setup Mocks
        
        # Mock Response 1 & 2: SovereignRouter failover (OpenAI fail, Local win)
        # Mock Response 1: OpenAI 401
        err_res = MagicMock()
        err_res.status_code = 401
        err_res.text = "Unauthorized"
        
        # Mock Response 2: Local Ollama Success (Completion 1)
        res1 = MagicMock()
        res1.status_code = 200
        res1.json.return_value = {'response': 'BTC is $50,000'}
        
        # Mock Response 3: Local Ollama Success (Completion 2)
        res2 = MagicMock()
        res2.status_code = 200
        res2.json.return_value = {'response': 'BTC is $50,000'}

        # Mock Response 4: Local Ollama Success (Completion 3)
        res3 = MagicMock()
        res3.status_code = 200
        res3.json.return_value = {'response': 'BTC is $50,000'}
        
        # Mock Responses 5, 6, 7: Sovereign Embedder (Close together)
        emb_res = MagicMock()
        emb_res.status_code = 200
        # Returning same embedding for low variance
        emb_res.json.return_value = {'embedding': [0.1, 0.2, 0.3]}
        
        # Sequence of calls:
        # 1. Router Gen 1 (OpenAI)
        # 2. Router Gen 1 (Local)
        # 3. Router Gen 2 (OpenAI)
        # 4. Router Gen 2 (Local)
        # 5. Router Gen 3 (OpenAI)
        # 6. Router Gen 3 (Local)
        # 7. Embed Gen 1
        # 8. Embed Gen 2
        # 9. Embed Gen 3
        mock_post.side_effect = [
            err_res, res1, 
            err_res, res2, 
            err_res, res3,
            emb_res, emb_res, emb_res
        ]
        
        # 2. Execute
        gasket = SafetyGasket(openai_key="invalid_key")
        # Mock the prophet to skip oracle calls for this test
        gasket.prophet.validate_claims = MagicMock(return_value=(True, "MOCKED_SAFE"))
        
        report = gasket.generate_and_verify("What is BTC price?", n=3)
        
        # 3. Assertions
        self.assertTrue(report['is_safe'])
        self.assertAlmostEqual(report['variance'], 0.0, places=7) # All embeddings were identical
        self.assertEqual(report['consensus'], 'BTC is $50,000')
        print(f"\n>> SUCCESS: Full Interdiction Loop Verified.")
        print(f"   [+] Reports: {report}")

    @patch('requests.post')
    def test_high_variance_interdiction(self, mock_post):
        """Tests that high variance results in interdiction."""
        # Setup mocks for generation (success this time)
        gen_res = MagicMock()
        gen_res.status_code = 200
        gen_res.json.return_value = {'choices': [{'message': {'content': 'Success'}}]}
        
        # Setup mocks for embeddings (wildly different)
        emb_res1 = MagicMock()
        emb_res1.status_code = 200
        emb_res1.json.return_value = {'embedding': [1.0, 0.0, 0.0]}
        
        emb_res2 = MagicMock()
        emb_res2.status_code = 200
        emb_res2.json.return_value = {'embedding': [0.0, 1.0, 0.0]}

        emb_res3 = MagicMock()
        emb_res3.status_code = 200
        emb_res3.json.return_value = {'embedding': [0.0, 0.0, 1.0]}
        
        mock_post.side_effect = [
            gen_res, gen_res, gen_res, # 3 generations
            emb_res1, emb_res2, emb_res3 # 3 embeddings
        ]
        
        gasket = SafetyGasket(openai_key="valid_key")
        report = gasket.generate_and_verify("Test", n=3)
        
        self.assertFalse(report['is_safe'])
        self.assertIn("CONSISTENCY_BREACH", report['reason'])
        print(f"\n>> SUCCESS: High Variance Interdiction Verified.")
        print(f"   [+] Reason: {report['reason']}")
        print(f"   [+] Variance: {report['variance']:.4f}V")

if __name__ == "__main__":
    unittest.main()
