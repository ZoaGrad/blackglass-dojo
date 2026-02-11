import asyncio
from typing import Dict, Optional

class TerritoryManager:
    """
    The 'Inhibitor Chip' module.
    Prevents fratricide by enforcing Mutual Exclusion (Mutex) on target assets.
    """
    def __init__(self, use_redis: bool = False):
        self.use_redis = use_redis
        self.local_locks: Dict[str, asyncio.Lock] = {}
        # self.redis_client = redis.Redis(...) if use_redis else None

    async def acquire_territory(self, token_address: str, clone_id: str) -> bool:
        """
        Attempts to acquire the lock for a specific token.
        Non-blocking: Returns False immediately if occupied.
        """
        token_key = token_address.lower()

        if self.use_redis:
            # Placeholder for Distributed Logic (Phase 2)
            # return self.redis_client.set(f"lock:{token_key}", clone_id, nx=True, px=5000)
            pass

        # Local Logic (Phase 1)
        if token_key not in self.local_locks:
            self.local_locks[token_key] = asyncio.Lock()
        
        lock = self.local_locks[token_key]
        
        if lock.locked():
            # In a real mutex, this might block, but for trading usually we skip if busy
            # to avoid stale quotes.
            return False
            
        await lock.acquire()
        print(f"[{clone_id}] Acquired Territory: {token_key}")
        return True

    async def release_territory(self, token_address: str, clone_id: str):
        """
        Releases the lock for a specific token.
        """
        token_key = token_address.lower()
        
        if self.use_redis:
            # Redis Release Logic
            pass

        # Local Logic
        if token_key in self.local_locks:
            if self.local_locks[token_key].locked():
                self.local_locks[token_key].release()
                print(f"[{clone_id}] Released Territory: {token_key}")
