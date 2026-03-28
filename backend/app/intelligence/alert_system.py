from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class AlertLevel(Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"

@dataclass
class IntelligenceAlert:
    id: str
    level: AlertLevel
    title: str
    description: str
    credibility_score: float
    timestamp: datetime

class RealTimeAlertSystem:
    """Military-grade 5-tier alert system"""
    
    def __init__(self):
        self.thresholds = {
            AlertLevel.ROUTINE: 0.3,
            AlertLevel.ELEVATED: 0.5,
            AlertLevel.HIGH: 0.7,
            AlertLevel.SEVERE: 0.85,
            AlertLevel.CRITICAL: 0.95
        }
    
    async def evaluate_event(self, event: Dict) -> List[IntelligenceAlert]:
        """Evaluates event against 5-tier thresholds and triggers alerts"""
        score = event.get('credibility_score', 0)
        level = self._determine_alert_level(score)
        
        alerts = []
        if score > self.thresholds[AlertLevel.HIGH]:
            print(f"ALERT: Triggering {level.value} alert for event {event.get('id')}")
            alert = IntelligenceAlert(
                id=f"ALT-{random.getrandbits(32)}",
                level=level,
                title=f"{level.value} Critical Signal Detected",
                description=f"Intelligence signal with {score:.2f} credibility verified.",
                credibility_score=score,
                timestamp=datetime.utcnow()
            )
            alerts.append(alert)
            await self._distribute_alert(alert)
            
        return alerts

    def _determine_alert_level(self, score: float) -> AlertLevel:
        if score >= 0.95: return AlertLevel.CRITICAL
        if score >= 0.85: return AlertLevel.SEVERE
        if score >= 0.70: return AlertLevel.HIGH
        if score >= 0.50: return AlertLevel.ELEVATED
        return AlertLevel.ROUTINE

    async def _distribute_alert(self, alert: IntelligenceAlert):
        # Distribution logic (WebSocket, Email, SMS placeholders)
        print(f"DISTRIBUTION: Alert {alert.id} pushed to Command Center.")

alert_system = RealTimeAlertSystem()
