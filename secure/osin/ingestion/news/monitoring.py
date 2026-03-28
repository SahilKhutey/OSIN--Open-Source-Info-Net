from prometheus_client import Counter, Gauge, Histogram, start_http_server
from datetime import datetime, timedelta
from typing import Dict, Any, List
import time
import hashlib
import statistics

# News-specific metrics
NEWS_ARTICLES_COLLECTED = Counter(
    'news_articles_collected_total',
    'Total news articles collected',
    ['source', 'status']  # newspaper3k, rss, gdelt
)

NEWS_EVENTS_COLLECTED = Counter(
    'news_events_collected_total',
    'Total news events collected',
    ['source', 'status']
)

NEWS_COLLECTION_LATENCY = Histogram(
    'news_collection_latency_seconds',
    'News data collection latency',
    ['content_type']  # articles, events
)

NEWS_RATE_LIMIT_STATUS = Gauge(
    'news_rate_limit_remaining',
    'News source rate limit remaining requests',
    ['source']  # newspaper3k, rss, gdelt
)

NEWS_COMPLIANCE_VIOLATIONS = Counter(
    'news_compliance_violations_total',
    'News compliance violations detected',
    ['violation_type']
)

NEWS_SOURCE_HEALTH = Gauge(
    'news_source_health',
    'News source health status',
    ['source']
)

class NewsMetricsCollector:
    """Collect and expose news ingestion metrics"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.start_time = datetime.utcnow()
        
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        
        start_http_server(self.port)
        print(f"News metrics server started on port {self.port}")
    
    def record_article_collected(self, source: str, status: str = "success"):
        """Record collected article"""
        
        NEWS_ARTICLES_COLLECTED.labels(source=source, status=status).inc()
    
    def record_event_collected(self, source: str, status: str = "success"):
        """Record collected event"""
        
        NEWS_EVENTS_COLLECTED.labels(source=source, status=status).inc()
    
    def record_collection_latency(self, content_type: str, latency: float):
        """Record collection latency"""
        
        NEWS_COLLECTION_LATENCY.labels(content_type=content_type).observe(latency)
    
    def update_rate_limit(self, source: str, remaining: int):
        """Update rate limit status"""
        
        NEWS_RATE_LIMIT_STATUS.labels(source=source).set(remaining)
    
    def record_compliance_violation(self, violation_type: str):
        """Record compliance violation"""
        
        NEWS_COMPLIANCE_VIOLATIONS.labels(violation_type=violation_type).inc()
    
    def update_source_health(self, source: str, health_score: float):
        """Update source health status"""
        
        NEWS_SOURCE_HEALTH.labels(source=source).set(health_score)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        
        return {
            "status": "healthy",
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "articles_collected": NEWS_ARTICLES_COLLECTED._value.get() if hasattr(NEWS_ARTICLES_COLLECTED, '_value') else 0,
            "events_collected": NEWS_EVENTS_COLLECTED._value.get() if hasattr(NEWS_EVENTS_COLLECTED, '_value') else 0,
            "avg_collection_latency": NEWS_COLLECTION_LATENCY._sum / max(1, NEWS_COLLECTION_LATENCY._count),
            "rate_limit_status": {
                "newspaper3k": NEWS_RATE_LIMIT_STATUS.labels(source="newspaper3k")._value.get() if hasattr(NEWS_RATE_LIMIT_STATUS.labels(source="newspaper3k"), '_value') else 10,
                "rss": NEWS_RATE_LIMIT_STATUS.labels(source="rss")._value.get() if hasattr(NEWS_RATE_LIMIT_STATUS.labels(source="rss"), '_value') else 15,
                "gdelt": NEWS_RATE_LIMIT_STATUS.labels(source="gdelt")._value.get() if hasattr(NEWS_RATE_LIMIT_STATUS.labels(source="gdelt"), '_value') else 5
            },
            "source_health": {
                "newspaper3k": NEWS_SOURCE_HEALTH.labels(source="newspaper3k")._value.get() if hasattr(NEWS_SOURCE_HEALTH.labels(source="newspaper3k"), '_value') else 1.0,
                "rss": NEWS_SOURCE_HEALTH.labels(source="rss")._value.get() if hasattr(NEWS_SOURCE_HEALTH.labels(source="rss"), '_value') else 1.0,
                "gdelt": NEWS_SOURCE_HEALTH.labels(source="gdelt")._value.get() if hasattr(NEWS_SOURCE_HEALTH.labels(source="gdelt"), '_value') else 1.0
            }
        }

# Alerting rules for news ingestion
NEWS_ALERTING_RULES = """
groups:
- name: news-ingestion-alerts
  rules:
  - alert: NewsIngestionDown
    expr: up{job="news-ingestion"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "News ingestion is down"
      description: "News ingestion has been down for more than 5 minutes"
  
  - alert: HighNewsErrorRate
    expr: rate(news_articles_collected_total{status="error"}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High news error rate"
      description: "News ingestion error rate is above 10%"
  
  - alert: NewsRateLimitCritical
    expr: news_rate_limit_remaining < 10
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "News rate limit critical"
      description: "News rate limit is running critically low"
  
  - alert: NewsComplianceViolation
    expr: rate(news_compliance_violations_total[5m]) > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "News compliance violation detected"
      description: "Compliance violation detected in news data collection"
  
  - alert: NewsSourceDegraded
    expr: news_source_health < 0.7
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "News source degraded"
      description: "One or more news sources are degraded"
"""

# Performance dashboard configuration
NEWS_GRAFANA_DASHBOARD = """
{
  "dashboard": {
    "title": "News Ingestion Metrics",
    "panels": [
      {
        "title": "Article Collection Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(news_articles_collected_total[5m])",
            "legendFormat": "{{source}} - {{status}}"
          }
        ]
      },
      {
        "title": "Event Collection Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(news_events_collected_total[5m])",
            "legendFormat": "{{source}} - {{status}}"
          }
        ]
      },
      {
        "title": "Rate Limit Status",
        "type": "gauge",
        "targets": [
          {
            "expr": "news_rate_limit_remaining",
            "legendFormat": "{{source}}"
          }
        ]
      },
      {
        "title": "Collection Latency",
        "type": "heatmap",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(news_collection_latency_seconds_bucket[5m]))",
            "legendFormat": "95th Percentile - {{content_type}}"
          }
        ]
      },
      {
        "title": "Source Health",
        "type": "gauge",
        "targets": [
          {
            "expr": "news_source_health",
            "legendFormat": "{{source}}"
          }
        ]
      },
      {
        "title": "Compliance Violations",
        "type": "stat",
        "targets": [
          {
            "expr": "news_compliance_violations_total",
            "legendFormat": "Total Violations"
          }
        ]
      }
    ]
  }
}
"""

class NewsHealthChecker:
    """Comprehensive news health checking"""
    
    def __init__(self):
        self.health_checks = {
            'newspaper3k_functionality': self._check_newspaper3k,
            'rss_functionality': self._check_rss,
            'gdelt_functionality': self._check_gdelt,
            'rate_limit_status': self._check_rate_limits,
            'compliance_status': self._check_compliance,
            'data_flow': self._check_data_flow
        }
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        
        results = {}
        for check_name, check_func in self.health_checks.items():
            try:
                results[check_name] = await check_func()
            except Exception as e:
                results[check_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    async def _check_newspaper3k(self) -> Dict[str, Any]:
        """Check newspaper3k functionality"""
        
        try:
            import newspaper
            article = newspaper.Article("https://www.bbc.com/news/world-62745805")
            article.download()
            article.parse()
            
            return {
                'status': 'healthy',
                'article_download': True,
                'article_parse': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_rss(self) -> Dict[str, Any]:
        """Check RSS functionality"""
        
        try:
            import feedparser
            feed = feedparser.parse("https://feeds.bbci.co.uk/news/rss.xml")
            
            return {
                'status': 'healthy',
                'feed_parsing': True,
                'entry_count': len(feed.get('entries', [])),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_gdelt(self) -> Dict[str, Any]:
        """Check GDELT functionality"""
        
        try:
            import requests
            response = requests.get("https://api.gdeltproject.org/api/v2/doc/doc", params={
                'query': 'trump',
                'mode': 'artlist',
                'maxrecords': 1,
                'format': 'json'
            })
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'api_connection': True,
                    'articles_found': len(response.json().get('articles', [])),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'degraded',
                    'error': f'API returned {response.status_code}',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_rate_limits(self) -> Dict[str, Any]:
        """Check rate limit status"""
        
        # This would integrate with actual rate limiter
        return {
            'status': 'healthy',
            'newspaper3k_remaining': 8,
            'rss_remaining': 12,
            'gdelt_remaining': 4,
            'next_reset': (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _check_compliance(self) -> Dict[str, Any]:
        """Check compliance status"""
        
        # This would check actual compliance metrics
        return {
            'status': 'healthy',
            'compliance_violations_24h': 0,
            'rate_limit_adherence': 1.0,
            'data_minimization_compliance': 1.0,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _check_data_flow(self) -> Dict[str, Any]:
        """Check data flow integrity"""
        
        # This would check Kafka connectivity and data processing
        return {
            'status': 'healthy',
            'kafka_connected': True,
            'data_processing_lag': 5,  # seconds
            'messages_per_second': 2.5,
            'error_rate': 0.02,
            'timestamp': datetime.utcnow().isoformat()
        }

# News data quality assurance
class NewsDataQuality:
    """Ensure news data quality and integrity"""
    
    def __init__(self):
        self.quality_metrics = {
            'duplicate_detection': self._check_duplicates,
            'data_completeness': self._check_completeness,
            'content_validity': self._check_content_validity,
            'metadata_integrity': self._check_metadata_integrity
        }
    
    async def validate_data_quality(self, data_batch: List[Dict]) -> Dict[str, Any]:
        """Validate quality of news data batch"""
        
        results = {}
        for metric_name, metric_func in self.quality_metrics.items():
            try:
                results[metric_name] = await metric_func(data_batch)
            except Exception as e:
                results[metric_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Calculate overall quality score
        quality_score = await self._calculate_overall_quality(results)
        
        return {
            'quality_score': quality_score,
            'metrics': results,
            'timestamp': datetime.utcnow().isoformat(),
            'batch_size': len(data_batch)
        }
    
    async def _check_duplicates(self, data_batch: List[Dict]) -> Dict[str, Any]:
        """Check for duplicate content"""
        
        seen_hashes = set()
        duplicates = 0
        
        for item in data_batch:
            content_hash = hashlib.sha256(
                f"{item.get('id', '')}_{item.get('url', '')}".encode()
            ).hexdigest()
            
            if content_hash in seen_hashes:
                duplicates += 1
            else:
                seen_hashes.add(content_hash)
        
        duplicate_rate = duplicates / len(data_batch) if data_batch else 0
        
        return {
            'status': 'healthy' if duplicate_rate < 0.05 else 'warning',
            'duplicate_rate': duplicate_rate,
            'duplicate_count': duplicates,
            'unique_content_rate': 1 - duplicate_rate
        }
    
    async def _check_completeness(self, data_batch: List[Dict]) -> Dict[str, Any]:
        """Check data completeness"""
        
        if not data_batch:
            return {'status': 'warning', 'completeness': 0, 'missing_fields': []}
        
        required_fields = ['id', 'url', 'title', 'type']
        missing_counts = {}
        
        for item in data_batch:
            for field in required_fields:
                if field not in item or not item[field]:
                    missing_counts[field] = missing_counts.get(field, 0) + 1
        
        completeness = 1 - (sum(missing_counts.values()) / (len(data_batch) * len(required_fields)))
        
        return {
            'status': 'healthy' if completeness > 0.95 else 'warning',
            'completeness': completeness,
            'missing_fields': missing_counts,
            'total_items': len(data_batch)
        }
    
    async def _check_content_validity(self, data_batch: List[Dict]) -> Dict[str, Any]:
        """Check content validity"""
        
        invalid_content = 0
        
        for item in data_batch:
            # Check if content is valid (not empty, not spam, etc.)
            content = item.get('content', '') or item.get('text', '') or item.get('summary', '')
            if not content or len(content.strip()) < 10:
                invalid_content += 1
        
        validity_rate = 1 - (invalid_content / len(data_batch)) if data_batch else 0
        
        return {
            'status': 'healthy' if validity_rate > 0.9 else 'warning',
            'validity_rate': validity_rate,
            'invalid_count': invalid_content,
            'valid_content_count': len(data_batch) - invalid_content
        }
    
    async def _check_metadata_integrity(self, data_batch: List[Dict]) -> Dict[str, Any]:
        """Check metadata integrity"""
        
        integrity_issues = 0
        
        for item in data_batch:
            metadata = item.get('metadata', {})
            
            # Check timestamp validity
            created_at = metadata.get('collected_at') or item.get('processing_metadata', {}).get('collected_at')
            if created_at:
                try:
                    datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    integrity_issues += 1
            
            # Check URL validity
            url = item.get('url', '')
            if url and not url.startswith(('http://', 'https://')):
                integrity_issues += 1
        
        integrity_rate = 1 - (integrity_issues / len(data_batch)) if data_batch else 0
        
        return {
            'status': 'healthy' if integrity_rate > 0.98 else 'warning',
            'integrity_rate': integrity_rate,
            'issues_count': integrity_issues,
            'checked_items': len(data_batch)
        }
    
    async def _calculate_overall_quality(self, metrics: Dict) -> float:
        """Calculate overall data quality score"""
        
        scores = []
        for metric_result in metrics.values():
            if isinstance(metric_result, dict) and 'status' in metric_result:
                # Convert status to numeric score
                status_scores = {
                    'healthy': 1.0,
                    'warning': 0.7,
                    'error': 0.3
                }
                scores.append(status_scores.get(metric_result['status'], 0.5))
            elif isinstance(metric_result, dict) and 'completeness' in metric_result:
                scores.append(metric_result['completeness'])
        
        return statistics.mean(scores) if scores else 0.0
