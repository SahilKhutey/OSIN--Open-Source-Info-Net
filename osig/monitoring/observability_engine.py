import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import psutil
from prometheus_client import Counter, Gauge, Histogram

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_usage: Dict[str, float]
    memory_usage: Dict[str, float]
    disk_usage: Dict[str, float]
    network_io: Dict[str, float]

class ObservabilityEngine:
    """Comprehensive observability engine for OSIG"""
    
    def __init__(self):
        self.metrics = self._initialize_prometheus_metrics()

    def _initialize_prometheus_metrics(self) -> Dict:
        return {
            'events_processed': Counter('osig_events_processed_total', 'Total events', ['source', 'type']),
            'processing_latency': Histogram('osig_processing_latency_seconds', 'Latency', ['stage']),
            'system_health': Gauge('osig_system_health_score', 'Health Score', ['component']),
            'kafka_lag': Gauge('osig_kafka_lag', 'Consumer Lag', ['topic'])
        }

    async def collect_metrics(self):
        while True:
            try:
                metrics = await self._collect_system_metrics()
                self._update_prometheus(metrics)
                await asyncio.sleep(30)
            except Exception as e:
                print(f"Observability Error: {e}")
                await asyncio.sleep(60)

    async def _collect_system_metrics(self) -> SystemMetrics:
        return SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage={'total_percent': psutil.cpu_percent(interval=1)},
            memory_usage={'used_percent': psutil.virtual_memory().percent},
            disk_usage={'percent': psutil.disk_usage('/').percent},
            network_io={'bytes_sent': psutil.net_io_counters().bytes_sent}
        )

    def _update_prometheus(self, metrics: SystemMetrics):
        self.metrics['system_health'].labels(component='cpu').set(100 - metrics.cpu_usage['total_percent'])
        self.metrics['system_health'].labels(component='memory').set(100 - metrics.memory_usage['used_percent'])

    async def get_health_report(self) -> Dict:
        metrics = await self._collect_system_metrics()
        score = ( (100-metrics.cpu_usage['total_percent']) + (100-metrics.memory_usage['used_percent']) ) / 2
        return {
            'status': 'HEALTHY' if score > 80 else 'DEGRADED',
            'overall_score': score,
            'timestamp': datetime.utcnow().isoformat()
        }
