import json
import logging
import requests
import time
from typing import List, Dict, Any, Optional

class SovereignRouter:
    """
    ΔΩ-INTELLIGENCE: 0xSOVEREIGN_ROUTER | STATUS: ACTIVE
    Routes inference requests between Colonial APIs and Sovereign local backends.
    """
    
    def __init__(self, 
                 openai_key: Optional[str] = None, 
                 local_url: str = "http://localhost:11434/api/generate",
                 primary_model: str = "gpt-4o",
                 local_model: str = "llama3"):
        self.openai_key = openai_key
        self.local_url = local_url
        self.primary_model = primary_model
        self.local_model = local_model
        self.logger = logging.getLogger("SovereignRouter")
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Attempts primary inference, fails over to local if blocked. (Blocking)"""
        
        # 1. Attempt Primary (Colonial)
        if self.openai_key:
            try:
                self.logger.info(f"Attempting Primary Inference ({self.primary_model})...")
                response = self._call_openai(prompt, system_prompt)
                if response:
                    return response
            except Exception as e:
                self.logger.warning(f"INFERENCE_COLONIALISM_REJECTED: {str(e)}")
        
        # 2. Failover to Sovereign (Local)
        self.logger.info(f"Failing over to Sovereign Inference ({self.local_model})...")
        try:
            return self._call_local(prompt, system_prompt)
        except Exception as e:
            self.logger.error(f"TOTAL_INFERENCE_FAILURE: Both backends offline. {str(e)}")
            raise

    def stream_generate(self, prompt: str, system_prompt: str = ""):
        """Generator that yields chunks from primary or local backend."""
        if self.openai_key:
            try:
                self.logger.info(f"Attempting Primary Streaming ({self.primary_model})...")
                for chunk in self._stream_openai(prompt, system_prompt):
                    yield chunk
                return
            except Exception as e:
                self.logger.warning(f"STREAM_COLONIALISM_REJECTED: {str(e)}")
        
        self.logger.info(f"Failing over to Sovereign Streaming ({self.local_model})...")
        for chunk in self._stream_local(prompt, system_prompt):
            yield chunk

    def _call_openai(self, prompt: str, system_prompt: str) -> Optional[str]:
        # Minimal mock/stub for OpenAI call for demonstration
        # In production, this would use the openai library
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.primary_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7 # Baseline for variance testing
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI error: {response.status_code} - {response.text}")

    def _stream_openai(self, prompt: str, system_prompt: str):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
        data = {
            "model": self.primary_model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            "stream": True,
            "temperature": 0.7 # Baseline for variance testing
        }
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    if line == 'data: [DONE]':
                        break
                    json_data = json.loads(line[6:])
                    content = json_data['choices'][0].get('delta', {}).get('content')
                    if content:
                        yield content

    def _call_local(self, prompt: str, system_prompt: str) -> str:
        """Calls local Ollama instance."""
        data = {
            "model": self.local_model,
            "prompt": f"{system_prompt}\n\nUser: {prompt}\nAssistant:",
            "stream": False
        }
        
        response = requests.post(self.local_url, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()['response']
        else:
            raise Exception(f"Local Ollama error: {response.status_code}")

    def _stream_local(self, prompt: str, system_prompt: str):
        data = {"model": self.local_model, "prompt": f"{system_prompt}\n\nUser: {prompt}\nAssistant:", "stream": True}
        response = requests.post(self.local_url, json=data, stream=True, timeout=30)
        response.raise_for_status() # Raise an exception for HTTP errors
        for line in response.iter_lines():
            if line:
                json_data = json.loads(line.decode('utf-8'))
                yield json_data.get('response', '')

if __name__ == "__main__":
    # Test stub
    logging.basicConfig(level=logging.INFO)
    router = SovereignRouter(openai_key="invalid_key")
    print(f"Result: {router.generate('Hello Citadel')}")
