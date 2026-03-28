import asyncio
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp

from architecture.privacy_core import PRIVACY_LEVELS

@dataclass
class ProxyNode:
    node_id: str
    location: str
    proxy_type: str  # residential, datacenter, vpn, tor
    ip_address: str
    port: int
    latency_ms: float
    success_rate: float
    last_used: datetime
    capabilities: List[str] = field(default_factory=list)
    is_active: bool = True

@dataclass
class ProxyRoute:
    route_id: str
    nodes: List[ProxyNode]
    total_latency_ms: float
    anonymity_score: float
    created_at: datetime

class HybridProxyNetwork:
    """Military-grade hybrid proxy management for OSIN"""
    
    def __init__(self):
        self.nodes = self._initialize_nodes()
        self.routes = {}

    def _initialize_nodes(self) -> Dict[str, ProxyNode]:
        # Implementation with provided samples
        nodes_list = [
            ProxyNode("res-us-001", "Virginia, USA", "residential", "192.168.1.100", 8080, 50, 0.95, datetime.utcnow(), ["twitter", "youtube"]),
            ProxyNode("vpn-sg-001", "Singapore", "vpn", "10.0.0.100", 443, 120, 0.85, datetime.utcnow(), ["all"]),
            ProxyNode("dc-de-001", "Frankfurt, DE", "datacenter", "1.2.3.4", 80, 30, 0.99, datetime.utcnow(), ["apis"]),
            ProxyNode("tor-exit-001", "Unknown", "tor", "127.0.0.1", 9050, 500, 0.60, datetime.utcnow(), ["sensitive"])
        ]
        return {n.node_id: n for n in nodes_list}

    async def create_route(self, target: str, privacy_level: str = "ENHANCED") -> ProxyRoute:
        if privacy_level == "TOR":
            selected = [n for n in self.nodes.values() if n.proxy_type == "tor"][:1]
        elif privacy_level == "ENHANCED":
            selected = self._select_multi_hop(target)
        else:
            selected = [max(self.nodes.values(), key=lambda x: x.success_rate)]
        
        return ProxyRoute(
            route_id=f"route-{random.randint(1000, 9999)}",
            nodes=selected,
            total_latency_ms=sum(n.latency_ms for n in selected),
            anonymity_score=self._calculate_anonymity(selected),
            created_at=datetime.utcnow()
        )

    def _select_multi_hop(self, target: str) -> List[ProxyNode]:
        entry = random.choice([n for n in self.nodes.values() if n.proxy_type in ["residential", "vpn"]])
        exit_node = random.choice([n for n in self.nodes.values() if "all" in n.capabilities or target in n.capabilities])
        return [entry, exit_node]

    def _calculate_anonymity(self, nodes: List[ProxyNode]) -> float:
        score = len(nodes) * 0.2
        if any(n.proxy_type == 'tor' for n in nodes): score += 0.5
        return min(1.0, score)

    async def make_request(self, route: ProxyRoute, url: str, **kwargs):
        proxy = f"http://{route.nodes[0].ip_address}:{route.nodes[0].port}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy, timeout=10, **kwargs) as resp:
                return await resp.text()
