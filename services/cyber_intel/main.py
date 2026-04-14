"""
OSIN Cyber Intelligence Engine - Comprehensive Cyber Reconnaissance and Asset Intelligence
Version: 2.1.0
Description: Domain intelligence, infrastructure mapping, and attack surface discovery
"""

import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import time
import uuid
import subprocess
import dns.resolver
import ipaddress
from concurrent.futures import ThreadPoolExecutor

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("osin-cyber-intel")

class CyberAnalysisRequest(BaseModel):
    target: str
    analysis_type: str = "standard"
    include_active: bool = False

class CyberIntelligenceResponse(BaseModel):
    request_id: str
    timestamp: str
    target: str
    domain_intel: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    metadata: Dict[str, Any]

app = FastAPI(title="OSIN Cyber Intelligence Engine", version="2.1.0")
executor = ThreadPoolExecutor(max_workers=4)

def run_dns_queries(domain: str) -> Dict:
    """Perform basic DNS intelligence gathering"""
    results = {}
    try:
        for rtype in ['A', 'MX', 'TXT', 'NS']:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                results[rtype] = [str(r) for r in answers]
            except:
                results[rtype] = []
        return {"success": True, "records": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_risk(dns_data: Dict) -> Dict:
    """Heuristic risk assessment based on DNS exposure"""
    score = 0
    factors = []
    
    records = dns_data.get("records", {})
    if len(records.get("MX", [])) == 0:
        score += 10
        factors.append("No MX records detected")
        
    if len(records.get("TXT", [])) > 5:
        score += 5
        factors.append("High TXT record density (possible SPF/DKIM complexity)")
        
    return {
        "risk_score": min(100, score),
        "risk_level": "LOW" if score < 30 else "MEDIUM",
        "factors": factors
    }

@app.post("/analyze-cyber", response_model=CyberIntelligenceResponse)
async def analyze_cyber(request: CyberAnalysisRequest):
    start_proc = time.time()
    target = request.target.strip()
    
    try:
        loop = asyncio.get_event_loop()
        dns_res = await loop.run_in_executor(executor, run_dns_queries, target)
        risk = calculate_risk(dns_res)
        
        response = CyberIntelligenceResponse(
            request_id=f"cyber_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow().isoformat(),
            target=target,
            domain_intel={
                "dns": dns_res,
                "whois": {"status": "limited_mode", "note": "Install 'whois' binary for full audit"}
            },
            risk_assessment=risk,
            metadata={
                "processing_time_ms": (time.time() - start_proc) * 1000,
                "analysis_depth": request.analysis_type
            }
        )
        
        logger.info(f"Cyber analysis complete for {target}: Risk {risk['risk_level']}")
        return response

    except Exception as e:
        logger.error(f"Cyber analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)
