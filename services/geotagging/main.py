"""
OSIN Geo-Tagging Service - NLP to Lat/Lon Conversion
Version: 2.1.0
Description: Converts location mentions in text to geographic coordinates using spaCy and Nominatim
"""

import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import spacy
from datetime import datetime
import time
import uuid
import json
import redis
import os
import re

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('geotagging_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-geotagging")

# Configuration via environment variables
GEOCODER_URL = os.getenv("GEOCODER_URL", "https://nominatim.openstreetmap.org/search")
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))
MAX_LOCATIONS_PER_EVENT = int(os.getenv("MAX_LOCATIONS_PER_EVENT", "5"))
USER_AGENT = os.getenv("USER_AGENT", "OSIN-Intelligence-Platform/2.1.0")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Load NLP model
try:
    # Use the small English model for speed, can be upgraded to md/lg for better accuracy
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model loaded successfully")
except OSError:
    logger.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    # In a real K8s env, this would be baked into the image

# Redis cache initialization
redis_client = None
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    redis_client.ping()
    logger.info(f"Redis cache connected at {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError:
    logger.warning("Redis not available, using in-memory fallback (simulated)")
    redis_client = None

class TextInput(BaseModel):
    text: str = Field(..., description="Text containing location mentions")
    event_id: Optional[str] = Field(None, description="Optional event identifier")
    source: Optional[str] = Field(None, description="Data source")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Initial confidence score")

class LocationResult(BaseModel):
    location: str = Field(..., description="Extracted location name")
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    confidence: float = Field(..., description="Geocoding confidence")
    source: str = Field(..., description="Geocoding source")
    country_code: Optional[str] = Field(None, description="Country code")
    importance: Optional[float] = Field(None, description="Location importance score")

class GeotaggingResponse(BaseModel):
    event_id: str = Field(..., description="Event identifier")
    locations: List[LocationResult] = Field(..., description="Geocoded locations")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    text_analysis: Dict[str, Any] = Field(..., description="NLP analysis metadata")
    timestamp: str = Field(..., description="Processing timestamp")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    nlp_model_loaded: bool = Field(..., description="NLP model status")
    geocoder_available: bool = Field(..., description="Geocoder connectivity")
    cache_enabled: bool = Field(..., description="Cache status")
    uptime_seconds: float = Field(..., description="Service uptime")

app = FastAPI(
    title="OSIN Geo-Tagging Service",
    description="NLP-based location extraction and geocoding for intelligence events",
    version="2.1.0"
)

# Service state
start_time = time.time()

def get_cache_key(location: str) -> str:
    """Generate cache key for location"""
    return f"geocode:{location.lower().strip().replace(' ', '_')}"

async def geocode_location(location: str) -> Optional[Dict]:
    """Geocode location using Nominatim with caching"""
    cache_key = get_cache_key(location)
    
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for: {location}")
                return json.loads(cached)
        except redis.RedisError:
            pass
    
    # Geocoding logic
    try:
        params = {
            "q": location,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        headers = {"User-Agent": USER_AGENT}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(GEOCODER_URL, params=params, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        result = {
                            "lat": float(data[0]["lat"]),
                            "lon": float(data[0]["lon"]),
                            "display_name": data[0]["display_name"],
                            "importance": data[0].get("importance", 0),
                            "country_code": data[0].get("address", {}).get("country_code", "").upper()
                        }
                        
                        # Cache the result
                        if redis_client:
                            try:
                                redis_client.setex(
                                    cache_key, 
                                    CACHE_TTL_HOURS * 3600, 
                                    json.dumps(result)
                                )
                            except redis.RedisError:
                                pass
                        
                        return result
        return None
        
    except Exception as e:
        logger.error(f"Geocoding failed for {location}: {e}")
        return None

def extract_locations(text: str) -> List[str]:
    """Extract location entities from text using spaCy NER and Regex fallbacks"""
    locations = set()
    
    # Method 1: spaCy NER
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC", "FAC"]:
            locations.add(ent.text.strip())
    
    # Method 2: Regex patterns for "near [Location]" or "[Location] City/State"
    patterns = [
        r'\b(in|near|at|around)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s+(County|City|State|Province|Region))',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            locations.add(match.group(2).strip())
    
    # Filter common false positives
    false_positives = {"Police", "Fire", "Department", "Station", "Center", "Building", "Reported"}
    filtered = [loc for loc in locations if loc not in false_positives and len(loc) > 1]
    
    # Sort by specificity (length)
    filtered.sort(key=len, reverse=True)
    
    return filtered[:MAX_LOCATIONS_PER_EVENT]

def calculate_confidence(location: str, geocode_result: Dict, text: str) -> float:
    """Calculate geocoding confidence score"""
    base = 0.7
    
    # Boost for string match
    if location.lower() in text.lower():
        base += 0.1
    
    # Boost based on geocoder importance
    importance = geocode_result.get("importance", 0)
    base += min(0.2, importance * 0.2)
    
    return min(1.0, base)

@app.post("/geotag", response_model=GeotaggingResponse)
async def geotag_text(input_data: TextInput):
    """Primary endpoint for text-to-coordinate conversion"""
    start_proc = time.time()
    
    if not input_data.text or len(input_data.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Input text too short")
    
    event_id = input_data.event_id or f"evt_{uuid.uuid4().hex[:8]}"
    
    # Extraction
    extracted = extract_locations(input_data.text)
    
    # Geocoding
    results = []
    for loc in extracted:
        try:
            geo_res = await geocode_location(loc)
            if geo_res:
                conf = calculate_confidence(loc, geo_res, input_data.text)
                results.append(LocationResult(
                    location=loc,
                    lat=geo_res["lat"],
                    lon=geo_res["lon"],
                    confidence=conf,
                    source="OpenStreetMap/Nominatim",
                    country_code=geo_res.get("country_code"),
                    importance=geo_res.get("importance")
                ))
        except Exception as e:
            logger.error(f"Geocoding error for {loc}: {e}")
            
    proc_time = (time.time() - start_proc) * 1000
    
    return GeotaggingResponse(
        event_id=event_id,
        locations=results,
        processing_time_ms=proc_time,
        text_analysis={
            "extracted_count": len(extracted),
            "geocoded_count": len(results),
            "locations_found": extracted
        },
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health monitoring"""
    geocoder_ok = False
    try:
        # Simple probe for geocoder
        async with aiohttp.ClientSession() as session:
            async with session.get(GEOCODER_URL, params={"q": "Berlin", "format": "json", "limit": 1}, timeout=3) as r:
                geocoder_ok = r.status == 200
    except:
        pass
        
    return HealthResponse(
        status="healthy",
        nlp_model_loaded=nlp is not None,
        geocoder_available=geocoder_ok,
        cache_enabled=redis_client is not None,
        uptime_seconds=time.time() - start_time
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        workers=2,
        log_level="info"
    )
