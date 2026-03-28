import os
from celery import Celery
from app.config import settings

celery_app = Celery(
    "osin_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="process_signal")
def process_signal_task(signal_data):
    # This will be refined to include cleaning, clustering, and AI scoring
    print(f"Processing signal: {signal_data.get('id')}")
    return {"status": "processed", "id": signal_data.get("id")}
