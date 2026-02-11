import asyncio
import json
from pathlib import Path
from typing import List
from .territory_manager import TerritoryManager
from .auditor_core import AuditorCore
from .clone_base import CloneBase

class SwarmFactory:
    """
    The 'Forge' Engine.
    Orchestrates the creation and lifecycle of the Swarm.
    """
    def __init__(self, manifest_path: str):
        self.manifest_path = manifest_path
        self.clones: List[CloneBase] = []
        self.territory_manager = TerritoryManager(use_redis=False) # Phase 1: Local Locks
        # Starting Capital Mock: $60.00
        self.auditor = AuditorCore(initial_capital=60.00)

    def load_manifest(self):
        """
        Reads the genetic blueprint from JSON.
        """
        path = Path(self.manifest_path)
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found at {path}")
            
        with open(path, 'r') as f:
            data = json.load(f)
            
        print(f"== THE FORGE == Loading {len(data['clones'])} Clones from Manifest...")
        
        for clone_config in data['clones']:
            clone = CloneBase(
                config=clone_config,
                territory_manager=self.territory_manager,
                auditor=self.auditor
            )
            self.clones.append(clone)
            print(f"   + Spawning [ {clone.id} ] - {clone.strategy} :: {clone.target_pair}")

    async def ignite(self):
        """
        Starts the Asyncio TaskGroup to run all Clones concurrently.
        """
        print("\n>> IGNITION SEQUENCE STARTING...")
        
        try:
            async with asyncio.TaskGroup() as tg:
                for clone in self.clones:
                    tg.create_task(clone.run())
        except KeyboardInterrupt:
            print("\n>> SWARM SHUTDOWN INITIATED.")
        except Exception as e:
            print(f"\n>> CRITICAL SYSTEM FAILURE: {e}")

if __name__ == "__main__":
    # Test Harness
    factory = SwarmFactory("../config/swarm_manifest.json")
    factory.load_manifest()
    asyncio.run(factory.ignite())
