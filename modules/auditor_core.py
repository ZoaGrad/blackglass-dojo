from typing import Dict
from decimal import Decimal

class InsufficientROIException(Exception):
    pass

class DrawdownViolationException(Exception):
    pass

class AuditorCore:
    """
    The 'Auditor' (South Node).
    Enforces hard-coded risk parameters that Strategy cannot override.
    """
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.hard_stop_loss = 0.05 # 5% Max Drawdown
        self.min_roi_bps = 50      # 0.5% (50 Basis Points) Net ROI
        self.max_trade_size_usd = 450.00 # $450 Max Trade Size (Liquidity constraint)
        self.gas_baseline_usd = 0.04     # Default (Replaced by Oracle)

    def update_gas_baseline(self, current_gas_usd: float):
        """
        Updates the gas baseline from a dynamic Oracle.
        Includes a 20% safety buffer for L1 security fees.
        """
        self.gas_baseline_usd = current_gas_usd * 1.20
        print(f"[AUDITOR] Gas Baseline Updated: ${self.gas_baseline_usd:.4f}")

    def verify_solvency(self, current_equity: float, clone_id: str):
        """
        Checks if the portfolio is within the max allowed drawdown.
        Triggers EMERGENCY SHUTDOWN if violated.
        """
        drawdown = (self.initial_capital - current_equity) / self.initial_capital
        
        if drawdown >= self.hard_stop_loss:
            reason = f"CRITICAL: Drawdown {drawdown:.2%} exceeds limit {self.hard_stop_loss:.2%}"
            print(f"[{clone_id}] AUDITOR INTERDICTION: {reason}")
            raise DrawdownViolationException(reason)
            
        return True

    def verify_opportunity(self, 
                           estimated_profit_usd: float, 
                           trade_size_usd: float) -> bool:
        """
        Checks if the trade meets the Minimum ROI and Max Size constraints.
        """
        # 1. Size Check
        if trade_size_usd > self.max_trade_size_usd:
            raise InsufficientROIException(f"Trade Size ${trade_size_usd} exceeds Auditor Limit ${self.max_trade_size_usd}")

        # 2. Net Profit Calculation
        net_profit = estimated_profit_usd - self.gas_baseline_usd
        roi_bps = (net_profit / trade_size_usd) * 10000
        
        if roi_bps < self.min_roi_bps:
            raise InsufficientROIException(f"ROI {roi_bps:.2f} bps < Minimum {self.min_roi_bps} bps")
            
        return True
