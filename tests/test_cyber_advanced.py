#!/usr/bin/env python3
"""
OSIN Advanced Cyber Intelligence Engine Test Suite
"""

import pytest
import requests
import time
import os

BASE_URL = os.getenv("TEST_CYBER_ADVANCED_URL", "http://localhost:8015")

def test_health_check():
    """Test advanced cyber service health and tool status"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        res = response.json()
        assert res["status"] == "healthy"
        # Verify tool chain is reported
        assert "nmap" in res["tools"]
        assert "recon-ng" in res["tools"]
    except requests.exceptions.ConnectionError:
        pytest.skip("Advanced Cyber service not running")

def test_nmap_profile_execution():
    """Test if Nmap profiles are correctly prioritized and handled"""
    payload = {
        "target": "localhost",
        "scan_type": "quick",
        "dns_enum": False,
        "port_scan": True,
        "shodan_query": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/advanced-scan", json=payload, timeout=60)
        assert response.status_code == 200
        res = response.json()
        
        assert res["target"] == "localhost"
        assert res["network_intel"]["nmap"]["success"] is True
        assert res["network_intel"]["nmap"]["args"] == "-T4 -F"
    except requests.exceptions.ConnectionError:
        pytest.skip("Advanced Cyber service not running")

def test_risk_scoring_heuristics_v2():
    """Test advanced multi-factor risk scoring"""
    payload = {
        "target": "localhost",
        "scan_type": "comprehensive",
        "dns_enum": False,
        "port_scan": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/advanced-scan", json=payload, timeout=60)
        assert response.status_code == 200
        res = response.json()
        
        # Comprehensive scan should trigger 'vulnerability' risk factor
        assert res["risk_assessment"]["risk_score"] >= 25
        assert any("Vulnerability" in f for f in res["risk_assessment"]["factors"])
    except requests.exceptions.ConnectionError:
        pytest.skip("Advanced Cyber service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
