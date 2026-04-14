#!/usr/bin/env python3
"""
OSIN Signal & Leak Intelligence Engine Test Suite
"""

import pytest
import requests
import os

BASE_URL = os.getenv("TEST_SIGNAL_INTEL_URL", "http://localhost:8016")

def test_health_check():
    """Test signal intel service health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Signal Intel service not running")

def test_signal_scan_execution():
    """Test if signal scans are correctly initiated and handled"""
    payload = {
        "target": "example.com",
        "intel_type": "basic",
        "include_emails": True,
        "include_leaks": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signal-scan", json=payload, timeout=30)
        assert response.status_code == 200
        res = response.json()
        
        assert res["target"] == "example.com"
        assert "request_id" in res
        assert "risk_assessment" in res
    except requests.exceptions.ConnectionError:
        pytest.skip("Signal Intel service not running")

def test_risk_scoring_signals():
    """Test risk scoring logic for email exposure"""
    payload = {
        "target": "leak-test@example.com",
        "intel_type": "comprehensive"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signal-scan", json=payload, timeout=30)
        assert response.status_code == 200
        res = response.json()
        
        # Verify metadata fields
        assert "processing_time_ms" in res["metadata"]
        assert res["email_intel"]["source"] == "theHarvester"
    except requests.exceptions.ConnectionError:
        pytest.skip("Signal Intel service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
