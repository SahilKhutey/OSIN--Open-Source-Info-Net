#!/usr/bin/env python3
"""
OSIN Geo-Tagging Service Test Suite
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_GEOTAGGING_URL", "http://localhost:8004")

def test_health_check():
    """Test service health and connectivity"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["nlp_model_loaded"] is True
    except requests.exceptions.ConnectionError:
        pytest.skip("Geo-tagging service not running")

def test_geotagging_extraction():
    """Test location extraction from text"""
    test_data = {
        "text": "Report of intense fire near Tesla HQ in New York City",
        "source": "test",
        "confidence": 0.7
    }
    
    try:
        response = requests.post(f"{BASE_URL}/geotag", json=test_data, timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        # Verify locations found
        found_locations = [loc["location"] for loc in data["locations"]]
        assert "New York City" in found_locations
        
        # Verify coordinates attached
        nyc = next(loc for loc in data["locations"] if loc["location"] == "New York City")
        assert 40.0 < nyc["lat"] < 41.0
        assert -75.0 < nyc["lon"] < -73.0
        assert npc["confidence"] > 0.7
    except requests.exceptions.ConnectionError:
        pytest.skip("Geo-tagging service not running")

def test_geotagging_multiple_cities():
    """Test extraction of multiple geographic entities"""
    test_data = {
        "text": "Storms hitting London, Paris, and Berlin simultaneously."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/geotag", json=test_data, timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        locations = [loc["location"] for loc in data["locations"]]
        assert len(locations) >= 3
        assert "London" in locations
        assert "Paris" in locations
        assert "Berlin" in locations
    except requests.exceptions.ConnectionError:
        pytest.skip("Geo-tagging service not running")

def test_invalid_input_short_text():
    """Test handling of insufficiently long text"""
    try:
        response = requests.post(f"{BASE_URL}/geotag", json={"text": "NYC"}, timeout=5)
        assert response.status_code == 400
    except requests.exceptions.ConnectionError:
        pytest.skip("Geo-tagging service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
