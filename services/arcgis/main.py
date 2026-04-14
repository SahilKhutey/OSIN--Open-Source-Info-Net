"""
OSIN ArcGIS Integration Service - Geospatial Intelligence Enrichment
Version: 2.1.0
Description: ArcGIS feature service integration for structured geospatial intelligence
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
import numpy as np

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arcgis_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-arcgis")

# Configuration
DEFAULT_RADIUS_KM = int(os.getenv("DEFAULT_RADIUS_KM", "50"))
MAX_FEATURES = int(os.getenv("MAX_FEATURES", "20"))

# ArcGIS Feature Services (Public verified services)
FEATURE_SERVICES = {
    "earthquakes": {
        "url": "https://services.arcgis.com/V6ZHFr6zdgNZuVG0/ArcGIS/rest/services/Earthquakes_from_last_7_days/FeatureServer/0/query",
        "name": "Recent Earthquakes",
        "category": "natural_events",
        "max_radius_km": 500
    },
    "wildfires": {
        "url": "https://services.arcgis.com/nSZVuSZjHpEZZbRo/ArcGIS/rest/services/Active_Fires/FeatureServer/0/query",
        "name": "Active Fires",
        "category": "natural_events",
        "max_radius_km": 200
    },
    "infrastructure": {
        "url": "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Power_Plants/FeatureServer/0/query",
        "name": "Power Plants",
        "category": "infrastructure",
        "max_radius_km": 100
    },
    "transportation": {
        "url": "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Major_Railroads/FeatureServer/0/query",
        "name": "Major Railroads",
        "category": "infrastructure",
        "max_radius_km": 50
    },
    "weather_alerts": {
        "url": "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/NOAA_Weather_Alerts/FeatureServer/0/query",
        "name": "Weather Alerts",
        "category": "weather",
        "max_radius_km": 300
    }
}

class EventEnrichmentRequest(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    text: str = Field(..., description="Event text content")
    event_type: Optional[str] = Field(None)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    timestamp: float = Field(..., description="Event timestamp")

class ArcGISResponse(BaseModel):
    event_id: str
    timestamp: str
    location: Dict[str, float]
    services_queried: List[str]
    features_found: Dict[str, int]
    features: Dict[str, List[Dict]]
    confidence_impact: float
    analysis: Dict[str, Any]

app = FastAPI(
    title="OSIN ArcGIS Intelligence Service",
    description="ArcGIS integration for structured geospatial intelligence enrichment",
    version="2.1.0"
)

# Service state
start_time = time.time()

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Haversine distance in kilometers"""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

async def query_arcgis_service(service_key: str, lat: float, lon: float, radius_km: float) -> List[Dict]:
    """Execute spatial query against ArcGIS Feature Service"""
    config = FEATURE_SERVICES.get(service_key)
    if not config: return []
    
    try:
        params = {
            "where": "1=1",
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "distance": min(radius_km, config.get("max_radius_km", radius_km)),
            "units": "esriSRUnit_Kilometer",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(config["url"], params=params, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    raw_features = data.get("features", [])
                    
                    processed = []
                    for feat in raw_features[:MAX_FEATURES]:
                        geom = feat.get("geometry", {})
                        f_lat, f_lon = geom.get("y", lat), geom.get("x", lon)
                        processed.append({
                            "attributes": feat.get("attributes", {}),
                            "geometry": geom,
                            "service": service_key,
                            "distance_km": calculate_distance(lat, lon, f_lat, f_lon)
                        })
                    return processed
        return []
    except Exception as e:
        logger.error(f"ArcGIS query failed for {service_key}: {e}")
        return []

def select_services(event_type: Optional[str], text: str) -> List[str]:
    """Intelligently map event context to ArcGIS layers"""
    text_lower = text.lower()
    selected = ["infrastructure"] # Base infrastructure for context
    
    mapping = {
        "fire": ["wildfires"],
        "earthquake": ["earthquakes"],
        "quake": ["earthquakes"],
        "storm": ["weather_alerts"],
        "flood": ["weather_alerts"],
        "outage": ["infrastructure"],
        "rail": ["transportation"]
    }
    
    for key, layers in mapping.items():
        if (event_type and key in event_type.lower()) or key in text_lower:
            selected.extend(layers)
            
    return list(set(selected))

@app.post("/arcgis-intel", response_model=ArcGISResponse)
async def enrich_event(req: EventEnrichmentRequest):
    """Enrich OSINT signal with authoritative GIS feature data"""
    start_proc = time.time()
    layers = select_services(req.event_type, req.text)
    
    features_data = {}
    tasks = [query_arcgis_service(l, req.lat, req.lon, DEFAULT_RADIUS_KM) for l in layers]
    results = await asyncio.gather(*tasks)
    
    for layer, res in zip(layers, results):
        features_data[layer] = res
        
    # Confidence impact calculation
    total_found = sum(len(f) for f in features_data.values())
    impact = 0.0
    if total_found > 0:
        impact = min(0.4, total_found * 0.05)
        # Add boost for extreme proximity (< 5km)
        for layer_features in features_data.values():
            if any(f.get("distance_km", 100) < 5 for f in layer_features):
                impact += 0.1
                break
                
    response_conf = min(1.0, req.confidence + impact)
    
    return ArcGISResponse(
        event_id=req.event_id,
        timestamp=datetime.utcnow().isoformat(),
        location={"lat": req.lat, "lon": req.lon},
        services_queried=layers,
        features_found={l: len(f) for l, f in features_data.items()},
        features=features_data,
        confidence_impact=response_conf,
        analysis={
            "total_features": total_found,
            "processing_time_ms": (time.time() - start_proc) * 1000
        }
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "services_available": list(FEATURE_SERVICES.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
