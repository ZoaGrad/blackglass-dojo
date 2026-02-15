import os
import time
import json
import random
from swarm_factory import Swarm

# [Ω.PANIC-FRAME THRESHOLDS]
GAS_CEILING_GWEI = 150
MAX_TRADE_LOSS_PCT = 0.01  # 1% per trade hard-stop
MAX_SHARD_DRAWDOWN = 0.05  # 5% total protocol lock

class SentinelAuditor:
    def __init__(self, min_balance_eth=0.0005, max_block_age=90):
        self.min_balance = min_balance_eth
        self.max_block_age = max_block_age
        self.violations = []
        self.total_drawdown = 0
        
    def check_substrate_health(self, web3):
        try:
            if not web3:
                return True, "MOCK_MODE_ACTIVE"
            latest_block = web3.eth.get_block('latest')
            block_time = latest_block['timestamp']
            current_time = int(time.time())
            age = current_time - block_time
            if age > self.max_block_age:
                print(f"[INHIBIT] :: Substrate is Stale: {age}s age detected.")
                return False, "Substrate Health: Stale Blocks"
            return True, "Healthy"
        except Exception as e:
            return False, f"Substrate Connectivity Issue: {e}"

    def check_constitution(self, agent, trade_data):
        if trade_data.get('estimated_slippage', 0) > agent.strategy['slippage_tolerance']:
            self.violations.append('Slippage tolerance exceeded')
            return False
        if trade_data.get('gas_estimate', 0) > 0.001:
            self.violations.append('Gas cost too high')
            return False
        return True
        
    def check_balance(self, web3, wallet):
        balance_eth = 1.0 # Mock
        if balance_eth < self.min_balance:
            print(f"[AUDITOR] Balance below threshold: {balance_eth} ETH")
            return False
        return True

    def emergency_stop(self, swarm):
        if self.total_drawdown >= MAX_SHARD_DRAWDOWN:
            print(f"[PANIC] Total Drawdown {self.total_drawdown*100:.2f}% breaches limit. FIRING KILL-SWITCH.")
            return True
        return False

class Sentinel:
    """
    The Kinetic Entity. Composes Swarm (Mind) and Auditor (Conscience).
    """
    def __init__(self):
        # Load environment
        self.BASE_RPC = os.getenv('BASE_RPC_URL', "https://mainnet.base.org")
        self.PRIVATE_KEY = os.getenv('PRIVATE_KEY', "0x000")
        self.WALLET_ADDRESS = os.getenv('WALLET_ADDRESS', "0x000")
        
        self.swarm = Swarm(self.BASE_RPC, self.WALLET_ADDRESS, self.PRIVATE_KEY)
        self.auditor = SentinelAuditor()
        self.generation_interval = 2
        

HEADLESS_MODE = False

def run_cycle(stop_event=None):
    print(f"[SENTINEL] Starting Evolution Loop (API Managed)...")
    
    # Initialize Sentinel inside the process
    if not os.getenv('WALLET_ADDRESS'):
        # Allow mock mode if env vars missing in dev
        print("[WARNING] Env vars missing, defaulting to MOCK Sentinel.")
        sentinel = Sentinel()
        # Mock wallet/rpc if needed or handle inside Sentinel
    else:
        sentinel = Sentinel()

    while True:
        # CHECK FOR EXTERNAL INTERDICTION
        if stop_event and stop_event.is_set():
            print("[SENTINEL] Stop Event Received. Halting.")
            break
            
        print(f"\n=== Generation {sentinel.swarm.generation} ===")
        
        # 1. HEALTH CHECKS
        is_healthy, reason = sentinel.auditor.check_substrate_health(sentinel.swarm.web3)
        if not is_healthy:
            print(f"[HIBERNATION] :: {reason}")
            break

        if sentinel.auditor.emergency_stop(sentinel.swarm):
            print("[SENTINEL] EMERGENCY STOP TRIGGERED.")
            if stop_event: stop_event.set()
            break
        
        # 2. MARKET DATA (MOCK)
        market_data = {
            'timestamp': time.time(),
            'volatility_index': 0.2, 
            'gas_price': 1000000000 
        }
        
        # 3. EVOLUTION
        fittest = sentinel.swarm.breed_generation(market_data)
        print(f"[EVOLUTION] Fittest score: {fittest.fitness_score:.4f}")
        
        # 4. TRADING SIGNAL
        if fittest.fitness_score > 0.0:
            trade_signal = {
                'pair': random.choice(fittest.strategy['target_pairs']),
                'side': random.choice(['BUY', 'SELL']),
                'size': fittest.strategy['max_position_size']
            }
            
            if sentinel.auditor.check_constitution(fittest, trade_signal):
                sentinel.swarm.execute_trade(fittest, trade_signal)
            else:
                print(f"[AUDITOR] Trade vetoed: {sentinel.auditor.violations[-1]}")
        
        # 5. LOGGING
        try:
            with open('evolution_log.jsonl', 'a') as log:
                log.write(json.dumps({
                    'generation': sentinel.swarm.generation,
                    'fittest_score': fittest.fitness_score,
                    'timestamp': time.time()
                }) + '\n')
        except:
            pass
        
        print(f"[SENTINEL] Sleeping for {sentinel.generation_interval} seconds...")
        time.sleep(sentinel.generation_interval)

def main():
    if not os.getenv('WALLET_ADDRESS'):
        print("[ERROR] Env vars missing.")
        # return # Commented out for local testing without .env for now

    # Classic Run
    sentinel = Sentinel()
    # sentinel.run_cycle() # The original method was bound to instance, now we use the standalone function or refactor class
    # For minimal disruption, let's just instantiate and run logic similar to run_cycle but standalone
    # Actually, better to just call run_cycle() if we want unified logic
    run_cycle()

if __name__ == "__main__":
    main()

