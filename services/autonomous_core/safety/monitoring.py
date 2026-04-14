"""
OSIN Safety and Monitoring System
Ensures autonomous intelligence operations remain within policy and resource boundaries
"""

from typing import Dict, List, Any
from datetime import datetime
import asyncio
import logging

class SafetyMonitor:
    """Watchdog for the OSIN Autonomous Intelligence Organism"""
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.safety_log = []
        self.thresholds = {
            "max_cpu_percent": 80.0,
            "max_action_frequency_hz": 1.0,  # 1 action per second
            "daily_action_budget": 500
        }
        self.logger = logging.getLogger("osin-safety")
        
    async def monitor_loop(self):
        """Continuous safety audit of the autonomous process"""
        self.logger.info("Initializing OSIN Safety Sentinel")
        while True:
            try:
                # 1. Audit Action Rates
                if self.orchestrator.autonomous_agent.actions_executed > self.thresholds['daily_action_budget']:
                    self._enforce_governance("Daily Action Budget Exceeded")
                
                # 2. Check for Resource Anomalies
                # (Mock check, in prod we use psutil)
                mock_cpu = 45.0 
                if mock_cpu > self.thresholds['max_cpu_percent']:
                    self._enforce_governance("High Resource Usage detected in Autonomous Core")
                
                await asyncio.sleep(60) # High-level audit every minute
            except Exception as e:
                self.logger.error(f"Safety monitor error: {e}")
                await asyncio.sleep(30)
                
    def _enforce_governance(self, reason: str):
        """Immediately throttle or restrict autonomous capabilities"""
        self.logger.warning(f"OSIN SAFETY PROTOCOL TRIGGERED: {reason}")
        self.orchestrator.is_running = False # Emergency Stop
        self._log_event(reason, "EMERGENCY_HALT")
        
    def _log_event(self, reason: str, action: str):
        self.safety_log.append({
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "action_taken": action
        })
