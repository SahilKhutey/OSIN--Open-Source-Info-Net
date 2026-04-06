from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router as signals_router
from app.config import settings
import time
import json
import asyncio
from typing import Set
import random
from datetime import datetime

app = FastAPI(title=settings.PROJECT_NAME)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/intelligence")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client (if any)
            data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            if data:
                await websocket.send_json({"type": "ack", "message": "received"})
    except asyncio.TimeoutError:
        pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Mock data generator for demo
async def generate_mock_events():
    """Generate mock intelligence events for testing"""
    sources = ['twitter', 'reddit', 'youtube', 'news']
    locations = [
        (37.7749, -122.4194),  # San Francisco
        (51.5074, -0.1278),    # London
        (35.6762, 139.6503),   # Tokyo
        (40.7128, -74.0060),   # New York
        (-33.8688, 151.2093),  # Sydney
    ]
    
    event_templates = [
        "Breaking: Market volatility detected in {region}",
        "Alert: Trending topic surge on {source}",
        "Intelligence: Geopolitical developments in {region}",
        "Analysis: Data anomaly detected",
        "Update: Cross-platform signal validation",
    ]
    
    threat_levels = [25, 35, 45, 55, 65]
    
    while True:
        try:
            lat, lon = random.choice(locations)
            source = random.choice(sources)
            event = {
                "type": "event",
                "payload": {
                    "id": f"evt_{int(time.time()*1000)}",
                    "platform": source,
                    "text": random.choice(event_templates).format(region="Zone Alpha", source=source),
                    "confidence": round(random.uniform(0.5, 0.95), 2),
                    "timestamp": datetime.utcnow().isoformat(),
                    "location": {
                        "lat": lat + random.uniform(-0.1, 0.1),
                        "lon": lon + random.uniform(-0.1, 0.1),
                        "accuracy": random.uniform(1, 10)
                    }
                }
            }
            await manager.broadcast(event)
            
            # Random threat level update
            if random.random() > 0.7:
                threat_event = {
                    "type": "threat",
                    "payload": {
                        "level": random.choice(threat_levels)
                    }
                }
                await manager.broadcast(threat_event)
            
            await asyncio.sleep(random.uniform(2, 5))
        except Exception as e:
            print(f"Error in event generator: {e}")
            await asyncio.sleep(5)

# Start background task for mock events
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generate_mock_events())

@app.get("/")
async def root():
    return {"message": "OSIN Intelligence Engine is LIVE", "ws": "/ws/intelligence"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
