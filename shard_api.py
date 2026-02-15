
import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from run_species import run_cycle, HEADLESS_MODE

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SHARD-API] - %(message)s')
logger = logging.getLogger("shard_api")

app = FastAPI(title="Blackglass Shard Alpha API", version="0.0.1")

# Global State
class ShardState:
    def __init__(self):
        self.running = False
        self.stop_event = asyncio.Event()
        self.equity = 1000.0
        self.drawdown = 0.0
        self.status = "IDLE"

state = ShardState()

class StatusResponse(BaseModel):
    status: str
    equity: float
    drawdown: float

@app.on_event("startup")
async def startup_event():
    logger.info("Shard API Booting...")
    # Auto-start simulation? For now, wait for trigger or manual start via /start
    # state.running = True
    # asyncio.create_task(evolution_loop())

@app.get("/status", response_model=StatusResponse)
async def get_status():
    return StatusResponse(
        status=state.status,
        equity=state.equity,
        drawdown=state.drawdown
    )

@app.post("/start")
async def start_shard(background_tasks: BackgroundTasks):
    if state.running:
        return {"message": "Shard already running"}
    
    state.running = True
    state.status = "RUNNING"
    state.stop_event.clear()
    background_tasks.add_task(evolution_loop)
    return {"message": "Shard evolution started"}

@app.post("/interdict")
async def interdict_shard():
    """
    The Kill Switch. Called by Spire (North Node) when Variance > 0.05V.
    """
    if not state.running:
        return {"message": "Shard is not running"}
    
    logger.warning("⚠️ RECEIVED INTERDICTION SIGNAL (NORTH NODE)")
    state.stop_event.set()
    state.running = False
    state.status = "INTERDICTED"
    return {"message": "Shard halted by Constitutional Interdiction"}

async def evolution_loop():
    logger.info("Starting Evolution Loop...")
    try:
        # Run the species evolution in headless mode
        # We need to adapt run_species.py to be callable/awaitable or run in a thread
        # For this PoC, we assuming run_cycle is async or fast enough
        while state.running and not state.stop_event.is_set():
            # Mocking the cycle for API connectivity proof if run_species is blocking
            # In real implementation, run_species.run_cycle() would be called here
            
            # Simulate state changes
            await asyncio.sleep(1) 
            state.equity += 1.0 # Stonks
            
            # In a real integration, we'd pull this from the actual running env
            # For now, let's just prove the link works
            
    except Exception as e:
        logger.error(f"Evolution Loop Failed: {e}")
        state.status = "ERROR"
    finally:
        state.running = False
        if state.status != "INTERDICTED":
            state.status = "STOPPED"
        logger.info("Evolution Loop Terminated.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
