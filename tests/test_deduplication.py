#!/usr/bin/env python3
"""
Comprehensive test suite for OSIN Deduplication Service v2.1.0
"""

import pytest
import requests
import json
import time
import os
from typing import List, Dict

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8002")
TEST_TIMEOUT = 30

def test_health_check():
    """Test service health endpoint with expanded v2.1 metrics"""
    response = requests.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] == True
    assert "all-MiniLM" in data["model_name"]
    assert "uptime_seconds" in data
    assert "total_batches_processed" in data
    assert "avg_processing_time_ms" in data

def test_metrics_endpoint():
    """Test metrics endpoint for configuration and memory usage"""
    response = requests.get(f"{BASE_URL}/metrics", timeout=TEST_TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert data["max_workers"] == 4
    assert data["batch_size"] == 1000
    assert data["similarity_threshold"] == 0.85
    assert "memory_usage_mb" in data

def test_basic_deduplication():
    """Test basic deduplication clustering functionality"""
    test_data = {
        "events": [
            {
                "id": "event_001",
                "text": "Explosion reported in New York near Tesla HQ",
                "source": "twitter",
                "timestamp": time.time()
            },
            {
                "id": "event_002", 
                "text": "Blast near Tesla office NYC",
                "source": "reddit",
                "timestamp": time.time()
            },
            {
                "id": "event_003",
                "text": "Stock market rises in Asia trading session",
                "source": "news",
                "timestamp": time.time()
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/deduplicate",
        json=test_data,
        timeout=TEST_TIMEOUT
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert "clusters" in result
    assert result["total_events"] == 3
    assert len(result["clusters"]) == 2  # Two unique events expected
    
    # Check that similar events are clustered
    cluster_sizes = [len(cluster) for cluster in result["clusters"]]
    assert 2 in cluster_sizes  # Two similar events (001 and 002)
    assert 1 in cluster_sizes  # One unique event (003)
    
    # Verify specific event clustering
    events_1_2_clustered = any(
        "event_001" in cluster and "event_002" in cluster 
        for cluster in result["clusters"]
    )
    assert events_1_2_clustered, "Similar events (NYC blast) should be clustered together"

def test_empty_batch():
    """Test handling of empty batch (should return 400)"""
    response = requests.post(
        f"{BASE_URL}/deduplicate",
        json={"events": []},
        timeout=TEST_TIMEOUT
    )
    assert response.status_code == 400

def test_large_batch():
    """Test handling of larger batch with multiple duplicates"""
    events = []
    # 10 distinct events
    for i in range(10):
        events.append({
            "id": f"distinct_event_{i}",
            "text": f"This is a unique test signal for event number {i} regarding regional activity.",
            "source": "test"
        })
    
    # 3 duplicate sets
    for i in range(3):
        events.append({
            "id": f"duplicate_{i}_a",
            "text": f"Crucial update: System anomaly {i} detected in the network.",
            "source": "test"
        })
        events.append({
            "id": f"duplicate_{i}_b",
            "text": f"System anomaly {i} was detected in the network (alert).",
            "source": "test"
        })
    
    response = requests.post(
        f"{BASE_URL}/deduplicate",
        json={"events": events},
        timeout=TEST_TIMEOUT
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # should have 10 (distinct) + 3 (clustered pairs) = 13 unique clusters
    assert result["total_events"] == 16
    assert result["unique_events"] == 13
    
    # Check for clusters of size 2
    clusters_of_2 = [len(c) for c in result["clusters"] if len(c) == 2]
    assert len(clusters_of_2) == 3

def test_performance_metrics():
    """Test that performance metrics are correctly calculated and returned"""
    test_data = {
        "events": [
            {"id": "perf_1", "text": "Signal one for performance test", "source": "test"},
            {"id": "perf_2", "text": "Signal two for performance test", "source": "test"}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/deduplicate",
        json=test_data,
        timeout=TEST_TIMEOUT
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert "processing_time_ms" in result
    assert "timestamp" in result
    assert result["processing_time_ms"] > 0
    assert result["total_events"] == 2

def test_multilingual_semantic_clustering():
    """Test cross-lingual semantic matching (if supported by model)"""
    test_data = {
        "events": [
            {"id": "en_1", "text": "Major protest in Paris today", "source": "twitter"},
            {"id": "fr_1", "text": "Grande manifestation à Paris aujourd'hui", "source": "twitter"}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/deduplicate",
        json=test_data,
        timeout=TEST_TIMEOUT
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # Note: all-MiniLM-L6-v2 has some multilingual capabilities but isn't as robust as paraphrase-multilingual
    # We check if they clustered or not just to see system behavior
    logger = json.dumps(result["clusters"])
    print(f"Multilingual clusters: {logger}")

if __name__ == "__main__":
    # Wait for service to be ready
    print("Waiting for deduplication service to be ready...")
    for _ in range(45):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("Service is ready!")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("Service not ready after 45 seconds")
        exit(1)
    
    # Run tests
    pytest.main([__file__, "-v"])
