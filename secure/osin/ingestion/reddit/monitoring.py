from prometheus_client import Counter, Gauge, Histogram, start_http_server
from datetime import datetime
from typing import Dict, Any
import time

# Reddit-specific metrics
REDDIT_SUBMISSIONS_PROCESSED = Counter(
    'reddit_submissions_processed_total',
    'Total Reddit submissions processed',
    ['subreddit', 'status']
)

REDDIT_COMMENTS_PROCESSED = Counter(
    'reddit_comments_processed_total',
    'Total Reddit comments processed',
    ['subreddit', 'status']
)

REDDIT_INGESTION_LATENCY = Histogram(
    'reddit_ingestion_latency_seconds',
    'Reddit ingestion latency',
    ['type']  # submission or comment
)

REDDIT_API_RATE_LIMIT = Gauge(
    'reddit_api_rate_limit_remaining',
    'Reddit API rate limit remaining',
    ['client']
)

REDDIT_SUBREDDIT_ACTIVITY = Gauge(
    'reddit_subreddit_activity',
    'Reddit subreddit activity level',
    ['subreddit']
)

class RedditMetricsCollector:
    """Collect and expose Reddit ingestion metrics"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.start_time = datetime.utcnow()
        
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        
        start_http_server(self.port)
        print(f"Reddit metrics server started on port {self.port}")
    
    def record_submission_processed(self, subreddit: str, status: str = "success"):
        """Record processed submission"""
        
        REDDIT_SUBMISSIONS_PROCESSED.labels(subreddit=subreddit, status=status).inc()
    
    def record_comment_processed(self, subreddit: str, status: str = "success"):
        """Record processed comment"""
        
        REDDIT_COMMENTS_PROCESSED.labels(subreddit=subreddit, status=status).inc()
    
    def record_ingestion_latency(self, content_type: str, latency: float):
        """Record ingestion latency"""
        
        REDDIT_INGESTION_LATENCY.labels(type=content_type).observe(latency)
    
    def update_rate_limit(self, client: str, remaining: int):
        """Update rate limit status"""
        
        REDDIT_API_RATE_LIMIT.labels(client=client).set(remaining)
    
    def update_subreddit_activity(self, subreddit: str, activity_level: float):
        """Update subreddit activity level"""
        
        REDDIT_SUBREDDIT_ACTIVITY.labels(subreddit=subreddit).set(activity_level)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        
        return {
            "status": "healthy",
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "submissions_processed": REDDIT_SUBMISSIONS_PROCESSED._value.get(),
            "comments_processed": REDDIT_COMMENTS_PROCESSED._value.get(),
            "avg_latency": REDDIT_INGESTION_LATENCY._sum / max(1, REDDIT_INGESTION_LATENCY._count)
        }
