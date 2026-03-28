from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time
from datetime import datetime

# Metrics
INGESTION_REQUESTS = Counter(
    'ingestion_requests_total',
    'Total ingestion requests',
    ['platform', 'status']
)

INGESTION_LATENCY = Histogram(
    'ingestion_latency_seconds',
    'Ingestion processing latency',
    ['platform']
)

PLATFORM_AVAILABILITY = Gauge(
    'platform_availability',
    'Platform availability status',
    ['platform']
)

CONTENT_VOLUME = Gauge(
    'content_volume',
    'Volume of content processed',
    ['platform', 'type']
)

class IngestionMonitor:
    """Monitor ingestion pipeline performance"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        
    def record_request(self, platform: str, status: str, latency: float):
        """Record ingestion request metrics"""
        INGESTION_REQUESTS.labels(platform=platform, status=status).inc()
        INGESTION_LATENCY.labels(platform=platform).observe(latency)
    
    def update_availability(self, platform: str, available: bool):
        """Update platform availability"""
        PLATFORM_AVAILABILITY.labels(platform=platform).set(1 if available else 0)
    
    def record_content_volume(self, platform: str, content_type: str, volume: int):
        """Record content volume"""
        CONTENT_VOLUME.labels(platform=platform, type=content_type).set(volume)
    
    def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics server"""
        start_http_server(port)
        print(f"Metrics server started on port {port}")

# Global monitor instance
monitor = IngestionMonitor()

def get_health_status():
    """Get overall health status for diagnostic endpoints"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": (datetime.utcnow() - monitor.start_time).total_seconds(),
        # Metrics access for reporting
    }
