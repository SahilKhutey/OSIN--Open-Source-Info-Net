"""
OSIN Threat Intelligence API Service
FastAPI implementation with defensive security controls
"""

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import uvicorn
import os

from .core_service import ThreatIntelService
from .database import OSINDatabase

app = FastAPI(
    title="OSIN Threat Intelligence API",
    description="Defensive internet-scale reconnaissance and breach monitoring",
    version="3.5.0"
)

api_key_header = APIKeyHeader(name="X-API-Key")

class ThreatAssessmentRequest(BaseModel):
    target: str = Field(..., description="Target for defensive reconnaissance")
    context: Optional[Dict] = None

class ThreatAssessmentResponse(BaseModel):
    target: str
    timestamp: str
    threat_score: float
    threat_level: str
    components: Dict
    recommendations: List[str]

# Dependencies
def get_service():
    db = OSINDatabase()
    return ThreatIntelService(db)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "osin-threat-intel"}

@app.post("/assess", response_model=ThreatAssessmentResponse)
async def assess_threat(
    request: ThreatAssessmentRequest,
    api_key: str = Security(api_key_header),
    service: ThreatIntelService = Depends(get_service)
):
    """Perform a comprehensive defensive threat assessment"""
    if not service.security.validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid OSIN API Key")
    
    try:
        assessment = await service.assess_threat(request.target, request.context)
        if "error" in assessment:
            raise HTTPException(status_code=500, detail=assessment["error"])
        return assessment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8017)
