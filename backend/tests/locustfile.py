"""
Locust Load Testing Suite for OSIN
Simulates real user behavior and system load scenarios.

Usage:
    locust -f tests/locustfile.py --host=http://localhost:3000 -u 100 -r 10

Options:
    -u/--users: Number of concurrent users
    -r/--spawn-rate: Users spawned per second
    --headless: Run without web UI
    -t/--run-time: Test duration (e.g., "10m", "1h")
"""

from locust import HttpUser, task, between
import random
from datetime import datetime


class OSINDashboardUser(HttpUser):
    """Simulates a normal dashboard user."""

    wait_time = between(2, 5)

    def on_start(self):
        """Called when a simulated user starts."""
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "OSIN-LoadTest/1.0"
        }

    @task(5)
    def view_dashboard(self):
        """View main dashboard - most frequent action."""
        self.client.get("/", headers=self.headers)

    @task(3)
    def view_live_feed(self):
        """View live intelligence feed."""
        self.client.get("/api/events/recent", headers=self.headers)


class OSINAPIConsumer(HttpUser):
    """Simulates API consumer (external system integration)."""

    wait_time = between(1, 3)

    @task(8)
    def fetch_recent_events(self):
        """Fetch recent events via API."""
        params = {
            "limit": random.randint(10, 100),
            "offset": random.randint(0, 1000)
        }
        self.client.get("/api/v1/events", params=params)

    @task(5)
    def fetch_alerts(self):
        """Fetch active alerts."""
        self.client.get("/api/v1/alerts")


class OSINHighThroughputUser(HttpUser):
    """Simulates high-throughput ingestion user."""

    wait_time = between(0.5, 1.5)

    @task(10)
    def bulk_ingest_events(self):
        """Bulk ingest events."""
        batch_size = random.randint(50, 200)
        events = [
            {
                "id": f"bulk_{i}",
                "platform": random.choice(["twitter", "reddit", "news"]),
                "text": f"Event {i}",
                "timestamp": datetime.utcnow().isoformat()
            }
            for i in range(batch_size)
        ]
        self.client.post("/api/ingest/batch", json=events)


if __name__ == "__main__":
    print("Run with: locust -f tests/locustfile.py "
          "--host=http://localhost:3000")
