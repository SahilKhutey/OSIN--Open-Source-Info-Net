#!/usr/bin/env python3
"""
OSIN Digital Forensics Service Test Suite
"""

import pytest
import requests
import time
import os
import io
import PIL.Image

BASE_URL = os.getenv("TEST_FORENSICS_URL", "http://localhost:8010")

def create_test_image(software_tag=None):
    """Create a temporary JPEG with optional software tag for metadata tampering tests"""
    img = PIL.Image.new('RGB', (100, 100), color='cyan')
    exif = img.getexif()
    if software_tag:
        exif[305] = software_tag # Software tag
        # Add basic GPS tag for geocoding tests
        gps_ifd = {
            1: 'N',
            2: ((34, 1), (3, 1), (800, 100)),
            3: 'W',
            4: ((118, 1), (14, 1), (3700, 100))
        }
        exif[34853] = gps_ifd

    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', exif=exif)
    img_io.seek(0)
    return img_io

def test_health_check():
    """Test forensics service health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Forensics service not running")

def test_metadata_integrity_audit():
    """Test detection of editing software in metadata (Ghiro-lite logic)"""
    # Create image tagged with "Adobe Photoshop"
    img_io = create_test_image(software_tag="Adobe Photoshop 2024")
    files = {'file': ('edited.jpg', img_io, 'image/jpeg')}
    data = {'analysis_depth': 'standard'}
    
    try:
        response = requests.post(f"{BASE_URL}/forensics-analysis", files=files, data=data, timeout=30)
        assert response.status_code == 200
        res = response.json()
        
        # Risk assessment should be high for edited images
        assert res["risk_assessment"]["tampering"] >= 0.7
        assert "Editing Software Detected" in res["tampering_indicators"]["indicators"]
        assert res["exif_analysis"]["Software"] == "Adobe Photoshop 2024"
    except requests.exceptions.ConnectionError:
        pytest.skip("Forensics service not running")

def test_clean_metadata_audit():
    """Test validation of clean, camera-original imagery"""
    img_io = create_test_image()
    files = {'file': ('clean.jpg', img_io, 'image/jpeg')}
    
    try:
        response = requests.post(f"{BASE_URL}/forensics-analysis", files=files, timeout=30)
        assert response.status_code == 200
        res = response.json()
        
        assert res["risk_assessment"]["tampering"] == 0.0
        assert not res["tampering_indicators"]["indicators"]
    except requests.exceptions.ConnectionError:
        pytest.skip("Forensics service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
