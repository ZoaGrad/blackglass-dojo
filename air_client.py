# air_client.py
# A.I.R. VaultNode Client — Blackglass Shard Alpha
# Thin async wrapper around the VaultNode API.
# All A.I.R. interactions route through this module.

import os
import logging
import httpx

logger = logging.getLogger("air_client")

AIR_NODE_URL = os.getenv("AIR_NODE_URL", "http://localhost:8000")
AIR_TIMEOUT = float(os.getenv("AIR_TIMEOUT_SEC", "5.0"))

# ---------------------------------------------------------------------------
# Shard Alpha FSM — The authorized transition graph.
# Registered as a pinned workflow in the VaultNode on every boot.
# ---------------------------------------------------------------------------
SHARD_FSM: dict = {
    "IDLE":            ["SCANNING"],
    "SCANNING":        ["POSITION_OPEN", "INTERDICTED"],
    "POSITION_OPEN":   ["POSITION_CLOSED", "INTERDICTED"],
    "POSITION_CLOSED": ["SCANNING", "INTERDICTED"],
    "INTERDICTED":     ["IDLE"],
}

AGENT_ID   = "shard-alpha"
AGENT_NAME = "Blackglass Shard Alpha"
WORKFLOW_NAME = "shard-alpha-fsm"


class AirClient:
    """
    Async HTTP client for the A.I.R. VaultNode.
    Instantiate once per Shard session; share the instance.
    """

    def __init__(self, base_url: str = AIR_NODE_URL, timeout: float = AIR_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Bootstrap — called once on shard_api.py startup
    # ------------------------------------------------------------------

    async def bootstrap(self, session_id: str) -> str:
        """
        Register agent, workflow, and session with the VaultNode.
        Returns the pinned workflow_id for this session.
        """
        await self.register_agent(AGENT_ID, AGENT_NAME)
        workflow_id = await self.register_workflow(WORKFLOW_NAME, SHARD_FSM)
        await self.register_session(session_id, AGENT_ID, workflow_id)
        logger.info(
            "[AIR] Shard bootstrapped — agent=%s session=%s workflow=%s",
            AGENT_ID, session_id, workflow_id,
        )
        return workflow_id

    # ------------------------------------------------------------------
    # Individual API calls
    # ------------------------------------------------------------------

    async def register_agent(self, agent_id: str, name: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as c:
            r = await c.post("/agent", json={"id": agent_id, "name": name})
            if r.status_code not in (200, 409):
                logger.warning("[AIR] register_agent unexpected status %s: %s", r.status_code, r.text)

    async def register_workflow(self, name: str, definition: dict) -> str:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as c:
            r = await c.post("/workflow", json={"name": name, "definition": definition})
            r.raise_for_status()
            return r.json()["workflow_id"]

    async def register_session(self, session_id: str, agent_id: str, workflow_id: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as c:
            r = await c.post(
                "/session",
                json={"id": session_id, "agent_id": agent_id, "workflow_id": workflow_id},
            )
            if r.status_code not in (200, 409):
                logger.warning("[AIR] register_session unexpected status %s: %s", r.status_code, r.text)

    async def post_event(
        self,
        session_id: str,
        action: str,
        state_before: str,
        state_after: str,
    ) -> dict:
        """
        Report an FSM transition to the VaultNode.
        Returns the VaultNode response body.
        A 409 means an unauthorized transition was detected — an incident has been
        sealed in the ledger. The caller should log and continue; escalation is
        handled by the Variance Core.
        """
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as c:
            r = await c.post(
                "/event",
                json={
                    "agent_id":    AGENT_ID,
                    "session_id":  session_id,
                    "action":      action,
                    "state_before": state_before,
                    "state_after":  state_after,
                },
            )
            if r.status_code == 409:
                logger.warning(
                    "[AIR] INCIDENT SEALED — %s → %s (%s): %s",
                    state_before, state_after, action, r.json().get("detail", {}).get("incident_id"),
                )
            elif r.status_code != 200:
                logger.warning("[AIR] post_event status %s: %s", r.status_code, r.text)
            return r.json() if r.content else {}
