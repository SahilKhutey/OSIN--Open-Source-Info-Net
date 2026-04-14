#!/usr/bin/env python3
"""
OSIN Audio Intelligence Engine Test Suite
"""

import pytest
import requests
import time
import os
import io
import numpy as np
import soundfile as sf

BASE_URL = os.getenv("TEST_AUDIO_INTEL_URL", "http://localhost:8012")

def create_test_audio(duration=2.0, frequency=440):
    """Create a temporary WAV file for testing (Sine wave)"""
    sr = 16000
    t = np.linspace(0, duration, int(sr * duration))
    y = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    img_io = io.BytesIO()
    sf.write(img_io, y, sr, format='WAV')
    img_io.seek(0)
    return img_io

def test_health_check():
    """Test audio intel service health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Audio Intel service not running")

def test_spectral_feature_extraction():
    """Test extraction of spectral centroid and RMS energy"""
    # Create 440Hz sine wave (Pure tone)
    audio_io = create_test_audio(frequency=440)
    files = {'file': ('test.wav', audio_io, 'audio/wav')}
    data = {'source': 'pytest_validation'}
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-audio", files=files, data=data, timeout=30)
        assert response.status_code == 200
        res = response.json()
        
        assert res["audio_metadata"]["duration"] >= 2.0
        assert res["audio_metadata"]["spectral_centroid_mean"] > 0
        assert res["audio_metadata"]["rms_energy_mean"] > 0
        assert res["confidence_score"] > 0
    except requests.exceptions.ConnectionError:
        pytest.skip("Audio Intel service not running")

def test_scene_classification_heuristics():
    """Test heuristic scene classification triggers"""
    # High frequency, high energy (should trigger urban_traffic heuristic)
    t = np.linspace(0, 1.0, 16000)
    # Mix high frequency noise with sine wave
    y = 0.8 * np.sin(2 * np.pi * 3000 * t) + 0.2 * np.random.randn(len(t))
    
    img_io = io.BytesIO()
    sf.write(img_io, y, 16000, format='WAV')
    img_io.seek(0)
    
    files = {'file': ('traffic_sim.wav', img_io, 'audio/wav')}
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-audio", files=files, timeout=30)
        assert response.status_code == 200
        res = response.json()
        assert res["scene_classification"]["scene_type"] == "urban_traffic"
        assert res["scene_classification"]["confidence"] >= 0.8
    except requests.exceptions.ConnectionError:
        pytest.skip("Audio Intel service not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
