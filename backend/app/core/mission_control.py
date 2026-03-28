from typing import Dict
from app.core.global_orchestrator import global_deploy
from app.core.security import osin_security
from app.core.redundancy_protocols import phoenix_protocol

class MissionControl:
    """
    Unified Command & Control Layer for global OSIN operations.
    """
    def __init__(self):
        self.operation_name = "GLOBAL DOMINANCE"
        self.deployment = global_deploy
        self.security = osin_security

    async def initialize_world_state(self):
        """
        Activates all regional hubs and verifies security backbone.
        """
        await self.deployment.global_monitoring_activation()
        self.security.log_immutable("OSIN GLOBAL STATE INITIALIZED")
        return "READY"

    def trigger_regional_recovery(self, zone: str):
        """
        Triggers Protocol Phoenix for a specific zone.
        """
        self.security.log_immutable(f"RECOVERY TRIGGERED: {zone}")
        return phoenix_protocol.initiate_rebuild(zone)

    def get_tactical_overview(self) -> Dict:
        """
        Returns combined health and status of all global units.
        """
        return {
            'hubs': self.deployment.get_global_status(),
            'opsec_level': 'ULTIMATE',
            'audit_count': len(self.security.immutable_logs)
        }

mission_control = MissionControl()
