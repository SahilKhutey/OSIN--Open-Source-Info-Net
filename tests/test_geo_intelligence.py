#!/usr/bin/env python3
"""
Comprehensive test suite for OSIN Geo-Intelligence Service v2.1.0-enhanced
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_GEO_SERVICE_URL", "http://localhost:8003")

def test_health_check():
    """Test health check and status"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Geo-intelligence service not running")

def test_layer_selection_inference_fire():
    """Test that fire-related and sensor-weighted logic works for fire keywords"""
    test_event = {
        "event_id": "test_inferred_fire",
        "text": "Intense burning reported in the state forest, thermal signatures detected.",
        "lat": 36.77,
        "lon": -119.41,
        "timestamp": time.time(),
        "source": "twitter",
        "confidence": 0.6
    }
    
    try:
        response = requests.post(f"{BASE_URL}/geo-intel", json=test_event, timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        # Verify layer selection (Inferred Type: Fire)
        layers = data["layers"].keys()
        assert any("FIRES_VIIRS" in l for l in layers)
        assert any("FIRES_MODIS" in l for l in layers)
        
        # Verify weighted confidence boost
        # VIIRS (0.3) + MODIS (0.25) + TRUE_COLOR (0.1) = 0.65 -> capped at 0.4 boost
        # 0.6 + 0.4 = 1.0
        assert data["confidence_impact"] > 0.95
        assert data["analysis"]["event_type_inferred"] == "fire"
    except requests.exceptions.ConnectionError:
        pytest.skip("Geo-intelligence service not running")

def test_layer_selection_inference_flood():
    """Test that flood keywords trigger the Precipitation layer"""
    test_event = {
        "event_id": "test_inferred_flood",
        "text": "Severe rainfall and flash flooding across the metropolitan area.",
        "lat": 29.76,
        "lon": -95.36,
        "timestamp": time.time(),
        "source": "news",
        "confidence": 0.5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/geo-intel", json=test_event, timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        layers = data["layers"].keys()
        assert any("PRECIPITATION" in l for l in layers)
        assert data["analysis"]["event_type_inferred"] == "flood"
        # TRUE_COLOR (0.1) + PRECIPITATION (0.15) = 0.25 boost -> 0.5 + 0.25 = 0.75
        assert 0.74 <= data["confidence_impact"] <= 0.76
    except requests.exceptions.ConnectionError:
        pytest.skip("Geo-intelligence service not running")

def test_manual_layer_override():
    """Test passing an explicit event_type for layer selection"""
    test_event = {
        "event_id": "test_manual_type",
        "text": "Strange activity detected near the power grid.",
        "lat": 34.05,
        "lon": -118.24,
        "timestamp": time.time(),
        "source": "intel",
        "confidence": 0.4,
        "event_type": "power_outage"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/geo-intel", json=test_event, timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        layers = data["layers"].keys()
        assert any("NIGHT_LIGHTS" in l for l in layers)
        assert data["analysis"]["event_type_inferred"] == "power_outage"
    except requests.exceptions.ConnectionError:
        pytest.skip("Geo-intelligence service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
