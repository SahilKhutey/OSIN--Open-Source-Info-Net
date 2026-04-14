#!/usr/bin/env python3
"""
OSIN ArcGIS Intelligence Service Test Suite
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_ARCGIS_URL", "http://localhost:8005")

def test_health_check():
    """Test service health and connectivity"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert len(data["services_available"]) > 0
    except requests.exceptions.ConnectionError:
        pytest.skip("ArcGIS service not running")

def test_arcgis_enrichment_earthquake():
    """Test enrichment for a seismic event in California"""
    test_event = {
        "event_id": "test_quake_001",
        "lat": 34.05,
        "lon": -118.25,
        "text": "Tremor felt in downtown LA area",
        "event_type": "earthquake",
        "confidence": 0.6,
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/arcgis-intel", json=test_event, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        assert data["event_id"] == "test_quake_001"
        assert "earthquakes" in data["services_queried"]
        # Even if no earthquakes happened in last 7 days, the response structure should be valid
        assert "features_found" in data
        assert data["confidence_impact"] >= 0.6
    except requests.exceptions.ConnectionError:
        pytest.skip("ArcGIS service not running")

def test_arcgis_enrichment_fire():
    """Test enrichment for a fire event near infrastructure"""
    test_event = {
        "event_id": "test_fire_001",
        "lat": 34.05,
        "lon": -118.25,
        "text": "Smoke plumes detected near the power station",
        "event_type": "fire",
        "confidence": 0.5,
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/arcgis-intel", json=test_event, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Should have queried both wildfires and infrastructure
        assert "wildfires" in data["services_queried"]
        assert "infrastructure" in data["services_queried"]
    except requests.exceptions.ConnectionError:
        pytest.skip("ArcGIS service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
