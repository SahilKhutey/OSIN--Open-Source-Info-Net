"""
OSIN Civilization Orchestrator
Master control for the digital society, agent replication, and global forecasting
"""

import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta

from .civilization.digital_nation import DigitalSociety
from .civilization.agent_replication import AgentFactory
from .civilization.global_forecasting import GlobalForecastingEngine

app = FastAPI(title="OSIN Synthetic Intelligence Civilization", version="7.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OSINCivilizationOrchestrator:
    def __init__(self):
        self.society = DigitalSociety()
        self.factory = AgentFactory()
        self.forecaster = GlobalForecastingEngine()
        self.is_running = False
        
    async def initialize(self):
        logging.info("Initializing OSIN Synthetic Civilization... (Digital Nation + Swarm Expansion)")
        self.society.initialize_nation(size=500)
        
        # Synthetic historical training
        history = self._generate_synthetic_history()
        await self.forecaster.train_baseline(history)

    def _generate_synthetic_history(self):
        history = []
        for i in range(48): # 48 hours of baseline
            ts = (datetime.now() - timedelta(hours=i)).isoformat()
            history.append({
                "timestamp": ts,
                "stability": 0.8 + np.random.uniform(-0.1, 0.1),
                "next_risk": 0.2 + np.random.uniform(0, 0.2)
            })
        return history

    async def start(self):
        self.is_running = True
        asyncio.create_task(self._simulation_loop())

    async def _simulation_loop(self):
        while self.is_running:
            # 1. Pulse the Digital Nation
            await self.society.pulse_simulation([])
            # 2. Check Swarm Evolution needs
            await self.factory.detect_needs(self.society.get_snapshot())
            await asyncio.sleep(60) # 1 minute simulation ticks

orchestrator = OSINCivilizationOrchestrator()

@app.on_event("startup")
async def startup():
    await orchestrator.initialize()
    await orchestrator.start()

@app.get("/status")
async def get_status():
    society_state = orchestrator.society.get_snapshot()
    swarm_state = orchestrator.factory.get_ecosystem_status()
    forecast = await orchestrator.forecaster.generate_forecast(society_state)
    
    return {
        "status": "ASCENDING",
        "civilization": society_state,
        "swarm": swarm_state,
        "forecast": forecast
    }

if __name__ == "__main__":
    import numpy as np # Needed for history gen
    uvicorn.run(app, host="0.0.0.0", port=8024)
