#!/usr/bin/env python3
"""
OSIN Cyber Intelligence Engine Test Suite
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_CYBER_INTEL_URL", "http://localhost:8014")

def test_health_check():
    """Test cyber intel service health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Cyber Intel service not running")

def test_dns_reconnaissance():
    """Test standard DNS reconnaissance on a known target"""
    payload = {
        "target": "google.com",
        "analysis_type": "standard",
        "include_active": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-cyber", json=payload, timeout=30)
        assert response.status_code == 200
        res = response.json()
        
        assert res["target"] == "google.com"
        assert res["domain_intel"]["dns"]["success"] is True
        # Google should have A and MX records
        assert len(res["domain_intel"]["dns"]["records"]["A"]) > 0
        assert len(res["domain_intel"]["dns"]["records"]["MX"]) > 0
        assert "risk_score" in res["risk_assessment"]
    except requests.exceptions.ConnectionError:
        pytest.skip("Cyber Intel service not running")

def test_risk_assessment_heuristics():
    """Test if risk assessment correctly identifies common factors"""
    # Using a non-existent or minimal domain
    payload = {
        "target": "example.invalid",
        "analysis_type": "quick"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-cyber", json=payload, timeout=10)
        assert response.status_code == 200
        res = response.json()
        
        # example.invalid should have 0 records, triggering the risk factors
        if len(res["domain_intel"]["dns"]["records"]["MX"]) == 0:
            assert "No MX records detected" in res["risk_assessment"]["factors"]
    except requests.exceptions.ConnectionError:
        pytest.skip("Cyber Intel service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
