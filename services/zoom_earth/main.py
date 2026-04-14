"""
OSIN Zoom Earth Integration Service - Real-time Weather & Environmental Intelligence
Version: 2.1.0
Description: Real-time weather, storm tracking, and environmental monitoring integration
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

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zoom_earth_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-zoom-earth")

# Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "PLACEHOLDER")
WEATHER_TILE_BASE = "https://tile.openweathermap.org/map"
DEFAULT_ZOOM_LEVEL = int(os.getenv("DEFAULT_ZOOM_LEVEL", "6"))

# Weather layer definitions
WEATHER_LAYERS = {
    "clouds": {"name": "Cloud Cover", "tile_path": "clouds_new", "opacity": 0.6},
    "precipitation": {"name": "Precipitation", "tile_path": "precipitation_new", "opacity": 0.7},
    "wind": {"name": "Wind Speed", "tile_path": "wind_new", "opacity": 0.5},
    "temp": {"name": "Temperature", "tile_path": "temp_new", "opacity": 0.6},
    "pressure": {"name": "Pressure", "tile_path": "pressure_new", "opacity": 0.5}
}

class EventEnrichmentRequest(BaseModel):
    event_id: str
    lat: float
    lon: float
    text: str
    event_type: Optional[str] = None
    confidence: float = 1.0
    timestamp: float

class WeatherIntelligenceResponse(BaseModel):
    event_id: str
    timestamp: str
    location: Dict[str, float]
    weather_layers: Dict[str, Dict]
    current_weather: Optional[Dict]
    severe_alerts: List[Dict]
    confidence_impact: float
    analysis: Dict[str, Any]

app = FastAPI(
    title="OSIN Zoom Earth Weather Service",
    version="2.1.0"
)

start_time = time.time()

async def get_current_weather(lat: float, lon: float) -> Optional[Dict]:
    """Fetch live atmospheric data from OpenWeatherMap"""
    if OPENWEATHER_API_KEY == "PLACEHOLDER": return None
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    return {
                        "temp": data.get("main", {}).get("temp"),
                        "humidity": data.get("main", {}).get("humidity"),
                        "wind_speed": data.get("wind", {}).get("speed"),
                        "conditions": data.get("weather", [{}])[0].get("description"),
                        "visibility": data.get("visibility")
                    }
        return None
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return None

async def get_noaa_alerts(lat: float, lon: float) -> List[Dict]:
    """Fetch severe weather alerts from NOAA (US Coverage)"""
    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    headers = {"User-Agent": "(OSIN-Intelligence-Platform, contact@osin.net)"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    alerts = []
                    for feature in data.get("features", []):
                        props = feature.get("properties", {})
                        alerts.append({
                            "event": props.get("event"),
                            "severity": props.get("severity"),
                            "description": props.get("headline")
                        })
                    return alerts
        return []
    except Exception as e:
        logger.warning(f"NOAA alerts unavailable: {e}")
        return []

@app.post("/weather-intel", response_model=WeatherIntelligenceResponse)
async def enrich_event(req: EventEnrichmentRequest):
    """Correlate intelligence signal with real-time environmental data"""
    start_proc = time.time()
    
    # Concurrent data gathering
    current_task = get_current_weather(req.lat, req.lon)
    alerts_task = get_noaa_alerts(req.lat, req.lon)
    current_weather, alerts = await asyncio.gather(current_task, alerts_task)
    
    # Resolve weather layers (Tiles generation)
    # Note: Modern dashboard clients often fetch tiles directly; 
    # we provide the metadata/URLs here.
    layers = {}
    for key, cfg in WEATHER_LAYERS.items():
        layers[key] = {
            "name": cfg["name"],
            "tile_url": f"{WEATHER_TILE_BASE}/{cfg['tile_path']}/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}",
            "opacity": cfg["opacity"]
        }
        
    # Analyze confidence impact
    # Example: If signal is "flood" and we have a "Flash Flood Warning", boost confidence.
    impact = 0.0
    text_lower = req.text.lower()
    
    if alerts:
        impact += 0.2
        for alert in alerts:
            if alert["event"].lower() in text_lower:
                impact += 0.2
                break
                
    if current_weather and current_weather.get("wind_speed", 0) > 15: # High wind context
        if any(w in text_lower for w in ["wind", "storm", "damage"]):
            impact += 0.1
            
    return WeatherIntelligenceResponse(
        event_id=req.event_id,
        timestamp=datetime.utcnow().isoformat(),
        location={"lat": req.lat, "lon": req.lon},
        weather_layers=layers,
        current_weather=current_weather,
        severe_alerts=alerts,
        confidence_impact=min(1.0, req.confidence + impact),
        analysis={
            "processing_time_ms": (time.time() - start_proc) * 1000,
            "has_warnings": len(alerts) > 0,
            "alerts_count": len(alerts)
        },
        metadata={"source": "OpenWeatherMap/NOAA", "service": "zoom_earth_intel"}
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "api_configured": OPENWEATHER_API_KEY != "PLACEHOLDER"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
