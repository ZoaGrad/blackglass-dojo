import asyncio
import random
from typing import Optional
from .territory_manager import TerritoryManager
from .auditor_core import AuditorCore, InsufficientROIException, DrawdownViolationException
from .safety_gasket import System5Gasket
from .market_oracle import MarketOracle

class CloneBase:
    """
    The Base Unit of the Swarm.
    """
    def __init__(self, 
                 config: dict, 
                 territory_manager: TerritoryManager, 
                 auditor: AuditorCore):
        self.id = config['id']
        self.name = config['name']
        self.strategy = config['strategy']
        self.target_pair = config['target_pair']
        self.risk_profile = config['risk_profile']
        self.extra_config = config
        
        self.territory_manager = territory_manager
        self.auditor = auditor
        self.active = True
        
        # SYSTEM 5 WIRED: The Ethical Layer
        self.gasket = System5Gasket()
        # SYSTEM 4 WIRED: The Sensor Array
        self.oracle = MarketOracle()

    async def run(self):
        """
        The Main Lifecycle Loop.
        """
        print(f"[{self.id}] ACTIVATED | Strategy: {self.strategy} | Target: {self.target_pair}")
        symbol = self.target_pair.split('/')[0] if '/' in self.target_pair else self.target_pair
        
        while self.active:
            try:
                # 1. Self-Preservation Check (Every Loop)
                # In a real scenario, equity comes from wallet state
                # Mocking equity for now
                current_equity = self.auditor.initial_capital # Placeholder
                self.auditor.verify_solvency(current_equity, self.id)

                # 2. Opportunity Scan (Real Market Data)
                await asyncio.sleep(random.uniform(0.5, 2.0)) # Hunting...
                
                # Fetch Real Kinetic Data
                current_price = self.oracle.get_price(symbol)
                kinetic_entropy = self.oracle.get_kinetic_entropy(symbol)
                
                # If Oracle Fails (Price=0), assume no opportunity
                found_opportunity = current_price > 0
                
                if found_opportunity:
                    
                    # 3. Territory Acquisition (Inhibitor Chip)
                    acquired = await self.territory_manager.acquire_territory(self.target_pair, self.id)
                    
                    if acquired:
                        try:
                            # 4. Auditor Check (The Hunger)
                            # Mocking Profit Est (Strategy Logic would go here)
                            est_profit_usd = random.uniform(0.01, 1.00) 
                            trade_size_usd = 400.00
                            
                            self.auditor.verify_opportunity(est_profit_usd, trade_size_usd)
                            
                            # 5. STP: CONSTITUTIONAL CLEARANCE (The Brain Check)
                            # The Hand cannot move without the Brain's signature.
                            # ASH PROTOCOL: Passing Kinetic Entropy for metabolic validation
                            cct = self.gasket.issue_constitutional_token(
                                intent=f"EXECUTE_TRADE::{self.target_pair}::{current_price}",
                                kinetic_entropy=kinetic_entropy
                            )
                            
                            if not cct:
                                raise PermissionError(f"SYSTEM 5 VETO: Constitutional Token Denied. Entropy: {kinetic_entropy:.4f}")
                            
                            # 5. Execution (Simulated)
                            token_id = cct.split('|')[1][:8]
                            print(f"[{self.id}] EXECUTING TRADE on {self.target_pair} (${current_price:.2f}) | Profit Est: ${est_profit_usd:.2f} | CCT: {token_id} | Entropy: {kinetic_entropy:.4f}")
                            await asyncio.sleep(0.2) # Execution Latency
                            
                        except InsufficientROIException as e:
                            print(f"[{self.id}] VETO: {e}")
                        except Exception as e:
                            print(f"[{self.id}] ERROR: {e}")
                        finally:
                            # 6. Release Territory
                            await self.territory_manager.release_territory(self.target_pair, self.id)
                    else:
                        # Territory occupied by Fratricide Protection
                        print(f"[{self.id}] BLOCKED: Territory {self.target_pair} Occupied.")
                        
            except DrawdownViolationException:
                print(f"[{self.id}] SUICIDE PROTOCOL: Drawdown Max Reached. Terminating.")
                self.active = False
                break
            except Exception as e:
                print(f"[{self.id}] CRITICAL FAILURE: {e}")
                await asyncio.sleep(5)
