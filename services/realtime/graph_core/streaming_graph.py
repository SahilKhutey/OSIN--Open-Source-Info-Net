"""
Real-Time Graph Linking Engine
Live entity and relationship management for OSIN Graph Core
"""

import asyncio
from typing import Dict, Any, Set
from datetime import datetime
import logging

# Assuming relative imports from the orchestrator or corrected package path
# For simplicity in this microservice, we will use mock/stub paths if needed
# but I'll implement based on the expected structure.

class StreamingGraphEngine:
    def __init__(self, entity_store, relationship_engine, similarity_engine):
        self.entity_store = entity_store
        self.relationship_engine = relationship_engine
        self.similarity_engine = similarity_engine
        self.active_connections: Set[str] = set()
        self.event_queue = asyncio.Queue()
        self.logger = logging.getLogger("osin-streaming-graph")
    
    async def process_event_stream(self):
        """Infinite loop for processing events from the queue in real-time"""
        self.logger.info("Starting real-time graph reasoning loop")
        while True:
            try:
                event = await self.event_queue.get()
                await self._process_event(event)
                self.event_queue.task_done()
            except Exception as e:
                self.logger.error(f"Streaming graph error: {e}")
                await asyncio.sleep(1)
    
    async def _process_event(self, event: Dict[str, Any]):
        """Convert intelligence event to graph entity and discover relationships"""
        # 1. Determine Entity Type
        entity_type = self._map_event_to_entity(event['type'])
        
        # 2. Ingest Entity
        entity_id = f"ent_{event['id'][-8:]}"
        entity_data = {
            "id": entity_id,
            "type": entity_type,
            "properties": {**event['data'], "source": event['source_module']},
            "source_modules": [event['source_module']],
            "confidence": event['confidence']
        }
        
        # Add to store (assuming add_entity takes a dict or Entity object)
        self.entity_store.add_entity(entity_data)
        self.active_connections.add(entity_id)
        
        # 3. Reasoning: Discovery auto-relationships
        await self._discover_relationships(entity_id, entity_data)
        
    def _map_event_to_entity(self, event_type: str) -> str:
        mapping = {
            'geo': 'location', 'cyber': 'domain', 'audio': 'audio', 
            'image': 'image', 'signal': 'wifi_network', 'threat': 'threat_signal'
        }
        return mapping.get(event_type, 'event')

    async def _discover_relationships(self, entity_id: str, entity_data: Dict):
        """Cross-reference new entity against existing entities for similarity"""
        existing = [e for e in self.entity_store.entities.values() if e['id'] != entity_id]
        
        for candidate in existing:
            # Semantic similarity check
            # In a real system, this would be highly optimized/vectorized
            related, score = self.similarity_engine.are_entities_related(entity_data, candidate)
            if related:
                self.relationship_engine.create_relationship(
                    entity_id, candidate['id'], 'SIMILAR_TO', {"score": score}, score
                )
