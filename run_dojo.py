import os
import sys
import time
import argparse

# Add current dir to path
sys.path.append(os.getcwd())

from modules.recorder import DojoRecorder
from modules.accelerator import DojoAccelerator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blackglass Dojo Simulation")
    parser.add_argument("--inject-variance", type=float, default=0.0, help="Inject semantic variance (e.g., 0.08)")
    args = parser.parse_args()

    banner = """
    ██████╗  ██████╗      ██╗ ██████╗ 
    ██╔══██╗██╔═══██╗     ██║██╔═══██╗
    ██║  ██║██║   ██║     ██║██║   ██║
    ██║  ██║██║   ██║██   ██║██║   ██║
    ██████╔╝╚██████╔╝╚█████╔╝╚██████╔╝
    ╚═════╝  ╚═════╝  ╚════╝  ╚═════╝ 
          SHADOW SIMULATION
    """
    print(banner)
    
    tape_path = "data/dojo_tape_v1.json"
    
    # 1. Record (Skip recording for speed if tape exists)
    if not os.path.exists(tape_path):
        print("\n[PHASE 1] RECORDING LIVE DATA...")
        recorder = DojoRecorder("https://mainnet.base.org") 
        recorder.record_live_session(duration_seconds=2, output_file=tape_path)
    
    # 2. Replay
    print(f"\n[PHASE 2] ACCELERATING TIME (Variance Injection: {args.inject_variance}V)")
    print(f">> Injecting {tape_path} into Swarm Matrix...")
    accelerator = DojoAccelerator(tape_path, injected_variance=args.inject_variance)
    accelerator.run_replay()
