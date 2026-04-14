#!/usr/bin/env python3
"""
OSIN Topographic Intelligence Service Test Suite
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_TOPOMAP_URL", "http://localhost:8008")

def test_health_check():
    """Test service health and Redis connectivity"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("TopoMap service not running")

def test_topo_intel_retrieval():
    """Test elevation lookup and risk analysis for a known coordinate (Mount Everest region)"""
    test_event = {
        "event_id": "test_everest_001",
        "lat": 27.9881,
        "lon": 86.9250,
        "text": "Base camp signal detected",
        "event_type": "expedition",
        "confidence": 0.7,
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/topo-intel", json=test_event, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        assert data["event_id"] == "test_everest_001"
        assert "elevation_data" in data
        assert data["elevation_data"]["center"] > 5000  # Everest base camp is >5000m
        
        # Check slope analysis
        assert "terrain_analysis" in data
        assert data["terrain_analysis"]["slope"]["max_slope_deg"] > 0
        
        # Check risk assessment
        assert "risk_assessment" in data
        assert "landslide" in data["risk_assessment"]
    except requests.exceptions.ConnectionError:
        pytest.skip("TopoMap service not running")

def test_flat_terrain_analysis():
    """Test terrain analysis for a known flat area (Netherlands)"""
    test_event = {
        "event_id": "test_flat_001",
        "lat": 52.3676,
        "lon": 4.9041,
        "text": "Amsterdam signal",
        "confidence": 0.8,
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/topo-intel", json=test_event, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        assert data["elevation_data"]["center"] < 50
        assert data["terrain_analysis"]["slope"]["max_slope_deg"] < 5
        # Flood risk should be high in Amsterdam (low elevation)
        assert data["risk_assessment"]["flooding"] > 0.5
    except requests.exceptions.ConnectionError:
        pytest.skip("TopoMap service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
