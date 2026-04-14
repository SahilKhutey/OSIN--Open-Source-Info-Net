"""
OSIN Graph Intelligence Core - Main FastAPI Service
Unified reasoning layer for cross-source intelligence fusion
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import uvicorn
import uuid

from .architecture import EntityType, RelationshipType, Entity
from .graph_builder import OSINGraphBuilder

app = FastAPI(
    title="OSIN Graph Intelligence Core",
    description="Unified reasoning engine for multi-modal intelligence fusion",
    version="3.6.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph orchestrator
graph = OSINGraphBuilder()

class EntityCreateRequest(BaseModel):
    type: EntityType
    properties: Dict[str, Any]
    source_modules: List[str]
    confidence: float = 1.0

class GraphQueryRequest(BaseModel):
    entity_id: Optional[str] = None
    depth: int = 1

@app.post("/ingest", status_code=201)
async def ingest_alert(data: Dict[str, Any] = Body(...)):
    """Convenience endpoint specifically for Command Center alert ingestion"""
    try:
        # Map dynamic alert data to Entity schema
        new_entity = Entity(
            id=f"alert_{data.get('id', uuid.uuid4().hex[:8])}",
            type=EntityType.THREAT_SIGNAL,
            properties={
                "message": data.get("text"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "source": data.get("source"),
                "raw_type": data.get("type")
            },
            source_modules=["command_center"],
            confidence=float(data.get("confidence", 0.8)),
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        entity_id = graph.add_entity(new_entity)
        return {"entity_id": entity_id, "status": "ingested_from_ops"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/entities", status_code=201)
async def create_entity(request: EntityCreateRequest):
    """Ingest a new entity into the intelligence graph"""
    try:
        new_entity = Entity(
            id=f"ent_{uuid.uuid4().hex[:12]}",
            type=request.type,
            properties=request.properties,
            source_modules=request.source_modules,
            confidence=request.confidence,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        entity_id = graph.add_entity(new_entity)
        return {"entity_id": entity_id, "status": "indexed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query/subgraph")
async def query_subgraph(request: GraphQueryRequest):
    """Extract a subgraph center on an entity for reasoning/visualization"""
    if not request.entity_id:
        return graph.analyze_network()
    
    subgraph = graph.get_entity_subgraph(request.entity_id, request.depth)
    return subgraph

@app.get("/analysis/network")
async def analyze_network():
    """Get global graph-theoretic situational awareness indicators"""
    return graph.analyze_network()

@app.post("/inference/predict")
async def predict_relationships(entity_id: str):
    """Run inference engine to predict potential hidden connections"""
    entity = graph.entity_store.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    predictions = graph.inference_engine.predict_relationships(entity)
    return predictions

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "entity_count": graph.entity_store.get_entity_count(),
        "relationship_count": len(graph.relationship_engine.relationships)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8020)
