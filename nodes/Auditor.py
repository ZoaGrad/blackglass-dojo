import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any

class Auditor:
    def __init__(self, strategy_path: str = "Strategy.md"):
        self.hard_stop = 0.05
        self.soft_stop = 0.01
        self.min_sharpe = 2.0

    def check_compliance(self, 
                         signal: str, 
                         current_equity: float, 
                         peak_equity: float, 
                         history: pd.DataFrame,
                         position_status: str = "CLOSED", # "OPEN" or "CLOSED"
                         proposed_position: float = 0.0) -> Dict[str, Any]:
        """
        Returns: {'approved': bool, 'action': str, 'status': str, 'reason': str}
        """
        # 0. CROSS-SYSTEM CIRCUIT BREAKER: SENTINEL FATIGUE CHECK
        sentinel_path = r"c:\Users\colem\blackglass-sentinel\sentinel_status.json"
        if os.path.exists(sentinel_path):
            try:
                with open(sentinel_path, 'r') as f:
                    sentinel_data = json.load(f)
                    if sentinel_data.get("status") == "FATIGUE_BREACH":
                        return {
                            "approved": False,
                            "action": "HOLD",
                            "status": "LOCKED",
                            "reason": "SENTINEL INTERDICTION: High fatigue risk detected. Global trading lock enforced."
                        }
            except Exception:
                pass # Fail open to telemetry errors, but logged in TUI
        current_drawdown = (peak_equity - current_equity) / peak_equity if peak_equity > 0 else 0
        
        # 1. THE KILL SWITCH (Interdiction)
        if current_drawdown >= self.hard_stop and position_status == "OPEN":
            return {
                "approved": True, # Approving the EMERGENCY ACTION
                "action": "FORCE_SELL",
                "status": "INTERDICTION",
                "reason": f"CRITICAL: Drawdown {current_drawdown:.2%} exceeds Hard Stop. LIQUIDATING."
            }

        # 2. THE LOCKOUT (Dead Man's Switch)
        if current_drawdown >= self.hard_stop and position_status == "CLOSED":
            return {
                "approved": False,
                "action": "HOLD",
                "status": "LOCKED",
                "reason": "Account locked due to max drawdown breach. Architect reset required."
            }

        # 3. CONSERVATIVE BUYING
        if signal == "BUY":
            if current_drawdown > self.soft_stop:
                return {
                    "approved": False,
                    "action": "HOLD",
                    "status": "VETO",
                    "reason": f"Vetoed: Cannot add risk while in drawdown {current_drawdown:.2%} > 1%."
                }
            # Add Sharpe check if sufficient history
            if len(history) >= 60:
                returns = history['equity'].pct_change().dropna()
                if returns.std() > 0:
                    sharpe = returns.mean() / returns.std() * np.sqrt(252)
                    if sharpe < self.min_sharpe:
                        return {
                            "approved": False,
                            "action": "HOLD",
                            "status": "VETO",
                            "reason": f"Sharpe too low: {sharpe:.2f} < 2.0"
                        }
            
            return {"approved": True, "action": "BUY", "status": "APPROVED", "reason": "Clear sky."}

        # 4. ALWAYS ALLOW SELLING
        if signal == "SELL":
            return {"approved": True, "action": "SELL", "status": "APPROVED", "reason": "Reducing exposure."}

        return {"approved": True, "action": "HOLD", "status": "PASSIVE", "reason": "Nominal."}
