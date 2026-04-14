import time
import requests
import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OSIN-AlertManager")

# Configuration from Environment
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
HEALTH_MONITOR_URL = os.getenv("HEALTH_MONITOR_URL", "http://health-monitor:8002/health")
ALERT_INTERVAL = int(os.getenv("ALERT_INTERVAL", "30"))  # Seconds between checks
SILENCE_PERIOD = int(os.getenv("SILENCE_PERIOD", "3600")) # Duration to silence same alert

class AlertManager:
    def __init__(self):
        self.sent_alerts = {} # {service_name: last_sent_timestamp}
        self.last_overall_status = "HEALTHY"

    def send_notification(self, title: str, message: str, severity: str = "critical"):
        color = "#ff0000" if severity == "critical" else "#ffa500"
        
        # Slack Payload
        slack_payload = {
            "attachments": [{
                "fallback": f"OSIN ALERT: {title}",
                "color": color,
                "title": title,
                "text": message,
                "footer": "OSIN SVP-2 Alerting Engine",
                "ts": int(time.time())
            }]
        }

        # Discord Payload
        discord_payload = {
            "content": f"**[OSIN ALERT - {severity.upper()}]**\n**{title}**\n{message}"
        }

        if SLACK_WEBHOOK_URL:
            try:
                requests.post(SLACK_WEBHOOK_URL, json=slack_payload, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")

        if DISCORD_WEBHOOK_URL:
            try:
                requests.post(DISCORD_WEBHOOK_URL, json=discord_payload, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send Discord alert: {e}")

        logger.info(f"NOTIFICATION SENT: {title} - {message}")

    def process_health_data(self, data: Dict):
        now = time.time()
        overall_status = data.get("overall_status", "UNKNOWN")

        # Track state transitions
        if overall_status != self.last_overall_status:
            if overall_status == "DEGRADED":
                self.send_notification("System Status: DEGRADED", "One or more services have failed health checks.")
            elif overall_status == "HEALTHY" and self.last_overall_status == "DEGRADED":
                self.send_notification("System Status: RECOVERED", "All services are back online.", severity="info")
            self.last_overall_status = overall_status

        # Check individual services
        for service_name, status_info in data.items():
            if service_name in ["system", "overall_status"]:
                continue

            status = status_info.get("status")
            if status == "DOWN":
                last_sent = self.sent_alerts.get(service_name, 0)
                if now - last_sent > SILENCE_PERIOD:
                    error_msg = status_info.get("error", "Unknown connection error")
                    self.send_notification(
                        f"Service Failure: {service_name}",
                        f"Health check failed for service `{service_name}`.\nDetails: `{error_msg}`"
                    )
                    self.sent_alerts[service_name] = now
            else:
                # Clear from sent alerts if service is back UP
                if service_name in self.sent_alerts:
                    del self.sent_alerts[service_name]

    def run(self):
        logger.info("AlertManager operational. Starting heartbeat monitor...")
        while True:
            try:
                response = requests.get(HEALTH_MONITOR_URL, timeout=5)
                if response.status_code == 200:
                    self.process_health_data(response.json())
                else:
                    logger.error(f"Health monitor returned {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to connect to health-monitor: {e}")
            
            time.sleep(ALERT_INTERVAL)

if __name__ == "__main__":
    manager = AlertManager()
    manager.run()
