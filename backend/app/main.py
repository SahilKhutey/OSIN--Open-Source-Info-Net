from fastapi import FastAPI, Request
from app.api.router import router as signals_router
from app.config import settings
import time

app = FastAPI(title=settings.PROJECT_NAME)

# Basic rate limiting middleware
RATE_LIMIT_DURATION = 1.0  # seconds
last_request_time = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip in last_request_time:
        if current_time - last_request_time[client_ip] < RATE_LIMIT_DURATION:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    
    last_request_time[client_ip] = current_time
    response = await call_next(request)
    return response

app.include_router(signals_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "OSIN Intelligence Engine is LIVE"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
