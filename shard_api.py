import asyncio
import threading
import uvicorn
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from run_species import Sentinel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Blackglass Shard Alpha: Neural Interface")

# GLOBAL STATE
SENTINEL = None
STOP_EVENT = threading.Event()
SENTINEL_THREAD = None

class InterdictionRequest(BaseModel):
    reason: str
    source: str

@app.on_event("startup")
async def startup_event():
    global SENTINEL, SENTINEL_THREAD
    print("⚡ KINETIC LINK: INITIALIZING SENTINEL...")
    
    # Initialize Sentinel (Mocks env vars if missing for safety)
    if not os.getenv("WALLET_ADDRESS"):
        os.environ["WALLET_ADDRESS"] = "0x0000000000000000000000000000000000000000"
        os.environ["PRIVATE_KEY"] = "0x000"
        os.environ["BASE_RPC_URL"] = "https://mainnet.base.org"
        
    SENTINEL = Sentinel()
    
    # Start Evolution Loop in Background Thread
    SENTINEL_THREAD = threading.Thread(target=SENTINEL.run_cycle, args=(STOP_EVENT,))
    SENTINEL_THREAD.daemon = True
    SENTINEL_THREAD.start()
    print("⚡ KINETIC LINK: SENTINEL ONLINE.")

@app.get("/status")
def get_status():
    """
    Telemetry Endpoint for the Spire.
    """
    if not SENTINEL:
        return {"status": "OFFLINE"}
    
    is_alive = SENTINEL_THREAD.is_alive()
    if not is_alive and not STOP_EVENT.is_set():
        return {"status": "CRASHED", "health": 0}
        
    if STOP_EVENT.is_set():
        return {"status": "INTERDICTED", "health": 0}

    # Mocking live equity for the interface test if not set
    # In a real kinetic link, Sentinel would expose thread-safe equity
    current_equity = SENTINEL.swarm.equity if hasattr(SENTINEL.swarm, 'equity') else 1000.0
    drawdown = SENTINEL.auditor.total_drawdown
    
    return {
        "status": "RUNNING",
        "equity": current_equity,
        "drawdown_pct": drawdown,
        "generation": SENTINEL.swarm.generation
    }

@app.post("/simulate_drawdown")
def simulate_drawdown(pct: float):
    """
    TESTING ONLY: Manually set drawdown to trigger Kill Switch.
    """
    if SENTINEL and SENTINEL.auditor:
        SENTINEL.auditor.total_drawdown = pct
        return {"status": "UPDATED", "drawdown": SENTINEL.auditor.total_drawdown}
    return {"status": "ERROR", "message": "Sentinel not initialized"}

@app.post("/interdict")
def interdict_shard(req: InterdictionRequest):
    """
    The Kill Switch. Spire calls this to halt the Shard.
    """
    print(f"🚨 INTERDICTION RECEIVED from {req.source}: {req.reason}")
    STOP_EVENT.set()
    return {"status": "INTERDICTED", "message": "Sentinel Halted."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
