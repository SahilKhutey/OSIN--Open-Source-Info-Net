import asyncio
import hashlib
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from layer2.hybrid_proxy_network import HybridProxyNetwork, ProxyRoute

@dataclass
class IngestionNode:
    node_id: str
    region: str
    capabilities: List[str]
    proxy_network: HybridProxyNetwork
    is_active: bool = True
    load: float = 0.0
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CollectionTask:
    task_id: str
    target: str
    query: str
    privacy_level: str
    assigned_node: Optional[str] = None
    status: str = "PENDING"
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None

class DistributedIngestionNetwork:
    """Geographically distributed ingestion network for OSIN"""
    
    def __init__(self):
        self.nodes = self._initialize_nodes()
        self.task_queue = asyncio.Queue()
        self.results_queue = asyncio.Queue()
        
    def _initialize_nodes(self) -> Dict[str, IngestionNode]:
        nodes = {}
        regions = [("us-east", ["twitter", "news"]), ("eu-west", ["instagram", "news"]), ("asia-se", ["youtube"])]
        for reg, caps in regions:
            nodes[f"node-{reg}"] = IngestionNode(f"node-{reg}", reg, caps, HybridProxyNetwork())
        return nodes

    async def submit_task(self, target: str, query: str, privacy: str = "ENHANCED") -> str:
        task_id = hashlib.sha256(f"{target}{query}{datetime.utcnow()}".encode()).hexdigest()[:8]
        task = CollectionTask(task_id, target, query, privacy)
        await self.task_queue.put(task)
        return task_id

    async def _execute_collection(self, task: CollectionTask, node: IngestionNode):
        task.status = "RUNNING"
        route = await node.proxy_network.create_route(task.target, task.privacy_level)
        
        # Simulate collection via proxy
        await asyncio.sleep(random.uniform(0.5, 1.5))
        raw_result = {"count": random.randint(10, 100), "source": task.target, "data": []}
        
        # Apply Differential Privacy (Laplace Mechanism)
        if task.privacy_level == "ENHANCED":
            epsilon = 1.0
            noise = np.random.laplace(0, 1.0/epsilon)
            raw_result["count"] = max(0, int(raw_result["count"] + noise))
            raw_result["_dp_applied"] = True
            
        task.status = "COMPLETED"
        task.result = raw_result
        await self.results_queue.put(task)
