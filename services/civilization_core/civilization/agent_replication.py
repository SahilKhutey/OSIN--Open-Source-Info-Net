"""
OSIN Agent Self-Replication
Autonomous generation of specialized AI nodes as the OSIN swarm grows
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np

class AgentCapability:
    GEO_SPATIAL = "geo_spatial"
    CYBER_INTEL = "cyber_intel"
    SIGNAL_ANALYSIS = "signal_analysis"

class SyntheticAgent:
    """A replicated intelligence node specialized in a specific domain"""
    def __init__(self, agent_id: str, capability: str):
        self.agent_id = agent_id
        self.capability = capability
        self.generation = datetime.now()
        self.performance = 0.85

class AgentFactory:
    """The 'Genome' of the OSIN organism: handles autonomous replication"""
    def __init__(self):
        self.active_agents: Dict[str, SyntheticAgent] = {}
        self.replication_events = []

    async def detect_needs(self, society_state: Dict):
        """Analyzes civilization stability and data volume to trigger replication"""
        needs = []
        if society_state.get('stability', 1.0) < 0.7:
            needs.append(AgentCapability.CYBER_INTEL)
        
        # Exponential growth simulation: replicate if population > 500
        if society_state.get('population_size', 0) > 500 and len(self.active_agents) < 10:
            needs.append(AgentCapability.GEO_SPATIAL)
            
        for need in needs:
            await self._replicate(need)

    async def _replicate(self, capability: str):
        """Spawns a new synthetic agent in the swarm"""
        a_id = f"replicated_{capability}_{len(self.active_agents)}"
        if a_id not in self.active_agents:
            agent = SyntheticAgent(a_id, capability)
            self.active_agents[a_id] = agent
            self.replication_events.append({
                "id": a_id,
                "capability": capability,
                "timestamp": datetime.now().isoformat()
            })
            print(f"OSIN Swarm Evolution: Replicated {a_id}")

    def get_ecosystem_status(self) -> Dict:
        return {
            "total_replicated": len(self.active_agents),
            "recent_replications": self.replication_events[-5:],
            "capabilities": list(set(a.capability for a in self.active_agents.values()))
        }
