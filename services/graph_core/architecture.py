"""
OSIN Graph Intelligence Core - Architecture
Unified reasoning layer for cross-source intelligence fusion
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class EntityType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DEVICE = "device"
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    IMAGE = "image"
    AUDIO = "audio"
    WIFI_NETWORK = "wifi_network"
    SATELLITE_TILE = "satellite_tile"
    THREAT_SIGNAL = "threat_signal"
    EVENT = "event"
    DOCUMENT = "document"
    CREDENTIAL = "credential"
    VULNERABILITY = "vulnerability"

class RelationshipType(Enum):
    LOCATED_AT = "LOCATED_AT"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    GENERATED_FROM = "GENERATED_FROM"
    MATCHES = "MATCHES"
    SIMILAR_TO = "SIMILAR_TO"
    OCCURRED_WITH = "OCCURRED_WITH"
    CONNECTED_TO = "CONNECTED_TO"
    EXPOSED_BY = "EXPOSED_BY"
    CORRELATED_WITH = "CORRELATED_WITH"
    OWNED_BY = "OWNED_BY"
    USED_BY = "USED_BY"
    TARGETS = "TARGETS"
    CONTAINS = "CONTAINS"
    DERIVED_FROM = "DERIVED_FROM"

@dataclass
class Entity:
    id: str
    type: EntityType
    properties: Dict[str, Any] = field(default_factory=dict)
    source_modules: List[str] = field(default_factory=list)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Relationship:
    id: str
    source_id: str
    target_id: str
    type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)

class OSINGraphArchitecture:
    """OSIN Graph Intelligence Core Architecture"""
    def __init__(self):
        self.supported_entity_types = list(EntityType)
        self.supported_relationship_types = list(RelationshipType)
        self.integration_points = {
            "geo_intel": "Geospatial intelligence layer",
            "cyber_intel": "Cyber threat intelligence",
            "audio_intel": "Audio analysis layer",
            "image_intel": "Image forensic layer",
            "signal_intel": "Signal intelligence",
            "threat_intel": "Threat assessment layer"
        }
