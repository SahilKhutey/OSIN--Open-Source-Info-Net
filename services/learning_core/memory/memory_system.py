"""
OSIN Persistent Intelligence Memory (PIM)
Long-term memory for continuous learning via LMDB and Vector Embeddings
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import lmdb
import pickle
import os

class MemoryStore:
    """Unified cognitive memory for the OSIN organism"""
    def __init__(self, db_path: str = "./osin_memory"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            
        # Use a lightweight transformer for vector search
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Initialize LMDB for multi-version concurrency
        self.env = lmdb.open(db_path, map_size=1099511627776)  # 1TB
        self._init_databases()
    
    def _init_databases(self):
        with self.env.begin(write=True) as txn:
            if not txn.get(b'episodic_index'):
                txn.put(b'episodic_index', pickle.dumps([]))
            if not txn.get(b'vector_index'):
                txn.put(b'vector_index', pickle.dumps([]))

    def store_episodic_memory(self, event: Dict[str, Any]) -> str:
        """Stores a high-fidelity intelligence episode"""
        memory_id = f"episode_{datetime.now().timestamp()}_{event.get('id', 'anon')}"
        
        # 1. Store the raw event
        with self.env.begin(write=True) as txn:
            txn.put(memory_id.encode(), pickle.dumps(event))
            index = pickle.loads(txn.get(b'episodic_index'))
            index.append(memory_id)
            txn.put(b'episodic_index', pickle.dumps(index))
            
        # 2. Extract semantic embeddings for similarity search
        self._store_vector_embedding(event)
        return memory_id

    def _store_vector_embedding(self, event: Dict[str, Any]):
        """Generates and stores the semantic fingerprint of the intelligence signal"""
        text = f"{event.get('type','')} {event.get('content','')} {json.dumps(event.get('properties', {}))}"
        embedding = self.embedding_model.encode(text)
        
        with self.env.begin(write=True) as txn:
            v_index = pickle.loads(txn.get(b'vector_index'))
            v_index.append({
                'id': event.get('id'),
                'embedding': embedding,
                'timestamp': datetime.now().isoformat()
            })
            txn.put(b'vector_index', pickle.dumps(v_index))

    def recall_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Recalls relevant intelligence context using semantic similarity"""
        query_emb = self.embedding_model.encode(query)
        with self.env.begin() as txn:
            v_index = pickle.loads(txn.get(b'vector_index'))
            
        similarities = []
        for item in v_index:
            sim = cosine_similarity([query_emb], [item['embedding']])[0][0]
            similarities.append((sim, item['id']))
            
        # Sort by similarity
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [{"id": mid, "score": float(score)} for score, mid in similarities[:limit]]

class MemoryManager:
    """Manages cognitive maintenance and cognitive pruning (forgetting)"""
    def __init__(self, store: MemoryStore):
        self.store = store
        
    async def perform_memory_maintenance(self):
        # Implementation would involve LMDB compaction and metadata pruning
        pass
