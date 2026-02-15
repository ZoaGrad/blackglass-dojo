import sys
import os
import yaml
import subprocess
from datetime import datetime

from dotenv import load_dotenv

# ZOAGRAD RESEARCH BRIDGE
# Bridges the SpiralOS environment to the AutoLLM/ArxivDigest tool.

ARXIV_ROOT = r"C:\Users\colem\Code\ArxivDigest"
CONFIG_FILE = r"C:\Users\colem\Code\ArxivDigest\config_zoagrad.yaml"
OUTPUT_DIR = r"C:\Users\colem\Code\blackglass-shard-alpha\data\research_digests"
DOTENV_PATH = r"C:\Users\colem\Code\blackglass-shard-alpha\.env"

def run_digest():
    print(f"[*] Initiating High-Frequency Research Digest...")
    print(f"[*] Configuration: {CONFIG_FILE}")
    
    # Load Environment
    load_dotenv(DOTENV_PATH)
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in .env")

    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Construct command to run action.py with the custom config
    # We must run it from the ArxivDigest root so relative paths work
    cmd = [
        sys.executable,
        os.path.join(ARXIV_ROOT, "src", "action.py"),
        "--config", CONFIG_FILE
    ]
    
    env = os.environ.copy()
    # Add src to PYTHONPATH so imports work
    env["PYTHONPATH"] = os.path.join(ARXIV_ROOT, "src") + os.pathsep + env.get("PYTHONPATH", "")
    
    try:
        # Run the process
        result = subprocess.run(cmd, cwd=ARXIV_ROOT, env=env, capture_output=True, text=True)
        
        print("[*] STDOUT:", result.stdout)
        if result.returncode != 0:
            print("[!] STDERR:", result.stderr)
            raise RuntimeError("ArxivDigest execution failed.")
            
        print("[*] Digest Cycle Complete.")
        
        # Check for output (ArxivDigest writes to 'digest.html' in CWD by default)
        default_output = os.path.join(ARXIV_ROOT, "digest.html")
        if os.path.exists(default_output):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_path = os.path.join(OUTPUT_DIR, f"zoagrad_digest_{timestamp}.html")
            os.rename(default_output, new_path)
            print(f"[+] Digest Artifact Secured: {new_path}")
            return new_path
        else:
            print("[!] Warning: No 'digest.html' found. Research yield may be zero.")
            return None

    except Exception as e:
        print(f"[!] Critical Bridge Failure: {e}")
        return None

if __name__ == "__main__":
    digest_path = run_digest()
    if digest_path:
        print(f"[*] INSTRUCTION: Upload {digest_path} to NotebookLM Brain.")
