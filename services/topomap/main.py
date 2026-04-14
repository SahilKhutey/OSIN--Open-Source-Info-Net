"""
OSIN Topographic Intelligence Service - Terrain and Elevation Analysis
Version: 2.1.0
Description: OpenTopoMap integration for terrain analysis and elevation intelligence
"""

import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import time
import os
import math
import redis

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('topomap_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-topomap")

# Configuration
OPENTOPOMAP_BASE_URL = "https://tile.opentopomap.org"
ELEVATION_API_URL = os.getenv("ELEVATION_API_URL", "https://api.open-elevation.com/api/v1/lookup")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DEFAULT_ZOOM_LEVEL = 12

# Analysis thresholds
SLOPE_RISK_THRESHOLD = 15  # degrees
FLOOD_ELEVATION_THRESHOLD = 50 # meters

# Redis cache
redis_client = None
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=2, decode_responses=True)
    redis_client.ping()
    logger.info(f"Redis cache connected for TopoMap at {REDIS_HOST}")
except redis.ConnectionError:
    logger.warning("Redis not available, using in-memory fallback")

class EventEnrichmentRequest(BaseModel):
    event_id: str
    lat: float
    lon: float
    text: str
    event_type: Optional[str] = None
    confidence: float = 1.0
    timestamp: float

class TopoIntelligenceResponse(BaseModel):
    event_id: str
    timestamp: str
    location: Dict[str, float]
    tile_url: str
    elevation_data: Optional[Dict]
    terrain_analysis: Dict[str, Any]
    risk_assessment: Dict[str, float]
    confidence_impact: float
    metadata: Dict[str, Any]

app = FastAPI(
    title="OSIN Topographic Intelligence Service",
    version="2.1.0"
)

start_time = time.time()

async def fetch_elevation(lat: float, lon: float) -> Optional[Dict]:
    """Fetch elevation stats for a 5-point cluster (cross-shape for slope)"""
    # 0.005 degrees is approx 500m
    offset = 0.005
    points = [
        {"latitude": lat, "longitude": lon},           # Center
        {"latitude": lat + offset, "longitude": lon},  # North
        {"latitude": lat - offset, "longitude": lon},  # South
        {"latitude": lat, "longitude": lon + offset},  # East
        {"latitude": lat, "longitude": lon - offset}   # West
    ]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ELEVATION_API_URL, json={"locations": points}, timeout=15) as r:
                if r.status != 200: return None
                data = await r.json()
                results = data.get("results", [])
                if len(results) < 5: return None
                
                elevs = [res["elevation"] for res in results]
                return {
                    "center": elevs[0],
                    "north": elevs[1],
                    "south": elevs[2],
                    "east": elevs[3],
                    "west": elevs[4],
                    "max": max(elevs),
                    "min": min(elevs)
                }
    except Exception as e:
        logger.error(f"Elevation API error: {e}")
        return None

def calculate_slope(e: Dict) -> Dict:
    """Approximate max slope in degrees"""
    # Distance between offset points (approx 555m north-south, varies east-west)
    dist = 555.0 
    
    d_ns = abs(e["north"] - e["south"]) / (dist * 2)
    d_ew = abs(e["east"] - e["west"]) / (dist * 2)
    
    max_gradient = max(d_ns, d_ew)
    slope_deg = math.degrees(math.atan(max_gradient))
    
    return {
        "max_slope_deg": slope_deg,
        "is_mountainous": slope_deg > 10,
        "is_flat": slope_deg < 2
    }

@app.post("/topo-intel", response_model=TopoIntelligenceResponse)
async def get_topo_intel(req: EventEnrichmentRequest):
    """Enrich intelligence signal with topographic context"""
    start_proc = time.time()
    
    # Check cache
    cache_key = f"topo:{round(req.lat, 4)}:{round(req.lon, 4)}"
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached: return TopoIntelligenceResponse(**json.loads(cached))
        except: pass

    elevation = await fetch_elevation(req.lat, req.lon)
    slope = calculate_slope(elevation) if elevation else {}
    
    # Risk Assessment
    risks = {
        "landslide": 0.0,
        "flooding": 0.0,
        "access_difficulty": 0.0
    }
    
    if elevation:
        # Landslide risk: High slope + context
        if slope["max_slope_deg"] > SLOPE_RISK_THRESHOLD:
            risks["landslide"] = min(1.0, (slope["max_slope_deg"] - 15) / 30)
            
        # Flood risk: Low center elevation + nearby higher points
        if elevation["center"] < FLOOD_ELEVATION_THRESHOLD:
            risks["flooding"] = 0.5 + (0.5 * (1 - (elevation["center"] / FLOOD_ELEVATION_THRESHOLD)))
            
        # Access: Steepness impact
        risks["access_difficulty"] = min(1.0, slope["max_slope_deg"] / 40)

    # Confidence Impact
    impact = 0.0
    if elevation and any(r > 0.7 for r in risks.values()):
        impact += 0.15 # Geographically validated risk baseline
        
    response = TopoIntelligenceResponse(
        event_id=req.event_id,
        timestamp=datetime.utcnow().isoformat(),
        location={"lat": req.lat, "lon": req.lon},
        tile_url=f"{OPENTOPOMAP_BASE_URL}/{{z}}/{{x}}/{{y}}.png",
        elevation_data=elevation,
        terrain_analysis={
            "slope": slope,
            "is_tactical_advantage": elevation["center"] > elevation.get("avg", 0) if elevation else False
        },
        risk_assessment=risks,
        confidence_impact=min(1.0, req.confidence + impact),
        metadata={"source": "OpenTopoMap/Open-Elevation", "version": "2.1.0"}
    )
    
    # Cache result
    if redis_client:
        try: redis_client.setex(cache_key, 86400, response.json())
        except: pass
        
    return response

@app.get("/health")
async def health():
    return {"status": "healthy", "redis": redis_client is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
