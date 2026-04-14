"""
Graph Builder - Creates and manages the unified intelligence graph
"""

import networkx as nx
import logging
from typing import Dict, List, Optional, Any
from .architecture import Entity, Relationship, RelationshipType
from .entity_store import EntityStore
from .relation_engine import RelationshipEngine
from .similarity_engine import SimilarityEngine, InferenceEngine

logger = logging.getLogger("osin-graph-builder")

class OSINGraphBuilder:
    def __init__(self):
        self.entity_store = EntityStore()
        self.relationship_engine = RelationshipEngine(self.entity_store)
        self.similarity_engine = SimilarityEngine()
        self.inference_engine = InferenceEngine(self.entity_store, self.relationship_engine)
        
        # NetworkX graph for advanced graph metrics
        self.nx_graph = nx.MultiDiGraph()
    
    def add_entity(self, entity: Entity) -> str:
        """Add entity to the reasoning graph and perform automated semantic linking"""
        entity_id = self.entity_store.add_entity(entity)
        
        # Sync to NetworkX
        self.nx_graph.add_node(entity_id, type=entity.type.value, **entity.properties)
        
        # Discovery Phase: Auto-link to existing entities
        self._auto_link_entity(entity)
        
        return entity_id
    
    def _auto_link_entity(self, entity: Entity):
        """Analyze existing graph nodes for semantic or property-based connections"""
        existing_entities = [e for e in self.entity_store.entities.values() if e.id != entity.id]
        
        for candidate in existing_entities:
            # 1. Semantic Similarity linking
            is_related, score = self.similarity_engine.are_entities_related(entity, candidate)
            if is_related:
                rel_id = self.relationship_engine.create_relationship(
                    entity.id,
                    candidate.id,
                    RelationshipType.SIMILAR_TO,
                    {"similarity_score": score},
                    score
                )
                if rel_id:
                    self.nx_graph.add_edge(entity.id, candidate.id, key=rel_id, type="SIMILAR_TO")
        
        # 2. Direct property linking (Example: Domain -> IP)
        # This is where specialized fusion logic is implemented
        pass

    def get_entity_subgraph(self, entity_id: str, depth: int = 1) -> Dict:
        """Extract a subgraph centered on a specific entity for visualization"""
        if entity_id not in self.nx_graph:
            return {"entities": [], "relationships": []}
            
        # Get nodes within depth
        nodes = {entity_id}
        for _ in range(depth):
            new_nodes = set()
            for node in nodes:
                new_nodes.update(self.nx_graph.neighbors(node))
                if hasattr(self.nx_graph, 'predecessors'):
                    new_nodes.update(self.nx_graph.predecessors(node))
            nodes.update(new_nodes)
            
        result = {
            "entities": [self.entity_store.get_entity(nid) for nid in nodes if self.entity_store.get_entity(nid)],
            "relationships": self.relationship_engine.get_relationships(entity_id=entity_id)
        }
        return result

    def analyze_network(self) -> Dict:
        """Calculate graph-theoretic indicators for intelligence situational awareness"""
        return {
            'entity_count': self.entity_store.get_entity_count(),
            'relationship_count': len(self.relationship_engine.relationships),
            'density': nx.density(self.nx_graph),
            'is_connected': nx.is_weakly_connected(self.nx_graph) if self.nx_graph.order() > 0 else True
        }
