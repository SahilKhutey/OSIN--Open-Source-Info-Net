"""
Relationship Engine - Manages connections between entities in OSIN Graph Core
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
import uuid
from .architecture import Relationship, RelationshipType, Entity

class RelationshipEngine:
    def __init__(self, entity_store):
        self.entity_store = entity_store
        self.relationships: Dict[str, Relationship] = {}
        self.relationship_index: Dict[str, Set[str]] = {}  # entity_id -> set of relationship_ids
        self.type_index: Dict[RelationshipType, Set[str]] = {rt: set() for rt in RelationshipType}
    
    def create_relationship(self, 
                          source_id: str, 
                          target_id: str, 
                          relationship_type: RelationshipType,
                          properties: Optional[Dict] = None,
                          confidence: float = 0.8) -> Optional[str]:
        """Create a relationship between entities with index updates"""
        if (not self.entity_store.get_entity(source_id) or 
            not self.entity_store.get_entity(target_id)):
            return None
        
        relationship_id = f"rel_{uuid.uuid4().hex[:12]}"
        relationship = Relationship(
            id=relationship_id,
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            properties=properties or {},
            confidence=confidence,
            created_at=datetime.now()
        )
        
        self.relationships[relationship_id] = relationship
        
        # Update entity link index
        for eid in [source_id, target_id]:
            if eid not in self.relationship_index:
                self.relationship_index[eid] = set()
            self.relationship_index[eid].add(relationship_id)
        
        # Update type index
        self.type_index[relationship_type].add(relationship_id)
        
        return relationship_id
    
    def get_relationships(self, 
                         entity_id: Optional[str] = None,
                         relationship_type: Optional[RelationshipType] = None) -> List[Relationship]:
        """Query relationships filtered by entity ID and/or relationship type"""
        rel_ids = set(self.relationships.keys())
        
        if entity_id:
            rel_ids.intersection_update(self.relationship_index.get(entity_id, set()))
        
        if relationship_type:
            rel_ids.intersection_update(self.type_index.get(relationship_type, set()))
            
        return [self.relationships[rid] for rid in rel_ids]
