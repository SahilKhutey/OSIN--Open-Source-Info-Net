from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from kafka import KafkaProducer, KafkaConsumer
import json
import hashlib

@dataclass
class IngestionConfig:
    """Ingestion pipeline configuration"""
    kafka_brokers: List[str] = field(default_factory=lambda: ['kafka1:9092', 'kafka2:9093'])
    batch_size: int = 1000
    flush_interval: int = 5  # seconds
    retry_attempts: int = 3
    rate_limit: Dict[str, int] = field(default_factory=lambda: {
        'twitter': 1000,  # requests per hour
        'reddit': 600,
        'youtube': 10000,
        'news': 10000,
        'instagram': 200  # very limited
    })

@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform: str
    api_keys: List[str] = field(default_factory=list)
    proxies: List[str] = field(default_factory=list)
    user_agents: List[str] = field(default_factory=list)
    rate_limit: int = 1000
    enabled: bool = True
