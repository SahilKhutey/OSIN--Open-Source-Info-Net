"""
OSIN Cross-Platform Correlation Engine
Version: 2.2.0
Description: Graph-based intelligence signal correlation and event linking using ArangoDB
"""

import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os
import time
from datetime import datetime
import uuid
from arango import ArangoClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('correlation_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-correlation")

# Configuration via environment variables
ARANGO_HOST = os.getenv("ARANGO_HOST", "localhost")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", "8529"))
ARANGO_DB = os.getenv("ARANGO_DB", "osin")
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PWD = os.getenv("ARANGO_PWD", "password")

class CorrelationRequest(BaseModel):
    event_id: str = Field(..., description="Unique signal identifier")
    text: str = Field(..., description="Signal content")
    lat: Optional[float] = Field(None, description="Latitude")
    lon: Optional[float] = Field(None, description="Longitude")
    entities: List[Dict[str, str]] = Field(default_factory=list, description="Extracted entities")
    timestamp: float = Field(..., description="Signal timestamp")
    source: str = Field(..., description="Platform source")
    confidence: float = Field(..., description="Signal confidence score")

class CorrelationResponse(BaseModel):
    event_id: str
    correlated_ids: List[str]
    new_edges: int
    graph_status: str

app = FastAPI(
    title="OSIN Correlation Engine",
    description="Graph-based signal linking for cross-platform intelligence",
    version="2.2.0"
)

# ArangoDB Initialization
client = ArangoClient(hosts=f"http://{ARANGO_HOST}:{ARANGO_PORT}")
db = None

def init_db():
    global db
    try:
        sys_db = client.db('_system', username=ARANGO_USER, password=ARANGO_PWD)
        if not sys_db.has_database(ARANGO_DB):
            sys_db.create_database(ARANGO_DB)
        db = client.db(ARANGO_DB, username=ARANGO_USER, password=ARANGO_PWD)
        
        # Create collections
        if not db.has_collection('Signals'):
            db.create_collection('Signals')
        if not db.has_collection('Entities'):
            db.create_collection('Entities')
        if not db.has_graph('IntelligenceGraph'):
            db.create_graph('IntelligenceGraph', edge_definitions=[
                {
                    'edge_collection': 'CorrelatedWith',
                    'from_vertex_collections': ['Signals'],
                    'to_vertex_collections': ['Signals']
                },
                {
                    'edge_collection': 'Mentions',
                    'from_vertex_collections': ['Signals'],
                    'to_vertex_collections': ['Entities']
                }
            ])
        logger.info("ArangoDB initialized and collections created")
    except Exception as e:
        logger.error(f"Failed to initialize ArangoDB: {e}")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/correlate", response_model=CorrelationResponse)
async def correlate_signal(req: CorrelationRequest):
    """Link signal to existing graph nodes and identify cross-platform correlations"""
    if db is None:
        raise HTTPException(status_code=503, detail="Graph database not connected")
    
    # 1. Upsert Signal Node
    signal_node = {
        "_key": req.event_id,
        "text": req.text,
        "location": {"lat": req.lat, "lon": req.lon} if req.lat else None,
        "timestamp": req.timestamp,
        "source": req.source,
        "confidence": req.confidence
    }
    db.collection('Signals').upsert(signal_node)
    
    correlated_ids = []
    new_edges = 0
    
    # 2. Process Entities and create edges
    for entity in req.entities:
        ent_name = entity.get('name', '').lower().strip()
        ent_type = entity.get('type', 'GENERIC')
        
        if not ent_name: continue
        
        ent_key = f"{ent_type}_{ent_name}".replace(" ", "_")
        
        # Upsert Entity Node
        db.collection('Entities').upsert({
            "_key": ent_key,
            "name": ent_name,
            "type": ent_type
        })
        
        # Create Mentions Edge
        edge_id = f"Signals/{req.event_id}->Entities/{ent_key}"
        if not db.collection('Mentions').has(edge_id):
            db.collection('Mentions').insert({
                "_from": f"Signals/{req.event_id}",
                "_to": f"Entities/{ent_key}",
                "_key": f"{req.event_id}_{ent_key}"
            })
            new_edges += 1
            
        # 3. Find other signals mentioning the same entity (Temporal window: 24h)
        query = """
        FOR v, e IN 1..1 ANY @entity Mentions
            FILTER v._key != @signal_id
            FILTER v.timestamp > @min_ts
            RETURN v._key
        """
        results = db.aql.execute(query, bind_vars={
            "entity": f"Entities/{ent_key}",
            "signal_id": req.event_id,
            "min_ts": req.timestamp - 86400
        })
        
        for other_id in results:
            if other_id not in correlated_ids:
                correlated_ids.append(other_id)
                # Create Correlation Edge
                db.collection('CorrelatedWith').upsert({
                    "_from": f"Signals/{req.event_id}",
                    "_to": f"Signals/{other_id}",
                    "type": "shared_entity",
                    "entity": ent_name
                })
                new_edges += 1
                
    return CorrelationResponse(
        event_id=req.event_id,
        correlated_ids=correlated_ids,
        new_edges=new_edges,
        graph_status="updated"
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "graph_connected": db is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
