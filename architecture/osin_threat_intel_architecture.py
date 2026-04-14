"""
OSIN Advanced Threat Intelligence Layer - Architecture
Version: 3.5.0
Description: Defensive, lawful implementation focusing on passive intelligence gathering
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class IntelSource(Enum):
    ZMAP = "internet_exposure_scan"
    FIRECRAWL = "web_crawling"
    TORBOT = "dark_web_monitoring"
    SPYCLOUD = "breach_intelligence"
    correlation = "threat_correlation"
    OSIN_CORE = "osin_fusion"

@dataclass
class ThreatIndicator:
    source: IntelSource
    timestamp: datetime
    indicator_type: str
    value: str
    confidence: float
    severity: ThreatLevel

@dataclass
class ThreatAssessment:
    target: str
    overall_score: float
    threat_level: ThreatLevel
    indicators: List[ThreatIndicator]
    correlations: Dict[str, List[str]]
    recommendations: List[str]

class OSINThreatIntelArchitecture:
    """Defensive threat intelligence architecture for OSIN"""
    
    def __init__(self):
        self.permitted_tools = {
            "zmap": "Internet-scale exposure scanning",
            "firecrawl": "Web content crawling and indexing",
            "torbot": "Dark web monitoring (passive only)",
            "spycloud": "Breach data intelligence"
        }
        
        self.excluded_tools = {
            "beef": "Browser Exploitation Framework - offensive tool",
            "flipper_zero": "Hardware tool - not software integrable"
        }
        
        self.integration_points = {
            "osin_core": "Threat data fusion with 15-layer intelligence",
            "3d_dashboard": "Real-time threat visualization"
        }
