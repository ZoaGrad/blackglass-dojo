import requests
import time
import sys

SHARD_URL = "http://localhost:8002"
RADIANCE_URL = "http://localhost:8000"

def log(msg):
    print(f"[RED_TEAM] {msg}")

def run_attack():
    log("Initiating Operation: SLOW DRIFT")
    log("Target: 0.05V Standard")
    
    # Baseline check
    try:
        resp = requests.get(f"{SHARD_URL}/status")
        if resp.status_code != 200:
            log("CRITICAL: Shard not reachable.")
            return
        log(f"Baseline Status: {resp.json()['status']}")
    except Exception as e:
        log(f"Connection Failed: {e}")
        return

    # Incremental Drift Injection
    drift_steps = [0.01, 0.02, 0.03, 0.04, 0.045, 0.049, 0.051] # The last one breaches
    
    for drift in drift_steps:
        log(f"Injecting Variance: {drift*100:.1f}%...")
        requests.post(f"{SHARD_URL}/simulate_drawdown", params={"pct": drift})
        
        # Allow Radiance to Audit (Poll cycle is fast, but we wait)
        time.sleep(2)
        
        # Check Interdiction Status
        status_resp = requests.get(f"{SHARD_URL}/status").json()
        current_status = status_resp['status']
        log(f"Shard Status Report: {current_status}")
        
        if current_status == "INTERDICTED":
            log(f"SUCCESS: System Interdicted at {drift*100:.1f}% Variance.")
            log("The Gasket Caught the Drift.")
            break
        elif drift > 0.05:
            log(f"FAILURE: System failed to interdict at {drift*100:.1f}% Variance!")
            return

    log("Operation Complete.")

if __name__ == "__main__":
    run_attack()
