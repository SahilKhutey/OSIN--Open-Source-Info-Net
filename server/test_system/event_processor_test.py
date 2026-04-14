import json
import time
import threading
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer

class EventProcessorTester:
    """
    SVP-1 Integrated Pipeline Tester.
    Injects synthetic intelligence events and verifies end-to-end propagation 
    through v9/v10 processors to the final alert stream.
    """
    def __init__(self, bootstrap_servers='kafka:29092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        self.consumer = KafkaConsumer(
            "osin.alerts.high_priority",
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='svp1-tester-group'
        )

    def inject_synthetic_event(self, source_type="social"):
        """Inject an event into the start of the processing pipeline"""
        test_id = f"SVP1_TST_{int(time.time())}"
        topic = f"osin.raw.{source_type}"
        
        payload = {
            "id": test_id,
            "type": "VERIFICATION_PROBE",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "text": "SVP-1 Diagnostic: Intelligence pipeline verification in progress.",
                "coordinates": [40.7128, -74.0060]
            },
            "metadata": {
                "test": True,
                "svp_version": "1.0.0"
            }
        }
        
        print(f"🚀 INJECTING PROBE [{test_id}] -> {topic}")
        self.producer.send(topic, payload)
        self.producer.flush()
        return test_id

    def verify_propagation(self, target_id: str, timeout: int = 45):
        """Monitor alert stream for processed synthetic events"""
        print(f"👂 MONITORING ALERTS FOR PROBE [{target_id}] (T-MAX: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = self.consumer.poll(timeout_ms=1000)
            for tp, records in messages.items():
                for record in records:
                    alert = record.value
                    if alert.get('id') == target_id or alert.get('metadata', {}).get('test'):
                        print(f"✅ PROBE DETECTED IN ALERTS // Latency: {time.time() - start_time:.2f}s")
                        return True
        
        print(f"❌ PROBE TIMED OUT: Pipeline latency exceeds {timeout}s or logic failure.")
        return False

    def run_suite(self):
        print("\n" + "="*50)
        print("OSIN SVP-1 INTEGRATION TEST SUITE")
        print("="*50)
        
        results = []
        
        # Test 1: Social Pipe
        tid1 = self.inject_synthetic_event("social")
        results.append(self.verify_propagation(tid1))
        
        # Test 2: Satellite Pipe
        tid2 = self.inject_synthetic_event("satellite")
        results.append(self.verify_propagation(tid2))
        
        success_count = sum(1 for r in results if r)
        total = len(results)
        
        print("\n" + "="*50)
        print(f"📊 SUITE SUMMARY: {success_count}/{total} PASS")
        print("="*50)
        return success_count == total

if __name__ == "__main__":
    tester = EventProcessorTester()
    time.sleep(5) # Allow consumer groups to balance
    success = tester.run_suite()
    exit(0 if success else 1)
