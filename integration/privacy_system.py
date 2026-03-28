import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from architecture.privacy_core import PRIVACY_LEVELS
from layer1.anonymous_gateway import AnonymousGateway, EphemeralSession
from layer2.hybrid_proxy_network import HybridProxyNetwork
from layer3.distributed_ingestion import DistributedIngestionNetwork
from layer4.data_obfuscation import DataObfuscationEngine
from layer5.query_privacy import QueryPrivacyEngine
from optional.tor_integration import SmartTorIntegration

class OSINPrivacySystem:
    """Unified Orchestrator for the OSIN Hybrid Privacy Stack"""
    
    def __init__(self):
        self.gateway = AnonymousGateway()
        self.proxy_net = HybridProxyNetwork()
        self.ingestion = DistributedIngestionNetwork()
        self.obfuscation = DataObfuscationEngine()
        self.query_eng = QueryPrivacyEngine()
        self.tor = SmartTorIntegration()

    async def process_task(self, query: str, request_meta: Dict) -> Dict:
        # 1. Ephemeral Session
        session = self.gateway.create_session(request_meta)
        
        # 2. Private Query Execution
        query_result = await self.query_eng.process_query(query, session.privacy_level)
        
        # 3. Data Obfuscation & Final Anonymization
        final_data = await self.obfuscation.process_data(query_result, session.privacy_level)
        
        return {
            "session_id": session.session_id,
            "privacy_level": session.privacy_level,
            "data": final_data,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_system_vitals(self) -> Dict:
        return {
            "active_sessions": len(self.gateway.sessions),
            "ingestion_nodes": len(self.ingestion.nodes),
            "tor_status": "ACTIVE" if self.tor.enabled else "DISABLED"
        }
