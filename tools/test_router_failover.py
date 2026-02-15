import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add current dir to path
sys.path.append(os.getcwd())

from modules.sovereign_router import SovereignRouter

class TestSovereignRouter(unittest.TestCase):
    
    @patch('requests.post')
    def test_primary_success(self, mock_post):
        """Test that primary (OpenAI) is called when key is valid."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Colonial Response'}}]
        }
        mock_post.return_value = mock_response
        
        router = SovereignRouter(openai_key="valid_key")
        result = router.generate("Test Prompt")
        
        self.assertEqual(result, "Colonial Response")
        # Ensure only 1 call was made (to OpenAI)
        self.assertEqual(mock_post.call_count, 1)

    @patch('requests.post')
    def test_failover_on_error(self, mock_post):
        """Test that it fails over to local when OpenAI returns an error."""
        # 1. First call (OpenAI) returns 401
        mock_openai_err = MagicMock()
        mock_openai_err.status_code = 401
        mock_openai_err.text = "Unauthorized"
        
        # 2. Second call (Local) returns 200
        mock_local_res = MagicMock()
        mock_local_res.status_code = 200
        mock_local_res.json.return_value = {'response': 'Sovereign Response'}
        
        mock_post.side_effect = [mock_openai_err, mock_local_res]
        
        router = SovereignRouter(openai_key="invalid_key")
        result = router.generate("Test Prompt")
        
        self.assertEqual(result, "Sovereign Response")
        # Ensure 2 calls were made
        self.assertEqual(mock_post.call_count, 2)

    @patch('requests.post')
    def test_failover_on_exception(self, mock_post):
        """Test that it fails over to local when OpenAI call raises an exception."""
        # 1. First call (OpenAI) raises exception
        # 2. Second call (Local) returns 200
        mock_local_res = MagicMock()
        mock_local_res.status_code = 200
        mock_local_res.json.return_value = {'response': 'Sovereign Response'}
        
        mock_post.side_effect = [Exception("Network Error"), mock_local_res]
        
        router = SovereignRouter(openai_key="key")
        result = router.generate("Test Prompt")
        
        self.assertEqual(result, "Sovereign Response")
        self.assertEqual(mock_post.call_count, 2)

if __name__ == "__main__":
    unittest.main()
