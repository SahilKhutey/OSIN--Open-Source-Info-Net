"""
OSIN Pic2Map Intelligence Service - Image Geolocation and EXIF Analysis
Version: 2.1.0
Description: Image geolocation, EXIF extraction, and visual analysis for intelligence
"""

import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import time
import uuid
import json
import tempfile
import shutil
from pathlib import Path
import PIL.Image
import PIL.ExifTags
import reverse_geocoder as rg
import numpy as np

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pic2map_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-pic2map")

class ImageIntelligenceResponse(BaseModel):
    event_id: str
    timestamp: str
    image_metadata: Dict[str, Any]
    exif_data: Dict[str, Any]
    gps_data: Optional[Dict] = None
    location_analysis: Dict[str, Any]
    visual_analysis: Dict[str, Any]
    confidence_score: float
    metadata: Dict[str, Any]

app = FastAPI(
    title="OSIN Pic2Map Intelligence Service",
    version="2.1.0"
)

start_time = time.time()

def convert_to_degrees(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def extract_gps(exif):
    """Extract decimal GPS from EXIF dictionary"""
    if not exif or "GPSInfo" not in exif:
        return None
        
    gps_info = exif["GPSInfo"]
    gps_tag_info = {}
    for key in gps_info:
        decode = PIL.ExifTags.GPSTAGS.get(key, key)
        gps_tag_info[decode] = gps_info[key]
        
    if "GPSLatitude" in gps_tag_info and "GPSLongitude" in gps_tag_info:
        lat = convert_to_degrees(gps_tag_info["GPSLatitude"])
        if gps_tag_info.get("GPSLatitudeRef") == "S": lat = -lat
        
        lon = convert_to_degrees(gps_tag_info["GPSLongitude"])
        if gps_tag_info.get("GPSLongitudeRef") == "W": lon = -lon
        
        return {"lat": lat, "lon": lon}
    return None

@app.post("/image-intel", response_model=ImageIntelligenceResponse)
async def analyze_image(
    file: UploadFile = File(...),
    event_id: Optional[str] = Form(None),
    source: Optional[str] = Form(None)
):
    start_proc = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        img = PIL.Image.open(tmp_path)
        exif_raw = img._getexif()
        exif = {}
        if exif_raw:
            for tag, value in exif_raw.items():
                decoded = PIL.ExifTags.TAGS.get(tag, tag)
                if isinstance(value, bytes): value = value.hex()
                exif[decoded] = value

        gps = extract_gps(exif)
        
        # Reverse Geocoding
        location_name = "Unknown"
        if gps:
            geo_results = rg.search((gps["lat"], gps["lon"]))
            if geo_results:
                res = geo_results[0]
                location_name = f"{res['name']}, {res['admin1']}, {res['cc']}"

        # Confidence Scoring
        confidence = 0.3 # Base
        if gps: confidence += 0.5
        if "DateTime" in exif: confidence += 0.1
        if "Model" in exif: confidence += 0.1

        response = ImageIntelligenceResponse(
            event_id=event_id or f"img_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow().isoformat(),
            image_metadata={
                "filename": file.filename,
                "format": img.format,
                "size": img.size
            },
            exif_data=exif,
            gps_data=gps,
            location_analysis={
                "location_name": location_name,
                "is_geolocated": gps is not None
            },
            visual_analysis={
                "aspect_ratio": img.size[0] / img.size[1]
            },
            confidence_score=min(1.0, confidence),
            metadata={"source": source or "manual_upload", "version": "2.1.0"}
        )
        
        logger.info(f"Analyzed image {file.filename}: geolocated={gps is not None}")
        return response

    finally:
        if Path(tmp_path).exists():
            Path(tmp_path).unlink()

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
