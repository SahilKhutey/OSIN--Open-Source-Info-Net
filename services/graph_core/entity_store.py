"""
Entity Store - Centralized entity management for OSIN Graph Core
"""

from typing import Dict, List, Optional, Set, Any
from datetime import datetime
import uuid
from .architecture import Entity, EntityType

class EntityStore:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.entity_index: Dict[EntityType, Set[str]] = {et: set() for et in EntityType}
        self.property_index: Dict[str, Dict[str, Set[str]]] = {}
    
    def add_entity(self, entity: Entity) -> str:
        """Add or update an entity in the store with comprehensive indexing"""
        if entity.id in self.entities:
            self._update_entity(entity)
        else:
            self._create_entity(entity)
        return entity.id
    
    def _create_entity(self, entity: Entity):
        """Create a new entity with full indexing"""
        self.entities[entity.id] = entity
        self.entity_index[entity.type].add(entity.id)
        self._index_properties(entity)
    
    def _update_entity(self, entity: Entity):
        """Update existing entity while maintaining index consistency"""
        old_entity = self.entities[entity.id]
        self._unindex_properties(old_entity)
        self.entities[entity.id] = entity
        self._index_properties(entity)
    
    def _index_properties(self, entity: Entity):
        for key, value in entity.properties.items():
            if key not in self.property_index:
                self.property_index[key] = {}
            val_str = str(value)
            if val_str not in self.property_index[key]:
                self.property_index[key][val_str] = set()
            self.property_index[key][val_str].add(entity.id)

    def _unindex_properties(self, entity: Entity):
        for key, value in entity.properties.items():
            val_str = str(value)
            if key in self.property_index and val_str in self.property_index[key]:
                self.property_index[key][val_str].discard(entity.id)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        return [self.entities[eid] for eid in self.entity_index.get(entity_type, set())]

    def get_entity_count(self) -> int:
        return len(self.entities)
