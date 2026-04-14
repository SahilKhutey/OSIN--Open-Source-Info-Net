"""
OSIN Digital Forensics Service - Advanced Image Analysis and Metadata Extraction
Version: 2.1.0
Description: Ghiro and EXIFlooter integration for deep image forensics and metadata analysis
"""

import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import time
import uuid
import tempfile
import shutil
from pathlib import Path
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forensics_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osin-forensics")

# Configuration
MAX_WORKERS = 4
app = FastAPI(title="OSIN Digital Forensics Service", version="2.1.0")
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
start_time = time.time()

class ForensicsResponse(BaseModel):
    event_id: str
    timestamp: str
    image_metadata: Dict[str, Any]
    exif_analysis: Dict[str, Any]
    tampering_indicators: Dict[str, Any]
    confidence_score: float
    risk_assessment: Dict[str, float]
    metadata: Dict[str, Any]

def run_exif_analysis(path: str) -> Dict:
    """Run EXIFlooter or ExifTool for deep metadata extraction"""
    try:
        # Prioritize exiftool for raw extraction
        res = subprocess.run(["exiftool", "-j", path], capture_output=True, text=True, timeout=10)
        return json.loads(res.stdout)[0] if res.returncode == 0 else {"error": res.stderr}
    except Exception as e:
        return {"error": str(e)}

def run_tamper_check(path: str) -> Dict:
    """Simplified tampering detection (Mocking Ghiro logic for ELA/Software indicators)"""
    indicators = []
    # In a real setup, we'd call 'ghiro-cl' or a custom ELA script here.
    # We'll check for software tags as a baseline indicator.
    return {"indicators": indicators}

@app.post("/forensics-analysis", response_model=ForensicsResponse)
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    event_id: Optional[str] = Form(None),
    source: Optional[str] = Form(None)
):
    start_proc = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Run forensic tools in parallel
        loop = asyncio.get_event_loop()
        exif = await loop.run_in_executor(executor, run_exif_analysis, tmp_path)
        tamper = await loop.run_in_executor(executor, run_tamper_check, tmp_path)

        # Risk Assessment logic
        tampering_risk = 0.0
        if "Software" in exif or "Photoshop" in str(exif):
            tampering_risk = 0.8
            tamper["indicators"].append("Editing Software Detected")

        # Confidence Scoring
        confidence = 0.5
        if tampering_risk > 0.5: confidence -= 0.3
        if "GPSLatitude" in exif: confidence += 0.2

        response = ForensicsResponse(
            event_id=event_id or f"forensic_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow().isoformat(),
            image_metadata={
                "filename": file.filename,
                "size": os.path.getsize(tmp_path)
            },
            exif_analysis=exif,
            tampering_indicators=tamper,
            confidence_score=max(0.0, confidence),
            risk_assessment={
                "tampering": tampering_risk,
                "metadata_integrity": 1.0 if not tamper["indicators"] else 0.4
            },
            metadata={"source": source or "console_upload", "version": "2.1.0"}
        )
        
        logger.info(f"Forensics complete for {file.filename}: integrity={confidence:.2f}")
        return response

    finally:
        background_tasks.add_task(os.remove, tmp_path)

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import json
    uvicorn.run(app, host="0.0.0.0", port=8010)
