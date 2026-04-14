#!/usr/bin/env python3
"""
OSIN Unified Forensics Pro Service Test Suite
"""

import pytest
import requests
import time
import os
import io
import PIL.Image
import numpy as np

BASE_URL = os.getenv("TEST_FORENSICS_PRO_URL", "http://localhost:8011")

def create_tampered_image():
    """Create a JPEG with a clear 'tampered' region (solid block) for Cloned/ELA testing"""
    # Create background
    img_arr = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    
    # Add a 'tampered' clear rectangle (which will show up in ELA)
    img_arr[50:100, 50:100] = [255, 0, 0] # Solid red block
    
    # Save as high quality original
    img = PIL.Image.fromarray(img_arr)
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', quality=95)
    img_io.seek(0)
    return img_io

def test_health_check():
    """Test forensics pro service health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Forensics Pro service not running")

def test_ela_tamper_detection():
    """Test detection of abnormal compression variance via ELA"""
    img_io = create_tampered_image()
    files = {'file': ('tampered.jpg', img_io, 'image/jpeg')}
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-forensics", files=files, timeout=45)
        assert response.status_code == 200
        res = response.json()
        
        # Tampered regions should drive the ELA score higher than a clean noise floor
        assert res["ela_analysis"]["score"] > 0
        assert res["authenticity_score"] < 100.0
        assert res["risk_assessment"]["tampering"] > 0
    except requests.exceptions.ConnectionError:
        pytest.skip("Forensics Pro service not running")

def test_authenticity_indexing():
    """Test the unified truth index calculation"""
    # Create a clean random noise image (minimal tampering)
    img_arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = PIL.Image.fromarray(img_arr)
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', quality=98)
    img_io.seek(0)
    
    files = {'file': ('clean.jpg', img_io, 'image/jpeg')}
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-forensics", files=files, timeout=30)
        assert response.status_code == 200
        res = response.json()
        
        # High quality random noise should have a higher authenticity score than the red-blocked tampered version
        assert res["authenticity_score"] >= 80.0
    except requests.exceptions.ConnectionError:
        pytest.skip("Forensics Pro service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
