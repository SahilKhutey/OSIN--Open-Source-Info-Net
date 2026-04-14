#!/usr/bin/env python3
"""
OSIN Pic2Map Intelligence Service Test Suite
"""

import pytest
import requests
import time
import os
import io
import PIL.Image
import PIL.ExifTags

BASE_URL = os.getenv("TEST_PIC2MAP_URL", "http://localhost:8009")

def create_geotagged_image():
    """Create a temporary JPEG with GPS EXIF metadata for testing"""
    img = PIL.Image.new('RGB', (100, 100), color='blue')
    
    # Simple GPS decimal-to-DMS conversion for test header
    # Test Location: Los Angeles (34.0522, -118.2437)
    exif = img.getexif()
    gps_ifd = {
        1: 'N',
        2: ((34, 1), (3, 1), (800, 100)), # 34 deg, 3 min, 8 sec
        3: 'W',
        4: ((118, 1), (14, 1), (3700, 100)) # 118 deg, 14 min, 37 sec
    }
    exif[34853] = gps_ifd # GPS tag
    
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', exif=exif)
    img_io.seek(0)
    return img_io

def test_health_check():
    """Test service health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Pic2Map service not running")

def test_image_geolocation_extraction():
    """Test extraction of GPS and metadata from a geocoded image"""
    img_io = create_geotagged_image()
    files = {'file': ('test_geo.jpg', img_io, 'image/jpeg')}
    data = {'source': 'pytest_validation', 'event_id': 'auto_test_001'}
    
    try:
        response = requests.post(f"{BASE_URL}/image-intel", files=files, data=data, timeout=30)
        assert response.status_code == 200
        res = response.json()
        
        assert res["event_id"] == "auto_test_001"
        assert res["gps_data"] is not None
        assert 34.0 <= res["gps_data"]["lat"] <= 34.1
        assert -118.3 <= res["gps_data"]["lon"] <= -118.2
        assert res["location_analysis"]["is_geolocated"] is True
        assert "Los Angeles" in res["location_analysis"]["location_name"]
    except requests.exceptions.ConnectionError:
        pytest.skip("Pic2Map service not running")

def test_non_geocoded_image():
    """Test handling of images without GPS data"""
    img = PIL.Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    files = {'file': ('no_geo.jpg', img_io, 'image/jpeg')}
    
    try:
        response = requests.post(f"{BASE_URL}/image-intel", files=files, timeout=30)
        assert response.status_code == 200
        res = response.json()
        assert res["gps_data"] is None
        assert res["location_analysis"]["is_geolocated"] is False
    except requests.exceptions.ConnectionError:
        pytest.skip("Pic2Map service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
