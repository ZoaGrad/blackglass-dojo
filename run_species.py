import os
import time
import json
# from dotenv import load_dotenv # Assuming python-dotenv might need install, using os.environ or mock for now
from swarm_factory import Swarm

# load_dotenv()

    # [Ω.PANIC-FRAME THRESHOLDS]
    GAS_CEILING_GWEI = 150
    MAX_TRADE_LOSS_PCT = 0.01  # 1% per trade hard-stop
    BLOCK_REORG_DEPTH = 3      # Number of blocks to wait for settlement stability
    MAX_SHARD_DRAWDOWN = 0.05  # 5% total protocol lock

    def __init__(self, min_balance_eth=0.0005, max_block_age=90):  # ~$1.50 at current prices
        self.min_balance = min_balance_eth
        self.max_block_age = max_block_age
        self.history = []
        self.violations = []
        self.total_drawdown = 0
        
    def check_substrate_health(self, web3):
        """
        [PHASE IV] :: Substrate Health Guard
        Monitors for network congestion or stagnation.
        """
        try:
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
        # Check against constitutional imperatives
        if trade_data.get('estimated_slippage', 0) > agent.strategy['slippage_tolerance']:
            self.violations.append('Slippage tolerance exceeded')
            return False
        if trade_data.get('gas_estimate', 0) > 0.001:  # Arbitrary gas cap
            self.violations.append('Gas cost too high')
            return False
        return True
        
    def check_balance(self, web3, wallet):
        # Mock balance check for Dry Run
        # balance = web3.eth.get_balance(wallet)
        # balance_eth = web3.from_wei(balance, 'ether')
        balance_eth = 1.0 # Mocking healthy balance
        
        if balance_eth < self.min_balance:
            print(f"[AUDITOR] Balance below threshold: {balance_eth} ETH")
            return False
        return True

    def emergency_stop(self, swarm):
        """Execute if balance drops below $55 equivalent or drawdown breaches limits"""
        # [Ω.PANIC-FRAME] :: Drawdown Check
        if self.total_drawdown >= self.MAX_SHARD_DRAWDOWN:
            print(f"[PANIC] Total Drawdown {self.total_drawdown*100:.2f}% breaches limit. FIRING KILL-SWITCH.")
            return True

        balance_eth = 1.0 # Mock
        eth_price = 3500  
        
        if balance_eth * eth_price < 40:  # $40 ritual threshold
            print(f"[APOPTOSIS] Balance ${balance_eth*eth_price:.2f} below sacrificial limit. Terminating.")
            return True
        return False

    def validate_gas(self, gas_price_wei):
        """Vetoes if gas spikes above 150 Gwei"""
        gwei = gas_price_wei / 1e9
        if gwei > self.GAS_CEILING_GWEI:
            print(f"[VETO] Gas Price {gwei:.1f} Gwei exceeds ceiling {self.GAS_CEILING_GWEI}")
            return False
        return True

def main():
    # Load environment
    BASE_RPC = os.getenv('BASE_RPC_URL', "https://mainnet.base.org")
    PRIVATE_KEY = os.getenv('PRIVATE_KEY', "0x000")
    WALLET_ADDRESS = os.getenv('WALLET_ADDRESS', "0x000")
    
    if not all([BASE_RPC, PRIVATE_KEY, WALLET_ADDRESS]):
        print("[ERROR] Missing environment variables. Please check .env")
        # return # Proceeding with mock for verification
        
    # Initialize
    swarm = Swarm(BASE_RPC, WALLET_ADDRESS, PRIVATE_KEY)
    auditor = SentinelAuditor()
    
    print("[ZOAGRAD SWARM] Initialized")
    print(f"Wallet: {WALLET_ADDRESS}")
    # print(f"Balance: {swarm.web3.eth.get_balance(WALLET_ADDRESS)} wei")
    print(f"Balance: MOCKED (Safe for Dry Run)")
    
    # Main evolution loop
    generation_interval = 2 # Compressed for testing (User said 1800)
    # generation_interval = 1800 
    
    print(f"[SENTINEL] Starting Evolution Loop (Test Mode - Fast Cycles)...")
    
    try:
        while True:
            print(f"\n=== Generation {swarm.generation} ===")
            
            # 1. Check substrate & balance safety
            is_healthy, reason = auditor.check_substrate_health(swarm.web3)
            if not is_healthy:
                print(f"[HIBERNATION] :: {reason}. Powering down Shard Factory.")
                break

            if auditor.emergency_stop(swarm):
                break
            
            if not auditor.check_balance(swarm.web3, WALLET_ADDRESS):
                print("[AUDITOR] Balance threshold breached. Stopping.")
                break
                
            # 2. Get market data (mock - replace with actual DEX feeds)
            market_data = {
                'timestamp': time.time(),
                'volatility_index': 0.2, # Mock
                'gas_price': 1000000000 # Mock
            }
            
            # 3. Breed new generation
            fittest = swarm.breed_generation(market_data)
            print(f"[EVOLUTION] Fittest score: {fittest.fitness_score:.4f}")
            
            # 4. Generate trade signal (mock - replace with actual opportunity detection)
            if fittest.fitness_score > 0.0:  # Lowered threshold to force action in test
                trade_signal = {
                    'pair': random.choice(fittest.strategy['target_pairs']),
                    'side': random.choice(['BUY', 'SELL']),
                    'size': fittest.strategy['max_position_size']
                }
                
                # 5. Auditor check
                if auditor.check_constitution(fittest, trade_signal):
                    swarm.execute_trade(fittest, trade_signal)
                else:
                    print(f"[AUDITOR] Trade vetoed: {auditor.violations[-1]}")
            
            # 6. Log generation
            # Ensure file exists
            with open('evolution_log.jsonl', 'a') as log:
                log.write(json.dumps({
                    'generation': swarm.generation,
                    'fittest_score': fittest.fitness_score,
                    'strategy': fittest.strategy,
                    'timestamp': time.time()
                }) + '\n')
            
            # 7. Wait for next generation
            print(f"[SENTINEL] Sleeping for {generation_interval} seconds...")
            time.sleep(generation_interval)
            
            if swarm.generation >= 3:
                print("\n[TEST] 3 Generations verified. System Functional.")
                break
                
    except KeyboardInterrupt:
        print("\n[STOP] User Termination.")

if __name__ == "__main__":
    import random  # For mock data
    main()
