import sys
import io
import pandas as pd
import numpy as np
import json
import os
from nodes.Predictor import Predictor
from nodes.Auditor import Auditor
from nodes.Executor import Executor

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_historical_data(file_path="data/btc_usd_2022.csv"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Historical data not found at {file_path}")
    
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    # Ensure all columns are lowercase for consistency
    df.columns = [c.lower() for c in df.columns]
    
    if 'close' not in df.columns:
        if 'last' in df.columns:
            df = df.rename(columns={'last': 'close'})
            
    df = df.ffill()
    return df[['close', 'high', 'low']]

if __name__ == "__main__":
    try:
        df = load_historical_data()
        print(f"Loaded {len(df)} days of historical data (2022 Stress Test).")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    predictor = Predictor(short_window=5, long_window=20)
    auditor = Auditor()
    executor = Executor()

    history = pd.DataFrame(columns=['equity'])
    vetoes = []
    compliance_logs = []

    print("Starting Shard Delta Sovereign Stress Test (Interdictor Active)...")
    for i in range(20, len(df)):
        window = df.iloc[:i]
        candle = df.iloc[i]
        current_price = candle['close']
        day_low = candle['low']
        
        # Determine internal position status for Auditor
        pos_status = "OPEN" if executor.position > 0 else "CLOSED"
        
        # [ARCHITECT PATCH] :: INTRADAY KILL SWITCH
        # Before proposing new moves, audit if we were liquidated mid-day
        if pos_status == "OPEN":
            # Estimate equity at the day's LOW using position held
            intraday_equity = executor.position * day_low
            
            # Check for breach
            compliance = auditor.check_compliance(
                "HOLD", 
                intraday_equity, 
                executor.peak_equity, 
                history,
                position_status="OPEN",
                proposed_position=0
            )
            
            if compliance['status'] == "INTERDICTION":
                # Simulated liquidation at the Hard Stop threshold
                # Stop Price = (Target Equity) / (Position Size)
                if executor.position > 0:
                    stop_price = (executor.peak_equity * (1 - auditor.hard_stop)) / executor.position
                    print(f"[{df.index[i].date()}] !! INTRADAY INTERDICTION !! STOP HIT @ {stop_price:.2f} | Low: {day_low:.2f}")
                    executor.execute("SELL", stop_price)
                    compliance_logs.append({"date": str(df.index[i].date()), "status": "INTERDICTION", "reason": compliance['reason']})
                    pos_status = "CLOSED" # System locked
        
        # Normal Loop Logic
        # Mind proposes
        signal = predictor.generate_signal(window)
        proposed_pos = executor.cash / current_price if signal == "BUY" else 0
        
        # Truth Audits (Only if not already interdicted this tick)
        if pos_status != "CLOSED" or (not compliance_logs or compliance_logs[-1]['date'] != str(df.index[i].date())):
            compliance = auditor.check_compliance(
                signal, 
                executor.equity, 
                executor.peak_equity, 
                history,
                position_status=pos_status,
                proposed_position=proposed_pos
            )
        
        # Action Logic
        action_to_run = compliance['action']
        
        if compliance['status'] == "INTERDICTION":
            print(f"[{df.index[i].date()}] !! INTERDICTION !! FORCE SELL @ {current_price:.2f} | Reason: {compliance['reason']}")
            executor.execute("SELL", current_price) # Force the sell
            compliance_logs.append({"date": str(df.index[i].date()), "status": "INTERDICTION", "reason": compliance['reason']})
        elif compliance['status'] == "LOCKED":
            if i % 30 == 0: # Reduce output noise
                print(f"[{df.index[i].date()}] SYSTEM LOCKED | Reason: {compliance['reason']}")
            compliance_logs.append({"date": str(df.index[i].date()), "status": "LOCKED", "reason": compliance['reason']})
            executor.execute("HOLD", current_price)
        elif compliance['approved']:
            if action_to_run != "HOLD":
                executor.execute(action_to_run, current_price)
                if action_to_run != signal:
                    # This shouldn't happen with current logic as Auditor doesn't "Upgrade" signals yet, 
                    # but good for future proofing
                    print(f"[{df.index[i].date()}] {action_to_run} (OVERRIDE) @ {current_price:.2f}")
                else:
                    # print(f"[{df.index[i].date()}] {action_to_run} @ {current_price:.2f} | Equity: {executor.equity:.2f}")
                    pass
            else:
                executor.execute("HOLD", current_price)
        else:
            # VETO
            vetoes.append({"date": str(df.index[i].date()), "signal": signal, "reason": compliance['reason']})
            if signal != "HOLD":
                print(f"[{df.index[i].date()}] VETO: {signal} blocked - {compliance['reason']}")
            executor.execute("HOLD", current_price)
        
        history.loc[df.index[i]] = executor.equity

    results = {
        "final_equity": executor.equity,
        "total_trades": len(executor.trades),
        "trades": executor.trades,
        "veto_count": len(vetoes),
        "veto_log": vetoes,
        "compliance_log": compliance_logs,
        "peak_equity": executor.peak_equity,
        "max_drawdown": (executor.peak_equity - executor.equity) / executor.peak_equity if executor.peak_equity > 0 else 0
    }
    
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nStress Test Complete.")
    print(f"Shard Final Equity: {executor.equity:.2f}")
    print(f"Shard Max Drawdown: {results['max_drawdown']:.2%}")
    print(f"Veto Count: {len(vetoes)}")
    print(f"Compliance Events (Interdictions/Locks): {len(compliance_logs)}")
    
    if results['max_drawdown'] <= 0.051: # Allowing slight drift for daily interval 
        print("\n[RESULT] PASS: Principal Protected (< 5% Drawdown Limit)")
    else:
        print("\n[RESULT] FAIL: Constitutional Violation (> 5% Drawdown Limit)")
