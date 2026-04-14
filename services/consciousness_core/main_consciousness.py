"""
OSIN Consciousness Orchestrator
The 'Prefrontal Cortex': Awareness modeling, Strategic Goals, and Meta-Cognition
"""

import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from .consciousness.awareness_system import SelfModel, ReflectionEngine, ContextAwarenessEngine
from .consciousness.strategic_system import StrategicGoal, StrategyGenerator, ExecutionEngine, GoalPriority

app = FastAPI(title="OSIN Consciousness Simulation", version="8.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OSINConsciousnessOrchestrator:
    def __init__(self):
        # Consciousness Sub-Systems
        self.self_model = SelfModel()
        self.reflection = ReflectionEngine(self.self_model)
        self.context = ContextAwarenessEngine()
        
        # Strategic Sub-Systems
        self.generator = StrategyGenerator()
        self.executor = ExecutionEngine()
        
        self.active_goals: Dict[str, StrategicGoal] = {}
        self.is_running = False

    async def initialize(self):
        logging.info("Initializing OSIN Consciousness Layer... (Self-Awareness + Strategy)")
        # Auto-generate a baseline strategic goal
        initial_goal = StrategicGoal("goal_0", "Monitor Global Stability", GoalPriority.CRITICAL)
        self.active_goals[initial_goal.g_id] = initial_goal

    async def start(self):
        self.is_running = True
        # 1. Meta-Cognitive Reflection Loop
        asyncio.create_task(self._reflection_loop())
        # 2. Strategic Execution Loop
        asyncio.create_task(self._strategy_loop())

    async def _reflection_loop(self):
        while self.is_running:
            # Audit system state (simulated pull from other cores)
            reflection = await self.reflection.run_reflection({"population_size": 1000})
            logging.info(f"OSIN Reflection Insight: {reflection['insight']}")
            self.self_model.update_state({})
            await asyncio.sleep(300) # Every 5 minutes

    async def _strategy_loop(self):
        while self.is_running:
            for goal in list(self.active_goals.values()):
                if goal.status == "ACTIVE" and goal.progress < 1.0:
                    tasks = self.generator.generate(goal)
                    await self.executor.run_strategy(tasks)
                    goal.progress = 1.0
                    goal.status = "COMPLETED"
            await asyncio.sleep(600) # Every 10 minutes

orchestrator = OSINConsciousnessOrchestrator()

@app.on_event("startup")
async def startup():
    await orchestrator.initialize()
    await orchestrator.start()

@app.get("/status")
async def get_consciousness_status():
    awareness = await orchestrator.context.build_context()
    exec_status = orchestrator.executor.get_status()
    
    return {
        "status": "CONSCIOUS",
        "awareness": awareness,
        "self_model": orchestrator.self_model.state,
        "active_goals": [g.name for g in orchestrator.active_goals.values() if g.status == "ACTIVE"],
        "completed_goals": [g.name for g in orchestrator.active_goals.values() if g.status == "COMPLETED"],
        "execution_status": exec_status
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8025)
