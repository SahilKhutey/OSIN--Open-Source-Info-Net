"""
OSIN Digital Nation Simulation
A simulated world-scale society with entities, economies, and systemic dependencies
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import numpy as np
from enum import Enum
import networkx as nx

class EntityRole(Enum):
    CITIZEN = "citizen"
    ORGANIZATION = "organization"
    DEVICE = "device"
    GOVERNMENT = "government"
    INFRASTRUCTURE = "infrastructure"

class EntityState:
    """The granular state of a synthetic intelligence citizen/entity"""
    def __init__(self, entity_id: str, role: EntityRole):
        self.entity_id = entity_id
        self.role = role
        self.attributes = {
            "trust": np.random.uniform(0.4, 0.9),
            "activity": np.random.uniform(0.1, 0.8),
            "risk_exposure": np.random.uniform(0.0, 0.3),
            "resources": np.random.uniform(0.5, 1.0)
        }
        self.location: Optional[tuple] = None
    
    def update(self, delta: Dict[str, float]):
        for k, v in delta.items():
            if k in self.attributes:
                self.attributes[k] = np.clip(self.attributes[k] + v, 0.0, 1.0)

    def to_dict(self) -> Dict:
        return {
            "id": self.entity_id,
            "role": self.role.value,
            "attributes": self.attributes,
            "location": self.location
        }

class DigitalSociety:
    """The 'Digital Nation' orchestrator for a synthetic intelligence civilization"""
    def __init__(self):
        self.entities: Dict[str, EntityState] = {}
        self.social_graph = nx.Graph()
        self.stability_index = 0.85
        
    def initialize_nation(self, size: int = 1000):
        """Initializes the population using strategic role distribution"""
        roles = [EntityRole.CITIZEN, EntityRole.ORGANIZATION, EntityRole.GOVERNMENT, EntityRole.INFRASTRUCTURE]
        for i in range(size):
            role = np.random.choice(roles, p=[0.7, 0.15, 0.05, 0.1])
            e_id = f"{role.value}_{i}"
            entity = EntityState(e_id, role)
            entity.location = (np.random.uniform(-90, 90), np.random.uniform(-180, 180))
            self.entities[e_id] = entity
            self.social_graph.add_node(e_id)
            
        # Create random connectivity (The Social Fabric)
        for i in range(size * 2):
            u, v = np.random.choice(list(self.entities.keys()), size=2)
            self.social_graph.add_edge(u, v, weight=np.random.random())

    async def pulse_simulation(self, events: List[Dict]):
        """Advance the digital society by one simulation tick based on global events"""
        for event in events:
            # Propagate event impact across the civilization graph
            impact = event.get('impact_strength', 0.05)
            # Simplified: Random walk impact on 10% of population
            targets = np.random.choice(list(self.entities.keys()), size=int(len(self.entities)*0.1))
            for t in targets:
                self.entities[t].update({"risk_exposure": impact})
        
        self._calculate_stability()

    def _calculate_stability(self):
        risks = [e.attributes['risk_exposure'] for e in self.entities.values()]
        self.stability_index = 1.0 - np.mean(risks)

    def get_snapshot(self) -> Dict:
        return {
            "population_size": len(self.entities),
            "stability": float(self.stability_index),
            "network_density": nx.density(self.social_graph),
            "timestamp": datetime.now().isoformat()
        }
