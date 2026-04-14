from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import requests
import time
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Any
import psutil
import socket
from prometheus_client import start_http_server, Gauge, Counter
import json

app = FastAPI(title="OSIN SVP-1 Health Monitor")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("osin-health")

# Prometheus metrics (Port 8003)
SERVICE_STATUS = Gauge('service_status', 'Service status (1=up, 0=down)', ['service'])
SERVICE_LATENCY = Gauge('service_latency_ms', 'Service latency in milliseconds', ['service'])
ERROR_COUNT = Counter('service_errors', 'Service errors', ['service'])

# Services to monitor (Internal Networking names from docker-compose)
SERVICES = {
    "kafka": {"url": "http://kafka:8080", "type": "http"},
    "backend": {"url": "http://backend:8000/health", "type": "http"},
    "xr_bridge": {"url": "http://xr-bridge:3001/health", "type": "http"},
    "graph_db": {"url": "http://neo4j:7474", "type": "http"},
    "llm_backend": {"url": "http://llm-backend:8000/health", "type": "http"},
    "kafka_broker": {"host": "kafka", "port": 29092, "type": "tcp"},
    "redis": {"host": "redis", "port": 6379, "type": "tcp"}
}

class HealthMonitor:
    def __init__(self):
        self.start_time = datetime.now()
    
    async def check_service(self, service_name: str, config: Dict) -> Dict:
        """Check service health with detailed metrics"""
        try:
            start_time = time.time()
            if config["type"] == "http":
                response = requests.get(config["url"], timeout=3)
                latency = (time.time() - start_time) * 1000
                status = response.status_code == 200
            elif config["type"] == "tcp":
                latency = await self.check_tcp_connection(config["host"], config["port"])
                status = latency is not None
            else:
                status = False
                latency = None
            
            result = {
                "status": "UP" if status else "DOWN",
                "latency_ms": round(latency, 2) if latency else None,
                "timestamp": datetime.now().isoformat()
            }
            
            SERVICE_STATUS.labels(service=service_name).set(1 if status else 0)
            if latency:
                SERVICE_LATENCY.labels(service=service_name).set(latency)
            
            return result
        except Exception as e:
            ERROR_COUNT.labels(service=service_name).inc()
            return {"status": "DOWN", "error": str(e), "timestamp": datetime.now().isoformat()}

    async def check_tcp_connection(self, host: str, port: int) -> float:
        start_time = time.time()
        try:
            with socket.create_connection((host, port), timeout=2):
                return (time.time() - start_time) * 1000
        except:
            return None

monitor = HealthMonitor()

# Mount static files for the HUD
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    results = {}
    for service_name, config in SERVICES.items():
        results[service_name] = await monitor.check_service(service_name, config)
    
    results["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "uptime_seconds": (datetime.now() - monitor.start_time).total_seconds()
    }
    
    all_healthy = all(r.get("status") == "UP" for s, r in results.items() if s != "system")
    results["overall_status"] = "HEALTHY" if all_healthy else "DEGRADED"
    return results

@app.get("/metrics")
async def metrics_endpoint():
    from prometheus_client import generate_latest
    return generate_latest()

if __name__ == "__main__":
    # Start Prometheus on Port 8003
    start_http_server(8003)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
