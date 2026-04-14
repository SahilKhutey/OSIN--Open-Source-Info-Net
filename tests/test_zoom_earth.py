#!/usr/bin/env python3
"""
OSIN Zoom Earth Intelligence Service Test Suite
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_ZOOM_EARTH_URL", "http://localhost:8007")

def test_health_check():
    """Test service health and API token status"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Zoom Earth service not running")

def test_weather_intel_enrichment():
    """Test atmospheric enrichment and alert retrieval for a known point"""
    test_event = {
        "event_id": "test_storm_001",
        "lat": 34.0522,
        "lon": -118.2437,
        "text": "Storm surge reported along the California coast",
        "event_type": "storm",
        "confidence": 0.6,
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/weather-intel", json=test_event, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        assert data["event_id"] == "test_storm_001"
        assert "weather_layers" in data
        assert "clouds" in data["weather_layers"]
        
        # Check impact boosting
        # If alerts were found, confidence should be boosted
        assert data["confidence_impact"] >= 0.6
    except requests.exceptions.ConnectionError:
        pytest.skip("Zoom Earth service not running")

def test_placeholder_key_behavior():
    """Verify that service gracefully handles placeholder API keys"""
    # This assumes the service is running with OPENWEATHER_API_KEY=PLACEHOLDER
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        if not data["api_configured"]:
            # If not configured, enrichment should still return layers metadata but no live telemetry
            test_event = {"event_id": "pk_test", "lat": 0, "lon": 0, "text": "test", "timestamp": time.time(), "confidence": 0.5}
            resp = requests.post(f"{BASE_URL}/weather-intel", json=test_event)
            assert resp.status_code == 200
            assert resp.json()["current_weather"] is None
    except requests.exceptions.ConnectionError:
        pytest.skip("Zoom Earth service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
