"""
OSIN Learning Orchestrator
The 'Subconscious' layer: memory consolidation, causal analysis, and RL self-improvement
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from .memory.memory_system import MemoryStore, MemoryManager
from .reasoning.causal_engine import CausalReasoningEngine
from .learning.self_improvement import SelfImprovementEngine

app = FastAPI(title="OSIN Learning Intelligence Organism", version="6.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OSINLearningOrchestrator:
    def __init__(self):
        self.memory_store = MemoryStore()
        self.memory_manager = MemoryManager(self.memory_store)
        self.causal_engine = CausalReasoningEngine(self.memory_store)
        self.improvement_engine = SelfImprovementEngine(self.memory_store, self.causal_engine)
        self.is_running = False
        self.learning_interval = 300 # 5 minutes
        
    async def initialize(self):
        logging.info("Initializing OSIN Learning Subconscious... (PIM + Causal + RL)")

    async def start(self):
        self.is_running = True
        # 1. Main Self-Evolution loop
        asyncio.create_task(self._evolution_loop())
        # 2. Causal Analysis background task
        asyncio.create_task(self._causal_audit_loop())

    async def _evolution_loop(self):
        while self.is_running:
            # Evaluate performance and update reinforcement learning weights
            improvement = await self.improvement_engine.improvement_cycle()
            logging.info(f"OSIN Evolution Step: Performance Gain {improvement['performance_gain']:.4f}")
            await asyncio.sleep(self.learning_interval)

    async def _causal_audit_loop(self):
        while self.is_running:
            # In a live system, we'd pull recent episodic memories and run cross-causal analysis
            await asyncio.sleep(600) # Every 10 minutes

orchestrator = OSINLearningOrchestrator()

@app.on_event("startup")
async def startup():
    await orchestrator.initialize()
    await orchestrator.start()

@app.get("/status")
async def get_status():
    trend = orchestrator.improvement_engine.get_trend()
    return {
        "status": "SELF_EVOLVING",
        "trend": trend,
        "performance": orchestrator.improvement_engine.performance_metrics,
        "memory_stats": {
            "causal_links": len(orchestrator.causal_engine.causal_graph),
            "db_path": orchestrator.memory_store.db_path
        }
    }

@app.get("/causal-graph")
async def get_causal_graph():
    return orchestrator.causal_engine.causal_graph

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8023)
