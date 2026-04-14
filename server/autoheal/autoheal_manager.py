import time
import requests
import logging
import docker
import os
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OSIN-AutoHeal")

# Configuration from Environment
HEALTH_MONITOR_URL = os.getenv("HEALTH_MONITOR_URL", "http://health-monitor:8002/health")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "15"))
RESTART_THRESHOLD = int(os.getenv("RESTART_THRESHOLD", "3"))  # Number of consecutive failures
COOLDOWN_PERIOD = int(os.getenv("COOLDOWN_PERIOD", "60"))    # Seconds to wait after restart

class AutoHealManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Connected to Docker daemon successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Docker daemon: {e}")
            self.client = None
            
        self.failure_counters = {}
        self.last_restart_time = {}

    def get_service_status(self) -> Dict:
        try:
            response = requests.get(HEALTH_MONITOR_URL, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch health status: {e}")
        return {}

    def restart_container(self, container_name: str):
        if not self.client:
            logger.error("Docker client not initialized. Cannot restart.")
            return

        # Check cooldown
        now = time.time()
        if container_name in self.last_restart_time:
            if now - self.last_restart_time[container_name] < COOLDOWN_PERIOD:
                logger.warning(f"Container {container_name} in cooldown. Skipping restart.")
                return

        try:
            # Map OSIN service names to container names
            # Note: In docker-compose, container names are usually [project]_[service]_1
            # We will search by label or exact match
            logger.info(f"Attempting to restart container matching service: {container_name}")
            
            containers = self.client.containers.list(all=True)
            target = None
            for c in containers:
                if container_name in c.name: # Simple match logic
                    target = c
                    break
            
            if target:
                logger.warning(f"RESTARTING container: {target.name}")
                target.restart()
                self.last_restart_time[container_name] = now
                self.failure_counters[container_name] = 0
            else:
                logger.error(f"Could not find container for service: {container_name}")
        except Exception as e:
            logger.error(f"Error during restart of {container_name}: {e}")

    def run(self):
        logger.info(f"AutoHealManager started. Interval: {CHECK_INTERVAL}s")
        while True:
            try:
                health_data = self.get_service_status()
                if not health_data:
                    time.sleep(CHECK_INTERVAL)
                    continue

                for service_name, status_info in health_data.items():
                    if service_name in ["system", "overall_status"]:
                        continue
                    
                    status = status_info.get("status")
                    if status == "DOWN":
                        self.failure_counters[service_name] = self.failure_counters.get(service_name, 0) + 1
                        logger.warning(f"Service {service_name} is DOWN ({self.failure_counters[service_name]}/{RESTART_THRESHOLD})")
                        
                        if self.failure_counters[service_name] >= RESTART_THRESHOLD:
                            self.restart_container(service_name)
                    else:
                        self.failure_counters[service_name] = 0
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
            
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    manager = AutoHealManager()
    manager.run()
