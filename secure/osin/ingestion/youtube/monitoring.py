from prometheus_client import Counter, Gauge, Histogram, start_http_server
from datetime import datetime
from typing import Dict, Any
import time

# YouTube-specific metrics
YOUTUBE_VIDEOS_PROCESSED = Counter(
    'youtube_videos_processed_total',
    'Total YouTube videos processed',
    ['source', 'status']  # yt_dlp, api, etc.
)

YOUTUBE_COMMENTS_PROCESSED = Counter(
    'youtube_comments_processed_total',
    'Total YouTube comments processed',
    ['video_id', 'status']
)

YOUTUBE_INGESTION_LATENCY = Histogram(
    'youtube_ingestion_latency_seconds',
    'YouTube ingestion latency',
    ['content_type']  # video, comment, metadata
)

YOUTUBE_API_QUOTA = Gauge(
    'youtube_api_quota_remaining',
    'YouTube API quota remaining',
    ['project']
)

YOUTUBE_CONTENT_QUALITY = Gauge(
    'youtube_content_quality_score',
    'YouTube content quality assessment',
    ['video_id']
)

class YouTubeMetricsCollector:
    """Collect and expose YouTube ingestion metrics"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.start_time = datetime.utcnow()
        
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        
        start_http_server(self.port)
        print(f"YouTube metrics server started on port {self.port}")
    
    def record_video_processed(self, source: str, status: str = "success"):
        """Record processed video"""
        
        YOUTUBE_VIDEOS_PROCESSED.labels(source=source, status=status).inc()
    
    def record_comment_processed(self, video_id: str, status: str = "success"):
        """Record processed comment"""
        
        YOUTUBE_COMMENTS_PROCESSED.labels(video_id=video_id, status=status).inc()
    
    def record_ingestion_latency(self, content_type: str, latency: float):
        """Record ingestion latency"""
        
        YOUTUBE_INGESTION_LATENCY.labels(content_type=content_type).observe(latency)
    
    def update_api_quota(self, project: str, remaining: int):
        """Update API quota status"""
        
        YOUTUBE_API_QUOTA.labels(project=project).set(remaining)
    
    def update_content_quality(self, video_id: str, quality_score: float):
        """Update content quality assessment"""
        
        YOUTUBE_CONTENT_QUALITY.labels(video_id=video_id).set(quality_score)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        
        return {
            "status": "healthy",
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "videos_processed": YOUTUBE_VIDEOS_PROCESSED._value.get(),
            "comments_processed": YOUTUBE_COMMENTS_PROCESSED._value.get(),
            "avg_latency": YOUTUBE_INGESTION_LATENCY._sum / max(1, YOUTUBE_INGESTION_LATENCY._count)
        }
