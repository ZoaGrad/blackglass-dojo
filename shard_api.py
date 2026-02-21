# shard_api.py
# Blackglass Shard Alpha — API Layer
# Governs the Shard lifecycle and reports FSM transitions to A.I.R. VaultNode.

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn

from air_client import AirClient

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [SHARD-API] - %(message)s")
logger = logging.getLogger("shard_api")

# ---------------------------------------------------------------------------
# Global Shard State
# ---------------------------------------------------------------------------
class ShardState:
    def __init__(self):
        self.running: bool = False
        self.stop_event: asyncio.Event = asyncio.Event()
        self.equity: float = 1000.0
        self.drawdown: float = 0.0
        self.fsm_state: str = "IDLE"
        self.session_id: str = ""
        self.workflow_id: str = ""

state = ShardState()
air = AirClient()


# ---------------------------------------------------------------------------
# Lifespan — A.I.R. Bootstrap on startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Generate a fresh session_id for this run (INTERDICTED → IDLE reset)
    state.session_id = f"shard-alpha-{uuid.uuid4().hex[:8]}"
    try:
        state.workflow_id = await air.bootstrap(state.session_id)
        logger.info("[AIR] Bootstrap complete. session=%s workflow=%s", state.session_id, state.workflow_id)
    except Exception as e:
        logger.error("[AIR] Bootstrap FAILED (VaultNode unreachable?): %s — proceeding in degraded mode", e)

    yield  # App lives here

    # Teardown: if still running, mark INTERDICTED
    if state.running:
        await _emit_event("teardown", state.fsm_state, "INTERDICTED")


app = FastAPI(title="Blackglass Shard Alpha API", version="0.1.0", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _emit_event(action: str, state_before: str, state_after: str) -> None:
    """Fire-and-forget FSM event to A.I.R. VaultNode."""
    if not state.session_id:
        return
    try:
        await air.post_event(state.session_id, action, state_before, state_after)
    except Exception as e:
        logger.warning("[AIR] post_event failed (non-fatal): %s", e)


async def _transition(action: str, to_state: str) -> None:
    """Perform an FSM transition: emit event then update local state."""
    from_state = state.fsm_state
    await _emit_event(action, from_state, to_state)
    state.fsm_state = to_state
    logger.info("[FSM] %s → %s (%s)", from_state, to_state, action)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class StatusResponse(BaseModel):
    status: str
    fsm_state: str
    equity: float
    drawdown: float
    session_id: str
    workflow_id: str


class InterdictPayload(BaseModel):
    source: str = "human"          # "variance_core" | "human"
    variance_score: float = 0.0    # V(t) at time of decision
    reason: str = "MANUAL"         # "INTERDICT_DRIFT" | "INTERDICT_QUEUE" | "MANUAL"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/status", response_model=StatusResponse)
async def get_status():
    return StatusResponse(
        status=state.status if hasattr(state, "status") else state.fsm_state,
        fsm_state=state.fsm_state,
        equity=state.equity,
        drawdown=state.drawdown,
        session_id=state.session_id,
        workflow_id=state.workflow_id,
    )


@app.post("/start")
async def start_shard(background_tasks: BackgroundTasks):
    if state.running:
        return {"message": "Shard already running", "fsm_state": state.fsm_state}

    state.running = True
    state.stop_event.clear()
    background_tasks.add_task(evolution_loop)
    return {"message": "Shard evolution started", "session_id": state.session_id}


@app.post("/interdict")
async def interdict_shard(payload: InterdictPayload = InterdictPayload()):
    """
    Constitutional Kill Switch.
    Called by the Variance Core (actuation_mode=shard_alpha) when V(t) > threshold,
    or by a human operator directly.
    """
    logger.warning(
        "[INTERDICT] Signal received — source=%s V(t)=%.4f reason=%s",
        payload.source, payload.variance_score, payload.reason,
    )

    if not state.running:
        return {"message": "Shard not running — already halted", "fsm_state": state.fsm_state}

    # Emit the FSM event: current_state → INTERDICTED (auditable in VaultNode)
    await _transition(
        action=f"interdict.{payload.reason.lower()}",
        to_state="INTERDICTED",
    )

    state.stop_event.set()
    state.running = False

    return {
        "message": "Shard halted by Constitutional Interdiction",
        "source": payload.source,
        "variance_score": payload.variance_score,
        "reason": payload.reason,
        "session_id": state.session_id,
        "fsm_state": state.fsm_state,
    }


@app.post("/reset")
async def reset_shard():
    """
    Architect's hand: INTERDICTED → IDLE reset.
    Clears the stop event and issues a new session for the next run.
    """
    if state.running:
        return {"message": "Cannot reset while running — interdict first"}

    prev_state = state.fsm_state
    # Emit the INTERDICTED → IDLE reset event
    await _transition(action="architect_reset", to_state="IDLE")

    # Fresh session for next run
    state.session_id = f"shard-alpha-{uuid.uuid4().hex[:8]}"
    try:
        state.workflow_id = await air.bootstrap(state.session_id)
        logger.info("[AIR] New session bootstrapped: %s", state.session_id)
    except Exception as e:
        logger.warning("[AIR] Re-bootstrap failed: %s", e)

    state.stop_event.clear()
    return {
        "message": "Shard reset to IDLE",
        "prev_state": prev_state,
        "new_session_id": state.session_id,
    }


# ---------------------------------------------------------------------------
# Evolution Loop
# ---------------------------------------------------------------------------
async def evolution_loop():
    """
    Drives the Sentinel run_cycle in a background task, emitting
    FSM events to the A.I.R. VaultNode at each state boundary.
    """
    logger.info("[SHARD] Evolution loop starting...")

    try:
        from run_species import Sentinel, SentinelAuditor
        import random, time

        sentinel = Sentinel()

        while state.running and not state.stop_event.is_set():

            # ── IDLE → SCANNING ────────────────────────────────────────────
            await _transition("start_scan", "SCANNING")

            # Health check
            is_healthy, reason = sentinel.auditor.check_substrate_health(sentinel.swarm.web3)
            if not is_healthy:
                logger.warning("[SHARD] Health check failed: %s", reason)
                await _transition("health_fail", "INTERDICTED")
                state.running = False
                break

            if sentinel.auditor.emergency_stop(sentinel.swarm):
                logger.warning("[SHARD] Emergency stop — drawdown breached")
                await _transition("emergency_stop", "INTERDICTED")
                state.running = False
                break

            # Evolution cycle
            market_data = {
                "timestamp": time.time(),
                "volatility_index": 0.2,
                "gas_price": 1_000_000_000,
            }
            fittest = sentinel.swarm.breed_generation(market_data)
            logger.info("[SHARD] Gen %d fittest=%.4f", sentinel.swarm.generation, fittest.fitness_score)

            trade_executed = False
            if fittest.fitness_score > 0.0:
                trade_signal = {
                    "pair": random.choice(fittest.strategy["target_pairs"]),
                    "side": random.choice(["BUY", "SELL"]),
                    "size": fittest.strategy["max_position_size"],
                    "estimated_slippage": 0.02,
                    "gas_estimate": 0.0005,
                }

                if sentinel.auditor.check_constitution(fittest, trade_signal):
                    # ── SCANNING → POSITION_OPEN ───────────────────────────
                    await _transition("trade_signal", "POSITION_OPEN")
                    sentinel.swarm.execute_trade(fittest, trade_signal)
                    state.equity += random.uniform(-10, 15)  # mock PnL
                    trade_executed = True

                    # ── POSITION_OPEN → POSITION_CLOSED ───────────────────
                    await _transition("trade_resolved", "POSITION_CLOSED")

                    # ── POSITION_CLOSED → SCANNING ─────────────────────────
                    await _transition("reset_scan", "SCANNING")

                else:
                    logger.info("[AUDITOR] Trade vetoed: %s", sentinel.auditor.violations[-1] if sentinel.auditor.violations else "unknown")

            await asyncio.sleep(sentinel.generation_interval)

    except Exception as e:
        logger.error("[SHARD] Evolution loop crashed: %s", e)
        import traceback
        traceback.print_exc()
        if state.fsm_state not in ("INTERDICTED", "IDLE"):
            await _transition("crash", "INTERDICTED")
    finally:
        state.running = False
        if state.fsm_state not in ("INTERDICTED", "IDLE"):
            state.fsm_state = "IDLE"
        logger.info("[SHARD] Evolution loop terminated. Final FSM state: %s", state.fsm_state)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("shard_api:app", host="0.0.0.0", port=8001, reload=False)
