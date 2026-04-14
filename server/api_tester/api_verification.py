import requests
import time
import json
import threading
from datetime import datetime

class APIVerifier:
    """
    SVP-1 API Reliability Suite.
    Performs scheduled health validation, endpoint capability checks, 
    and micro-load testing for the OSIN intelligence API layer.
    """
    def __init__(self, base_url="http://backend:8000"):
        self.base_url = base_url
        self.results = []
    
    def test_health(self):
        """Verify the primary system health endpoint"""
        start = time.time()
        try:
            res = requests.get(f"{self.base_url}/health", timeout=5)
            latency = (time.time() - start) * 1000
            
            success = res.status_code == 200
            print(f"[{'PASSED' if success else 'FAILED'}] HEALTH_CHECK // Latency: {latency:.2f}ms")
            
            self.results.append({"test": "health", "success": success, "latency": latency})
            return success
        except Exception as e:
            print(f"[FAILED] HEALTH_CHECK // Error: {e}")
            return False

    def test_intelligence_stream(self):
        """Verify the intelligence event retrieval capability"""
        start = time.time()
        try:
            res = requests.get(f"{self.base_url}/events", timeout=10)
            latency = (time.time() - start) * 1000
            
            success = res.status_code == 200
            event_count = len(res.json()) if success else 0
            print(f"[{'PASSED' if success else 'FAILED'}] EVENT_STREAM // Latency: {latency:.2f}ms // Events: {event_count}")
            
            self.results.append({"test": "events", "success": success, "latency": latency})
            return success
        except Exception as e:
            print(f"[FAILED] EVENT_STREAM // Error: {e}")
            return False

    def run_stress_pulse(self, concurrency=8, duration=5):
        """Execute a short burst load test to verify scalability"""
        print(f"🔥 INITIATING STRESS_PULSE: {concurrency} workers // {duration}s...")
        
        stats = {"success": 0, "fail": 0, "latencies": []}
        stop_event = threading.Event()
        
        def worker():
            while not stop_event.is_set():
                start = time.time()
                try:
                    res = requests.get(f"{self.base_url}/health", timeout=2)
                    if res.status_code == 200:
                        stats["success"] += 1
                        stats["latencies"].append((time.time() - start) * 1000)
                    else:
                        stats["fail"] += 1
                except:
                    stats["fail"] += 1
        
        threads = [threading.Thread(target=worker) for _ in range(concurrency)]
        for t in threads: t.start()
        time.sleep(duration)
        stop_event.set()
        for t in threads: t.join()
        
        avg_lat = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0
        success_rate = (stats["success"] / (stats["success"] + stats["fail"])) * 100 if (stats["success"] + stats["fail"]) > 0 else 0
        
        print(f"📊 STRESS_PULSE COMPLETE // Success: {success_rate:.1f}% // Avg Latency: {avg_lat:.2f}ms")
        
        self.results.append({"test": "stress", "success": success_rate > 95, "rate": success_rate})
        return success_rate > 95

    def verify_full_stack(self):
        print("\n" + "="*50)
        print("OSIN SVP-1 API VERIFICATION SUITE")
        print("="*50)
        
        tests = [
            self.test_health,
            self.test_intelligence_stream,
            lambda: self.run_stress_pulse(concurrency=10, duration=5)
        ]
        
        all_passed = True
        for test in tests:
            if not test(): all_passed = False
            
        print("="*50)
        print(f"VERIFICATION RESULT: {'✅ PASS' if all_passed else '❌ FAIL'}")
        print("="*50 + "\n")
        return all_passed

if __name__ == "__main__":
    verifier = APIVerifier()
    success = verifier.verify_full_stack()
    exit(0 if success else 1)
