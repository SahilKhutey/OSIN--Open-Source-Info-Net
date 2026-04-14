"""
OSIN Deduplication Service - Semantic Event Clustering Engine
Version: 2.1.0
Description: Identifies duplicate intelligence signals using semantic similarity
"""

import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import uuid
from datetime import datetime
import json
import os

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deduplication_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-deduplication")

# Configuration via environment variables
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

# Global resources
model = None
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

class Event(BaseModel):
    id: str = Field(..., description="Unique event identifier")
    text: str = Field(..., description="Event text content for similarity analysis")
    source: str = Field("unknown", description="Data source identifier")
    timestamp: Optional[float] = Field(None, description="Event timestamp")
    metadata: Dict[str, Any] = Field({}, description="Additional event metadata")
    entities: Optional[List[Dict]] = Field(None, description="Extracted entities")

class EventBatch(BaseModel):
    events: List[Event] = Field(..., description="Batch of events to deduplicate")
    batch_id: Optional[str] = Field(None, description="Optional batch identifier")
    priority: int = Field(1, description="Processing priority (1-10)")

class DeduplicationResponse(BaseModel):
    clusters: List[List[str]] = Field(..., description="Groups of duplicate event IDs")
    batch_id: str = Field(..., description="Batch identifier")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    total_events: int = Field(..., description="Number of input events")
    unique_events: int = Field(..., description="Number of unique event clusters")
    similarity_threshold: float = Field(..., description="Similarity threshold used")
    timestamp: str = Field(..., description="Processing completion timestamp")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="ML model availability")
    model_name: str = Field(..., description="Model identifier")
    uptime_seconds: float = Field(..., description="Service uptime")
    total_batches_processed: int = Field(..., description="Total batches processed")
    avg_processing_time_ms: float = Field(..., description="Average processing time")

class MetricsResponse(BaseModel):
    max_workers: int = Field(..., description="Thread pool size")
    batch_size: int = Field(..., description="Maximum batch size")
    model: str = Field(..., description="Model information")
    similarity_threshold: float = Field(..., description="Current similarity threshold")
    memory_usage_mb: float = Field(..., description="Current memory usage")

app = FastAPI(
    title="OSIN Deduplication Service",
    description="Semantic event deduplication engine for intelligence signals",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Service state
start_time = time.time()
total_batches_processed = 0
total_processing_time = 0.0

@app.on_event("startup")
async def startup_event():
    """Initialize service resources on startup"""
    global model
    logger.info(f"Loading sentence transformer model: {MODEL_NAME}")
    try:
        model = SentenceTransformer(MODEL_NAME)
        # Warm up the model
        warmup_texts = ["warmup text for model initialization"]
        model.encode(warmup_texts)
        logger.info("Model loaded and warmed up successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        # In Kubernetes environment, we want the pod to restart on model load failure
        raise RuntimeError(f"Model initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Shutting down deduplication service")
    executor.shutdown(wait=False)

def process_batch_sync(events: List[Event], batch_id: str) -> Dict[str, Any]:
    """Synchronous batch processing for thread pool execution"""
    start_time_proc = time.time()
    
    if not events:
        return {
            "clusters": [],
            "processing_time_ms": 0,
            "total_events": 0,
            "unique_events": 0
        }
    
    texts = [event.text for event in events]
    ids = [event.id for event in events]
    
    try:
        # Generate embeddings with batching for memory efficiency
        embeddings = model.encode(
            texts, 
            batch_size=EMBEDDING_BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        # Cluster similar events using connected components approach
        clusters = []
        visited = set()
        
        for i in range(len(texts)):
            if i in visited:
                continue
                
            cluster = [ids[i]]
            visited.add(i)
            
            # Find all similar events
            for j in range(len(texts)):
                if (j not in visited and 
                    similarity_matrix[i][j] > SIMILARITY_THRESHOLD):
                    cluster.append(ids[j])
                    visited.add(j)
            
            clusters.append(cluster)
        
        processing_time = (time.time() - start_time_proc) * 1000
        
        logger.debug(
            f"Batch {batch_id}: Processed {len(events)} events -> "
            f"{len(clusters)} clusters in {processing_time:.2f}ms"
        )
        
        return {
            "clusters": clusters,
            "processing_time_ms": processing_time,
            "total_events": len(events),
            "unique_events": len(clusters)
        }
        
    except Exception as e:
        logger.error(f"Batch processing failed for {batch_id}: {e}")
        raise

@app.post("/deduplicate", response_model=DeduplicationResponse)
async def deduplicate(batch: EventBatch, background_tasks: BackgroundTasks):
    """Deduplicate a batch of events using semantic similarity"""
    global total_batches_processed, total_processing_time
    
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not batch.events:
        raise HTTPException(status_code=400, detail="No events provided")
    
    batch_id = batch.batch_id or f"batch_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    logger.info(
        f"Processing batch {batch_id} with {len(batch.events)} events "
        f"(priority: {batch.priority})"
    )
    
    # Process in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            executor, process_batch_sync, batch.events, batch_id
        )
    except Exception as e:
        logger.error(f"Execution failed for batch {batch_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")
    
    # Update metrics
    total_batches_processed += 1
    total_processing_time += result["processing_time_ms"]
    
    logger.info(
        f"Batch {batch_id} completed: {result['unique_events']} "
        f"unique events from {result['total_events']} total "
        f"in {result['processing_time_ms']:.2f}ms"
    )
    
    return DeduplicationResponse(
        clusters=result["clusters"],
        batch_id=batch_id,
        processing_time_ms=result["processing_time_ms"],
        total_events=result["total_events"],
        unique_events=result["unique_events"],
        similarity_threshold=SIMILARITY_THRESHOLD,
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/deduplicate/bulk")
async def deduplicate_bulk(batches: List[EventBatch]):
    """Process multiple batches concurrently"""
    results = []
    # Process sequentially for simplicity, or use gather for parallelism if thread pool allows
    for batch in batches:
        try:
            result = await deduplicate(batch, BackgroundTasks())
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process batch in bulk: {e}")
            results.append({"error": str(e), "batch_id": batch.batch_id})
    
    return {"results": results}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with service metrics"""
    uptime = time.time() - start_time
    divisor = max(total_batches_processed, 1)
    avg_processing_time = total_processing_time / divisor
    
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        model_name=MODEL_NAME,
        uptime_seconds=uptime,
        total_batches_processed=total_batches_processed,
        avg_processing_time_ms=avg_processing_time
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Service metrics and configuration endpoint"""
    try:
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        memory_usage = 0.0
    
    return MetricsResponse(
        max_workers=MAX_WORKERS,
        batch_size=BATCH_SIZE,
        model=MODEL_NAME,
        similarity_threshold=SIMILARITY_THRESHOLD,
        memory_usage_mb=memory_usage
    )

@app.get("/config")
async def get_config():
    """Get current service configuration"""
    return {
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "max_batch_size": BATCH_SIZE,
        "model": MODEL_NAME,
        "embedding_batch_size": EMBEDDING_BATCH_SIZE
    }

@app.post("/config/update")
async def update_config(new_threshold: Optional[float] = None):
    """Update service configuration (restricted in production)"""
    global SIMILARITY_THRESHOLD
    if new_threshold is not None and 0.1 <= new_threshold <= 1.0:
        old_threshold = SIMILARITY_THRESHOLD
        SIMILARITY_THRESHOLD = new_threshold
        logger.info(f"Similarity threshold updated: {old_threshold} -> {new_threshold}")
        return {"message": f"Threshold updated to {new_threshold}"}
    return {"message": "Invalid threshold value"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        workers=2,
        log_level="info",
        timeout_keep_alive=30
    )
