import os
import logging
import httpx
import time
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, start_http_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OSIN-ZeroTrustGate")

# Metrics
AUTH_SUCCESS = Counter('auth_success_total', 'Successful authentications', ['client'])
AUTH_FAILURE = Counter('auth_failure_total', 'Failed authentications', ['reason'])
PROXY_LATENCY = Histogram('proxy_request_latency_seconds', 'Gateway proxy latency', ['target'])

# Configuration
API_KEYS = {
    # In production, these should be securely stored (e.g. env or vault)
    os.getenv("GATEWAY_KEY_INTERNAL", "osin-internal-v12"): "internal",
    os.getenv("GATEWAY_KEY_XR", "osin-xr-v12"): "xr-client"
}

# Destinations (Internal K8s DNS)
TARGET_MAP = {
    "api": "http://backend-service.osin-system.svc.cluster.local:8000",
    "xr": "http://xr-bridge.osin-system.svc.cluster.local:3001",
    "anomaly": "http://anomaly-service.osin-system.svc.cluster.local:8004"
}

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="OSIN v12 Zero Trust Gateway")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Security
header_scheme = APIKeyHeader(name="X-OSIN-API-KEY")

async def validate_api_key(api_key: str = Security(header_scheme)):
    if api_key in API_KEYS:
        client = API_KEYS[api_key]
        AUTH_SUCCESS.labels(client=client).inc()
        return client
    AUTH_FAILURE.labels(reason="invalid_key").inc()
    raise HTTPException(status_code=403, detail="Invalid Intelligence Credentials")

@app.middleware("http")
async def apply_security_posture(request: Request, call_next):
    # mTLS Check (In K8s, usually handled by Istio/Ingress or sidecar)
    # Here we simulate certificate validation
    cert = request.scope.get('ssl', {}).get('client_cert')
    # Use ENV to enable/disable MTLS strictness for dev
    if os.getenv("STRICT_MTLS") == "true" and not cert:
        logger.warning(f"Blocking request from {request.client.host} - Missing MTLS Certificate")
        raise HTTPException(status_code=401, detail="MTLS Identity Certificate Required")

    # Proceed and Add Headers
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Secure Headers
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none';"
    
    return response

@app.get("/health")
@limiter.limit("5/minute")
async def health(request: Request):
    return {"status": "shield_active", "timestamp": datetime.now().isoformat()}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("120/minute")
async def gateway_proxy(
    request: Request, 
    service: str, 
    path: str, 
    client_identity: str = Depends(validate_api_key)
):
    """Zero Trust Multi-Service Proxy"""
    if service not in TARGET_MAP:
        raise HTTPException(status_code=404, detail="Service endpoint not found in OSIN mesh")

    base_url = TARGET_MAP[service]
    target_url = f"{base_url}/{path}"
    
    logger.info(f"Proxying request from [{client_identity}] to [{service}] -> {path}")
    
    start_time = time.time()
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Reconstruct request for proxy
            resp = await client.request(
                method=request.method,
                url=target_url,
                params=dict(request.query_params),
                headers={"X-OSIN-Identity": client_identity}, # Internal tracking header
                content=await request.body()
            )
            
            PROXY_LATENCY.labels(target=service).observe(time.time() - start_time)
            return resp.content
            
        except Exception as e:
            logger.error(f"Proxy Failure to {service}: {e}")
            raise HTTPException(status_code=502, detail="Gateway error communicating with internal service mesh")

if __name__ == "__main__":
    import uvicorn
    # Start Prometheus metrics on 8006
    start_http_server(8006)
    uvicorn.run(app, host="0.0.0.0", port=8443)
