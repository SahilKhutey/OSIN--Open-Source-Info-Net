from prometheus_client import Counter, Gauge, Histogram, start_http_server
from datetime import datetime
from typing import Dict, Any, List
import time
import hashlib
import statistics

# LinkedIn-specific metrics
LINKEDIN_JOBS_COLLECTED = Counter(
    'linkedin_jobs_collected_total',
    'Total LinkedIn jobs collected',
    ['status']  # success, error, blocked
)

LINKEDIN_COMPANIES_COLLECTED = Counter(
    'linkedin_companies_collected_total',
    'Total LinkedIn companies collected',
    ['status']
)

LINKEDIN_POSTS_COLLECTED = Counter(
    'linkedin_posts_collected_total',
    'Total LinkedIn posts collected',
    ['status']
)

LINKEDIN_COLLECTION_LATENCY = Histogram(
    'linkedin_collection_latency_seconds',
    'LinkedIn data collection latency',
    ['content_type']  # jobs, companies, posts
)

LINKEDIN_RATE_LIMIT_STATUS = Gauge(
    'linkedin_rate_limit_remaining',
    'LinkedIn rate limit remaining requests',
    []
)

LINKEDIN_COMPLIANCE_VIOLATIONS = Counter(
    'linkedin_compliance_violations_total',
    'LinkedIn compliance violations detected',
    ['violation_type']
)

LINKEDIN_PROXY_ROTATIONS = Counter(
    'linkedin_proxy_rotations_total',
    'Number of proxy rotations',
    []
)

class LinkedInMetricsCollector:
    """Collect and expose LinkedIn ingestion metrics"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.start_time = datetime.utcnow()
        
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        
        start_http_server(self.port)
        print(f"LinkedIn metrics server started on port {self.port}")
    
    def record_jobs_collected(self, status: str = "success"):
        """Record collected jobs"""
        
        LINKEDIN_JOBS_COLLECTED.labels(status=status).inc()
    
    def record_companies_collected(self, status: str = "success"):
        """Record collected companies"""
        
        LINKEDIN_COMPANIES_COLLECTED.labels(status=status).inc()
    
    def record_posts_collected(self, status: str = "success"):
        """Record collected posts"""
        
        LINKEDIN_POSTS_COLLECTED.labels(status=status).inc()
    
    def record_collection_latency(self, content_type: str, latency: float):
        """Record collection latency"""
        
        LINKEDIN_COLLECTION_LATENCY.labels(content_type=content_type).observe(latency)
    
    def update_rate_limit(self, remaining: int):
        """Update rate limit status"""
        
        LINKEDIN_RATE_LIMIT_STATUS.set(remaining)
    
    def record_compliance_violation(self, violation_type: str):
        """Record compliance violation"""
        
        LINKEDIN_COMPLIANCE_VIOLATIONS.labels(violation_type=violation_type).inc()
    
    def record_proxy_rotation(self):
        """Record proxy rotation"""
        
        LINKEDIN_PROXY_ROTATIONS.inc()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        
        return {
            "status": "healthy",
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "jobs_collected": LINKEDIN_JOBS_COLLECTED._value.get() if hasattr(LINKEDIN_JOBS_COLLECTED, '_value') else 0,
            "companies_collected": LINKEDIN_COMPANIES_COLLECTED._value.get() if hasattr(LINKEDIN_COMPANIES_COLLECTED, '_value') else 0,
            "posts_collected": LINKEDIN_POSTS_COLLECTED._value.get() if hasattr(LINKEDIN_POSTS_COLLECTED, '_value') else 0,
            "avg_collection_latency": LINKEDIN_COLLECTION_LATENCY._sum / max(1, LINKEDIN_COLLECTION_LATENCY._count),
            "rate_limit_remaining": LINKEDIN_RATE_LIMIT_STATUS._value.get() if hasattr(LINKEDIN_RATE_LIMIT_STATUS, '_value') else 100,
            "compliance_violations": LINKEDIN_COMPLIANCE_VIOLATIONS._value.get() if hasattr(LINKEDIN_COMPLIANCE_VIOLATIONS, '_value') else 0
        }

# Alerting rules for LinkedIn ingestion
LINKEDIN_ALERTING_RULES = """
groups:
- name: linkedin-ingestion-alerts
  rules:
  - alert: LinkedInIngestionDown
    expr: up{job="linkedin-ingestion"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "LinkedIn ingestion is down"
      description: "LinkedIn ingestion has been down for more than 5 minutes"
  
  - alert: HighLinkedInErrorRate
    expr: rate(linkedin_jobs_collected_total{status="error"}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High LinkedIn error rate"
      description: "LinkedIn ingestion error rate is above 10%"
  
  - alert: LinkedInRateLimitCritical
    expr: linkedin_rate_limit_remaining < 10
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "LinkedIn rate limit critical"
      description: "LinkedIn rate limit is running critically low"
  
  - alert: LinkedInComplianceViolation
    expr: rate(linkedin_compliance_violations_total[5m]) > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "LinkedIn compliance violation detected"
      description: "Compliance violation detected in LinkedIn data collection"
  
  - alert: LinkedInBlockedBySite
    expr: rate(linkedin_jobs_collected_total{status="blocked"}[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "LinkedIn blocking detected"
      description: "LinkedIn is blocking data collection attempts"
"""

# Performance dashboard configuration
LINKEDIN_GRAFANA_DASHBOARD = """
{
  "dashboard": {
    "title": "LinkedIn Ingestion Metrics",
    "panels": [
      {
        "title": "Content Collection Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(linkedin_jobs_collected_total[5m])",
            "legendFormat": "Jobs - {{status}}"
          },
          {
            "expr": "rate(linkedin_companies_collected_total[5m])",
            "legendFormat": "Companies - {{status}}"
          },
          {
            "expr": "rate(linkedin_posts_collected_total[5m])",
            "legendFormat": "Posts - {{status}}"
          }
        ]
      },
      {
        "title": "Rate Limit Status",
        "type": "gauge",
        "targets": [
          {
            "expr": "linkedin_rate_limit_remaining",
            "legendFormat": "Remaining Requests"
          }
        ]
      },
      {
        "title": "Collection Latency",
        "type": "heatmap",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(linkedin_collection_latency_seconds_bucket[5m]))",
            "legendFormat": "95th Percentile - {{content_type}}"
          }
        ]
      },
      {
        "title": "Compliance Violations",
        "type": "stat",
        "targets": [
          {
            "expr": "linkedin_compliance_violations_total",
            "legendFormat": "Total Violations"
          }
        ]
      },
      {
        "title": "Proxy Rotations",
        "type": "timeseries",
        "targets": [
          {
            "expr": "linkedin_proxy_rotations_total",
            "legendFormat": "Proxy Changes"
          }
        ]
      }
    ]
  }
}
"""

class LinkedInHealthChecker:
    """Comprehensive LinkedIn health checking"""
    
    def __init__(self):
        self.health_checks = {
            'playwright_functionality': self._check_playwright,
            'rate_limit_status': self._check_rate_limits,
            'compliance_status': self._check_compliance,
            'proxy_connectivity': self._check_proxy_connectivity,
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
    
    async def _check_playwright(self) -> Dict[str, Any]:
        """Check Playwright functionality"""
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Test basic navigation to LinkedIn
                await page.goto("https://www.linkedin.com/", timeout=15000)
                await page.wait_for_selector("body", timeout=10000)
                
                await browser.close()
                
                return {
                    'status': 'healthy',
                    'browser_navigation': True,
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
            'requests_remaining': 85,
            'next_reset': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'current_usage': 15,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _check_compliance(self) -> Dict[str, Any]:
        """Check compliance status"""
        
        # This would check actual compliance metrics
        return {
            'status': 'healthy',
            'compliance_violations_24h': 0,
            'rate_limit_adherence': 1.0,
            'proxy_rotation_success': 0.95,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _check_proxy_connectivity(self) -> Dict[str, Any]:
        """Check proxy connectivity"""
        
        # This would test proxy connections
        return {
            'status': 'healthy',
            'active_proxies': 3,
            'proxy_success_rate': 0.98,
            'failed_connections': 2,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _check_data_flow(self) -> Dict[str, Any]:
        """Check data flow integrity"""
        
        # This would check Kafka connectivity and data processing
        return {
            'status': 'healthy',
            'kafka_connected': True,
            'data_processing_lag': 15,  # seconds
            'messages_per_second': 0.5,
            'error_rate': 0.01,
            'timestamp': datetime.utcnow().isoformat()
        }

# LinkedIn data quality assurance
class LinkedInDataQuality:
    """Ensure LinkedIn data quality and integrity"""
    
    def __init__(self):
        self.quality_metrics = {
            'duplicate_detection': self._check_duplicates,
            'data_completeness': self._check_completeness,
            'content_validity': self._check_content_validity,
            'metadata_integrity': self._check_metadata_integrity
        }
    
    async def validate_data_quality(self, data_batch: List[Dict]) -> Dict[str, Any]:
        """Validate quality of LinkedIn data batch"""
        
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
        
        required_fields = ['id', 'url', 'type']
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
            content = item.get('content', '') or item.get('title', '') or item.get('description', '')
            if not content or len(content.strip()) < 10:
                invalid_content += 1
        
        validity_rate = 1 - (invalid_content / len(data_batch)) if data_batch else 0
        
        return {
            'status': 'healthy' if validity_rate > 0.8 else 'warning',
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
