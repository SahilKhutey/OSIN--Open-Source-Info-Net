"""
Similarity Engine - Advanced semantic and pattern matching for OSIN Graph Core
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from .architecture import Entity, RelationshipType, EntityType

# Configure logger
logger = logging.getLogger("osin-graph-similarity")

class SimilarityEngine:
    def __init__(self):
        # In a production environment, we would load the model here
        # self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.model = None
        self.similarity_cache: Dict[Tuple[str, str], float] = {}
        logger.info("Similarity Engine Initialized (Model Stubbed for Performance)")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two text inputs (Simple fallback)"""
        if not text1 or not text2:
            return 0.0
        
        # Simple Jaccard similarity fallback if model is not loaded
        t1 = set(text1.lower().split())
        t2 = set(text2.lower().split())
        intersection = t1.intersection(t2)
        union = t1.union(t2)
        return len(intersection) / len(union) if union else 0.0
    
    def are_entities_related(self, 
                           entity1: Entity, 
                           entity2: Entity, 
                           threshold: float = 0.7) -> Tuple[bool, float]:
        """Determine if two entities are related based on semantic similarity of properties"""
        text1 = self._extract_comparison_text(entity1)
        text2 = self._extract_comparison_text(entity2)
        
        similarity = self.calculate_similarity(text1, text2)
        return similarity > threshold, similarity
    
    def _extract_comparison_text(self, entity: Entity) -> str:
        """Extract relevant text from entity properties for semantic comparison"""
        parts = [entity.type.value]
        for val in entity.properties.values():
            if isinstance(val, str):
                parts.append(val)
        return " ".join(parts)

class InferenceEngine:
    """Advanced inference and predictive relationship discovery"""
    def __init__(self, entity_store, relationship_engine):
        self.entity_store = entity_store
        self.relationship_engine = relationship_engine
        self.similarity_engine = SimilarityEngine()
    
    def predict_relationships(self, entity: Entity) -> List[Dict]:
        """Predict potential hidden relationships for an entity"""
        predictions = []
        all_entities = [e for e in self.entity_store.entities.values() if e.id != entity.id]
        
        # Find top 5 similar entities
        for candidate in all_entities:
            related, score = self.similarity_engine.are_entities_related(entity, candidate)
            if related:
                predictions.append({
                    'target_id': candidate.id,
                    'relationship_type': RelationshipType.SIMILAR_TO.value,
                    'confidence': score,
                    'reason': f"Semantic similarity detected ({int(score*100)}%)"
                })
        
        return sorted(predictions, key=lambda x: x['confidence'], reverse=True)[:5]
