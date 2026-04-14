#!/usr/bin/env python3
"""
OSIN Mapillary Intelligence Service Test Suite
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_MAPILLARY_URL", "http://localhost:8006")

def test_health_check():
    """Test service health and API token status"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Mapillary service not running")

def test_street_intel_retrieval():
    """Test image retrieval for a known coordinate (LA)"""
    test_event = {
        "event_id": "test_la_001",
        "lat": 34.0522,
        "lon": -118.2437,
        "text": "Signal in downtown Los Angeles",
        "confidence": 0.5,
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/street-intel", json=test_event, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        assert data["event_id"] == "test_la_001"
        assert "images_found" in data
        assert isinstance(data["images"], list)
        
        # Coverage quality should be a float between 0 and 1
        assert 0 <= data["coverage_quality"] <= 1.0
        assert data["confidence_impact"] >= 0.5
    except requests.exceptions.ConnectionError:
        pytest.skip("Mapillary service not running")

def test_no_coverage_area():
    """Test response in areas with likely no street coverage (middle of ocean)"""
    test_event = {
        "event_id": "test_ocean_001",
        "lat": 0.0,
        "lon": 0.0,
        "text": "Signal in the middle of the Atlantic",
        "confidence": 0.8,
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/street-intel", json=test_event, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        assert data["images_found"] == 0
        assert data["coverage_quality"] == 0.0
        # Confidence should remain unchanged if no verification images found
        assert data["confidence_impact"] == 0.8
    except requests.exceptions.ConnectionError:
        pytest.skip("Mapillary service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
