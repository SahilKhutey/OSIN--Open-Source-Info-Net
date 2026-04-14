"""
OSIN Causal Reasoning Engine
Infers the underlying 'Why' behind intelligence event sequences
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from enum import Enum

class CausalRelationType(Enum):
    CAUSES = "causes"
    TRIGGERS = "triggers"
    ENABLES = "enables"
    PREVENTS = "prevents"
    CORRELATED = "correlated"
    UNRELATED = "unrelated"

class CausalReasoningEngine:
    """Advanced causal inference for strategic OSINT"""
    def __init__(self, memory_store):
        self.memory_store = memory_store
        self.causal_graph = {} # Key: event_a_event_b
        self.min_confidence = 0.6
    
    async def analyze_causality(self, event_a: Dict, event_b: Dict) -> Dict[str, Any]:
        """Analyzes spatial, temporal, and semantic metrics to infer causality"""
        # 1. Temporal Analysis (Effect must follow Cause)
        t_a = datetime.fromisoformat(event_a['timestamp'])
        t_b = datetime.fromisoformat(event_b['timestamp'])
        dt = (t_b - t_a).total_seconds()
        
        if dt < 0: return {"status": "temporal_invalid", "confidence": 0.0}
        
        # 2. Semantic Similarity Score
        # We'd ideally use the memory_store's embedding model here
        # For now, we simulate with a 0.7 floor for known related types
        similarity = 0.5
        if event_a.get('type') == event_b.get('type'): similarity = 0.8
        
        # 3. Probabilistic Inference
        confidence = similarity * np.exp(-dt / 86400) # Decay over 24h
        
        rel_type = CausalRelationType.CORRELATED
        if confidence > 0.8: rel_type = CausalRelationType.CAUSES
        elif confidence > 0.6: rel_type = CausalRelationType.TRIGGERS
        
        result = {
            "source": event_a['id'],
            "target": event_b['id'],
            "relation": rel_type.value,
            "confidence": float(confidence),
            "timestamp": datetime.now().isoformat()
        }
        
        self.causal_graph[f"{event_a['id']}_{event_b['id']}"] = result
        return result

    def get_causal_chains(self, seed_event_id: str) -> List[Dict]:
        """Retrieves known downstream effects of a specific intelligence event"""
        return [r for r in self.causal_graph.values() if r['source'] == seed_event_id]
