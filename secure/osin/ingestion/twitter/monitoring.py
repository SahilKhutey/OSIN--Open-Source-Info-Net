from prometheus_client import Counter, Gauge, Histogram, start_http_server
from typing import Dict, Any
import time
from datetime import datetime

# Twitter-specific metrics
TWITTER_TWEETS_PROCESSED = Counter(
    'twitter_tweets_processed_total',
    'Total tweets processed',
    ['source', 'status']
)

TWITTER_INGESTION_LATENCY = Histogram(
    'twitter_ingestion_latency_seconds',
    'Tweet ingestion latency',
    ['source']
)

TWITTER_RATE_LIMIT_STATUS = Gauge(
    'twitter_rate_limit_remaining',
    'Twitter API rate limit remaining',
    ['endpoint']
)

TWITTER_ERROR_RATE = Gauge(
    'twitter_error_rate',
    'Twitter ingestion error rate',
    ['error_type']
)

class TwitterMetricsCollector:
    """Collect and expose Twitter ingestion metrics"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.start_time = datetime.utcnow()
        
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        
        start_http_server(self.port)
        print(f"Twitter metrics server started on port {self.port}")
    
    def record_tweet_processed(self, source: str, status: str = "success"):
        """Record processed tweet"""
        
        TWITTER_TWEETS_PROCESSED.labels(source=source, status=status).inc()
    
    def record_ingestion_latency(self, source: str, latency: float):
        """Record ingestion latency"""
        
        TWITTER_INGESTION_LATENCY.labels(source=source).observe(latency)
    
    def update_rate_limit(self, endpoint: str, remaining: int):
        """Update rate limit status"""
        
        TWITTER_RATE_LIMIT_STATUS.labels(endpoint=endpoint).set(remaining)
    
    def record_error(self, error_type: str):
        """Record error occurrence"""
        
        TWITTER_ERROR_RATE.labels(error_type=error_type).inc()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        
        return {
            "status": "healthy",
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "tweets_processed": TWITTER_TWEETS_PROCESSED._value.get(),
            "avg_latency": TWITTER_INGESTION_LATENCY._sum / max(1, TWITTER_INGESTION_LATENCY._count)
        }
