"""
OSIN Autonomous Intelligence Organism - Main Orchestrator
The "Prefrontal Cortex" of the OSIN Platform (v5.0.0)
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from .agent_system import AutonomousAgent, PolicyEngine
from .swarm_system import SwarmOrchestrator
from .digital_twin.earth_twin import DigitalTwinEngine
from .safety.monitoring import SafetyMonitor

# Access to the brain (Graph Core)
from services.graph_core.graph_builder import OSINGraphBuilder

app = FastAPI(title="OSIN Autonomous Intelligence Organism", version="5.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OSINAutonomousOrchestrator:
    def __init__(self):
        self.graph_builder = OSINGraphBuilder()
        self.policy_engine = PolicyEngine()
        self.autonomous_agent = AutonomousAgent(self.graph_builder, self.policy_engine)
        self.swarm_orchestrator = SwarmOrchestrator()
        self.digital_twin = DigitalTwinEngine()
        self.safety_monitor = SafetyMonitor(self)
        
        self.is_running = False
        self.cycle_interval = 60 # seconds

    async def initialize(self):
        logging.info("Initializing OSIN Autonomous Organism (v5.0.0)...")

    async def start(self):
        self.is_running = True
        # 1. Start Autonomous Thinking Cycle
        asyncio.create_task(self._autonomous_loop())
        # 2. Start Swarm Processing
        asyncio.create_task(self._swarm_loop())
        # 3. Start Digital Twin Simulation
        asyncio.create_task(self._simulation_loop())
        # 4. Start Safety Watchdog
        asyncio.create_task(self.safety_monitor.monitor_loop())

    async def _autonomous_loop(self):
        while self.is_running:
            results = await self.autonomous_agent.autonomous_cycle()
            if results: logging.info(f"Autonomous Cycle Active: {len(results)} actions.")
            await asyncio.sleep(self.cycle_interval)

    async def _swarm_loop(self):
        while self.is_running:
            # Sync graph events to Swarm
            # In a real system, we'd poll recent entities
            await asyncio.sleep(300) # Every 5 minutes

    async def _simulation_loop(self):
        while self.is_running:
            forecast = await self.digital_twin.simulate_horizon(24)
            logging.info(f"Digital Twin Forecast: {forecast['simulated_risks']}")
            await asyncio.sleep(3600) # Every hour

orchestrator = OSINAutonomousOrchestrator()

@app.on_event("startup")
async def startup():
    await orchestrator.initialize()
    await orchestrator.start()

@app.get("/status")
async def get_status():
    return {
        "status": "AUTONOMOUS" if orchestrator.is_running else "MONITORED",
        "actions_executed": orchestrator.autonomous_agent.actions_executed,
        "swarm_agents": len(orchestrator.swarm_orchestrator.agents),
        "earth_state_updated": orchestrator.digital_twin.state.last_updated.isoformat(),
        "safety_log": orchestrator.safety_monitor.safety_log[-5:]
    }

@app.get("/simulation/forecast")
async def get_forecast():
    return await orchestrator.digital_twin.simulate_horizon(24)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8022)
