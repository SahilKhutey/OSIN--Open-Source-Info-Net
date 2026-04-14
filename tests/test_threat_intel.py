#!/usr/bin/env python3
"""
OSIN Advanced Threat Intelligence Engine Test Suite
"""

import pytest
import requests
import os

BASE_URL = os.getenv("TEST_THREAT_INTEL_URL", "http://localhost:8017")
X_API_KEY = "osin_master_threat_key_v350"

def test_health_check():
    """Test threat intel service health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Threat Intel service not running")

def test_threat_assessment_unauthorized():
    """Test if authentication is enforced"""
    payload = {"target": "example.com"}
    try:
        response = requests.post(f"{BASE_URL}/assess", json=payload, timeout=10)
        assert response.status_code == 403 # Missing header
    except requests.exceptions.ConnectionError:
        pytest.skip("Threat Intel service not running")

def test_threat_assessment_authorized():
    """Test authorized threat assessment initiation"""
    payload = {"target": "example.com"}
    headers = {"X-API-Key": X_API_KEY}
    
    try:
        response = requests.post(f"{BASE_URL}/assess", json=payload, headers=headers, timeout=30)
        assert response.status_code == 200
        res = response.json()
        assert res["target"] == "example.com"
        assert "threat_score" in res
        assert "components" in res
    except requests.exceptions.ConnectionError:
        pytest.skip("Threat Intel service not running")

def test_target_validation_lawful_boundaries():
    """Test if SecurityValidator prohibits unauthorized targets (e.g. private IP)"""
    payload = {"target": "192.168.1.1"}
    headers = {"X-API-Key": X_API_KEY}
    
    try:
        response = requests.post(f"{BASE_URL}/assess", json=payload, headers=headers, timeout=10)
        assert response.status_code == 400
        assert "prohibited target" in response.json()["detail"].lower()
    except requests.exceptions.ConnectionError:
        pytest.skip("Threat Intel service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
