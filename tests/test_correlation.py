#!/usr/bin/env python3
"""
OSIN Correlation Service Test Suite
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_CORRELATION_URL", "http://localhost:8005")

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Correlation service not running")

def test_entity_resolution_linking():
    """Test that two signals mentioning the same entity are linked"""
    entity = {"name": "TestEntity_001", "type": "PERSON"}
    
    signal_1 = {
        "event_id": "sig_a",
        "text": "Signal A mentions TestEntity_001",
        "entities": [entity],
        "timestamp": time.time(),
        "source": "twitter",
        "confidence": 0.8
    }
    
    signal_2 = {
        "event_id": "sig_b",
        "text": "Signal B also mentions TestEntity_001",
        "entities": [entity],
        "timestamp": time.time() + 10,
        "source": "reddit",
        "confidence": 0.8
    }
    
    try:
        # Submit first signal
        resp1 = requests.post(f"{BASE_URL}/correlate", json=signal_1, timeout=5)
        assert resp1.status_code == 200
        
        # Submit second signal
        resp2 = requests.post(f"{BASE_URL}/correlate", json=signal_2, timeout=5)
        assert resp2.status_code == 200
        data = resp2.json()
        
        # Verify that sig_b is correlated with sig_a
        assert "sig_a" in data["correlated_ids"]
        assert data["new_edges"] > 0
    except requests.exceptions.ConnectionError:
        pytest.skip("Correlation service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
