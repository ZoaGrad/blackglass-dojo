import asyncio
import os
import sys

# Add current dir to path to ensure modules are found
sys.path.append(os.getcwd())

from modules.swarm_factory import SwarmFactory

if __name__ == "__main__":
    banner = """
    ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗
    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║
    ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║
    ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║
    ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
    ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
             OPERATION PERFECT CELL
    """
    print(banner)
    
    manifest_path = "config/swarm_manifest.json"
    
    if not os.path.exists(manifest_path):
        print(f"ERROR: Manifest not found at {manifest_path}")
        sys.exit(1)
        
    print(">> [SYSTEM] INITIALIZING SWARM PROTOCOL...")
    factory = SwarmFactory(manifest_path)
    factory.load_manifest()
    
    try:
        print(">> [SYSTEM] IGNITING MAIN THRUSTERS (Ctrl+C to abort)...")
        asyncio.run(factory.ignite())
    except KeyboardInterrupt:
        print("\n>> [SYSTEM] MANUAL OVERRIDE. SHUTTING DOWN.")
