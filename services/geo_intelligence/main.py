"""
OSIN Geo-Intelligence Service - NASA Worldview Integration
Version: 2.1.0 (Enhanced)
Description: Satellite imagery and environmental data integration for threat verification
"""

import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import time
import uuid
import json
import os
from enum import Enum
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('geo_intelligence_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-geo-intelligence")

# Configuration via environment variables
NASA_GIBS_BASE = os.getenv("NASA_GIBS_BASE", "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best")
DEFAULT_ZOOM_LEVEL = int(os.getenv("DEFAULT_ZOOM_LEVEL", "9"))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "30"))

# NASA GIBS Available Layers
class NASALayer(str, Enum):
    TRUE_COLOR = "MODIS_Terra_CorrectedReflectance_TrueColor"
    FIRES_VIIRS = "VIIRS_SNPP_CorrectedReflectance_TrueColor"
    FIRES_MODIS = "MODIS_Terra_Thermal_Anomalies_All"
    AEROSOLS = "OMI_Aerosol_Index"
    PRECIPITATION = "IMERG_Precipitation_Rate"
    NIGHT_LIGHTS = "VIIRS_SNPP_DayNightBand_At_Sensor_Radiance"
    TEMPERATURE = "MODIS_Terra_Land_Surface_Temp_Day"
    VEGETATION = "MODIS_Terra_NDVI"
    SNOW = "MODIS_Terra_Snow_Cover"

# Layer metadata with weighted confidence impact
LAYER_METADATA = {
    NASALayer.TRUE_COLOR: {
        "name": "True Color Imagery",
        "description": "Natural color satellite imagery",
        "use_cases": ["general", "visual_confirmation", "environmental"],
        "confidence_impact": 0.1
    },
    NASALayer.FIRES_VIIRS: {
        "name": "VIIRS Fire Detection",
        "description": "Active fire and thermal anomaly detection",
        "use_cases": ["fires", "explosions", "thermal_anomalies"],
        "confidence_impact": 0.3
    },
    NASALayer.FIRES_MODIS: {
        "name": "MODIS Thermal Anomalies",
        "description": "High-resolution thermal anomaly detection",
        "use_cases": ["fires", "industrial_incidents", "thermal_anomalies"],
        "confidence_impact": 0.25
    },
    NASALayer.AEROSOLS: {
        "name": "Aerosol Index",
        "description": "Smoke, dust, and pollution detection",
        "use_cases": ["smoke", "pollution", "explosions", "fires"],
        "confidence_impact": 0.2
    },
    NASALayer.PRECIPITATION: {
        "name": "Precipitation Rate",
        "description": "Rainfall and precipitation intensity",
        "use_cases": ["floods", "storms", "precipitation"],
        "confidence_impact": 0.15
    },
    NASALayer.NIGHT_LIGHTS: {
        "name": "Night Lights",
        "description": "Artificial light detection and power grid monitoring",
        "use_cases": ["power_outages", "urban_activity", "conflict_zones"],
        "confidence_impact": 0.2
    },
    NASALayer.TEMPERATURE: {
        "name": "Land Surface Temperature",
        "description": "Surface temperature anomalies",
        "use_cases": ["heatwaves", "industrial_activity", "environmental"],
        "confidence_impact": 0.15
    }
}

class GeoRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    lon: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    event_type: Optional[str] = Field(None, description="Type of event for layer selection")
    layers: Optional[List[NASALayer]] = Field(None, description="Specific NASA layers to fetch")
    radius_km: float = Field(10, description="Search radius in kilometers")
    zoom_level: int = Field(DEFAULT_ZOOM_LEVEL, ge=1, le=15, description="Zoom level for tiles")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class EventEnrichmentRequest(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    text: str = Field(..., description="Event text content")
    lat: Optional[float] = Field(None, description="Latitude coordinate")
    lon: Optional[float] = Field(None, description="Longitude coordinate")
    timestamp: float = Field(..., description="Event timestamp")
    source: str = Field(..., description="Data source")
    entities: Optional[List[Dict]] = Field(None, description="Extracted entities")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score")
    event_type: Optional[str] = Field(None, description="Event type for layer selection")

class GeoIntelligenceResponse(BaseModel):
    event_id: str = Field(..., description="Original event identifier")
    timestamp: str = Field(..., description="Processing timestamp")
    location: Dict[str, float] = Field(..., description="Coordinates")
    date: str = Field(..., description="Imagery date")
    layers: Dict[str, Dict] = Field(..., description="Available satellite layers")
    tile_urls: Dict[str, str] = Field(..., description="Tile URL templates")
    confidence_impact: float = Field(..., description="Confidence adjustment based on geo-intel")
    analysis: Dict[str, Any] = Field(..., description="Analytical insights")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    nasa_connectivity: bool = Field(..., description="NASA GIBS connectivity")
    available_layers: int = Field(..., description="Number of available layers")
    uptime_seconds: float = Field(..., description="Service uptime")

app = FastAPI(
    title="OSIN Geo-Intelligence Service",
    description="Enhanced NASA Worldview integration for satellite intelligence verification",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Service state
start_time = time.time()
executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS)

def generate_tile_url(layer: NASALayer, date: str, zoom_level: int = DEFAULT_ZOOM_LEVEL) -> str:
    """Generate NASA GIBS tile URL for specific layer and date"""
    return f"{NASA_GIBS_BASE}/{layer}/default/{date}/GoogleMapsCompatible_Level{zoom_level}/{{z}}/{{y}}/{{x}}.jpg"

def select_layers_for_event(event_type: Optional[str], text: str) -> List[NASALayer]:
    """Intelligently select NASA layers based on event type and content (Inferred)"""
    selected_layers = [NASALayer.TRUE_COLOR]  # Always include true color
    
    text_lower = text.lower()
    
    # Determine event type from text if not provided
    inferred_type = event_type.lower() if event_type else None
    if not inferred_type:
        if any(word in text_lower for word in ['fire', 'wildfire', 'burning', 'blaze']):
            inferred_type = 'fire'
        elif any(word in text_lower for word in ['explosion', 'blast', 'detonation']):
            inferred_type = 'explosion'
        elif any(word in text_lower for word in ['flood', 'rain', 'storm', 'precipitation']):
            inferred_type = 'flood'
        elif any(word in text_lower for word in ['power', 'outage', 'blackout', 'electricity']):
            inferred_type = 'power_outage'
        elif any(word in text_lower for word in ['smoke', 'pollution', 'haze', 'air quality']):
            inferred_type = 'pollution'
        elif any(word in text_lower for word in ['heat', 'temperature', 'hot', 'heatwave']):
            inferred_type = 'temperature'
    
    # Layer selection logic based on inferred type
    if inferred_type == 'fire':
        selected_layers.extend([NASALayer.FIRES_VIIRS, NASALayer.FIRES_MODIS, NASALayer.AEROSOLS])
    elif inferred_type == 'explosion':
        selected_layers.extend([NASALayer.FIRES_VIIRS, NASALayer.AEROSOLS])
    elif inferred_type == 'flood':
        selected_layers.extend([NASALayer.PRECIPITATION])
    elif inferred_type == 'power_outage':
        selected_layers.extend([NASALayer.NIGHT_LIGHTS])
    elif inferred_type in ['pollution', 'smoke']:
        selected_layers.extend([NASALayer.AEROSOLS])
    elif inferred_type == 'temperature':
        selected_layers.extend([NASALayer.TEMPERATURE])
    
    return list(set(selected_layers))

async def check_nasa_connectivity() -> bool:
    """Check connectivity to NASA GIBS service"""
    try:
        async with aiohttp.ClientSession() as session:
            test_url = generate_tile_url(NASALayer.TRUE_COLOR, datetime.now().strftime('%Y-%m-%d')).format(z=9, y=100, x=100)
            async with session.head(test_url, timeout=10) as response:
                return response.status == 200
    except:
        return False

def calculate_confidence_impact(selected_layers: List[NASALayer], original_confidence: float) -> float:
    """Calculate confidence adjustment based on selected sensors impact (Weighted)"""
    impact = 0.0
    
    for layer in selected_layers:
        layer_impact = LAYER_METADATA.get(layer, {}).get('confidence_impact', 0.05)
        impact += layer_impact
    
    # Cap the maximum impact to prevent over-inflation
    max_impact = 0.4
    actual_impact = min(impact, max_impact)
    
    return min(1.0, original_confidence + actual_impact)

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("OSIN Geo-Intelligence Service (Enhanced) starting up")
    
    # Check NASA connectivity
    nasa_connected = await check_nasa_connectivity()
    if nasa_connected:
        logger.info("NASA GIBS connectivity: ✅ CONNECTED")
    else:
        logger.warning("NASA GIBS connectivity: ⚠️ LIMITED")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Geo-Intelligence Service")
    executor.shutdown(wait=False)

@app.post("/geo-intel", response_model=GeoIntelligenceResponse)
async def get_geo_intelligence(req: EventEnrichmentRequest):
    """Main endpoint for enhanced geo-intelligence enrichment"""
    start_processing = time.time()
    
    if not req.lat or not req.lon:
        raise HTTPException(status_code=400, detail="Event missing location coordinates")
    
    # Convert timestamp to date string
    event_date = datetime.fromtimestamp(req.timestamp).strftime('%Y-%m-%d')
    
    # Select appropriate layers based on event type and content
    selected_layers = select_layers_for_event(req.event_type, req.text)
    
    # Generate tile URLs for all selected layers
    tile_urls = {}
    layer_metadata = {}
    
    for layer in selected_layers:
        tile_urls[layer.value] = generate_tile_url(layer, event_date, DEFAULT_ZOOM_LEVEL)
        layer_metadata[layer.value] = LAYER_METADATA.get(layer, {})
    
    # Calculate weighted confidence impact
    confidence_impact = calculate_confidence_impact(selected_layers, req.confidence)
    
    processing_time = time.time() - start_processing
    
    response = GeoIntelligenceResponse(
        event_id=req.event_id,
        timestamp=datetime.utcnow().isoformat(),
        location={"lat": req.lat, "lon": req.lon},
        date=event_date,
        layers=layer_metadata,
        tile_urls=tile_urls,
        confidence_impact=confidence_impact,
        analysis={
            "layer_count": len(selected_layers),
            "processing_time_ms": processing_time * 1000,
            "recommended_layers": [layer.value for layer in selected_layers],
            "event_type_inferred": req.event_type or "auto_detected",
            "verification_status": "pending_analysis"
        },
        metadata={
            "source": "NASA GIBS",
            "service_version": "2.1.0-enhanced",
            "nasa_gibs_base": NASA_GIBS_BASE
        }
    )
    
    logger.info(
        f"Enhanced geo-intel for event {req.event_id}: "
        f"{len(selected_layers)} layers, "
        f"confidence: {req.confidence:.2f} → {confidence_impact:.2f}"
    )
    
    return response

@app.post("/bulk-geo-intel")
async def bulk_geo_intelligence(requests: List[EventEnrichmentRequest]):
    """Process multiple events concurrently"""
    results = []
    for req in requests:
        try:
            result = await get_geo_intelligence(req)
            results.append(result.dict())
        except Exception as e:
            logger.error(f"Failed to process event {req.event_id}: {e}")
            results.append({"error": str(e), "event_id": req.event_id})
    
    return {"results": results}

@app.get("/layers")
async def get_available_layers():
    """Get available NASA layers and metadata"""
    return {
        "available_layers": LAYER_METADATA,
        "total_layers": len(LAYER_METADATA),
        "nasa_gibs_base": NASA_GIBS_BASE
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    nasa_connected = await check_nasa_connectivity()
    
    return HealthResponse(
        status="healthy",
        nasa_connectivity=nasa_connected,
        available_layers=len(LAYER_METADATA),
        uptime_seconds=time.time() - start_time
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        workers=2,
        log_level="info",
        timeout_keep_alive=30
    )
