import os
import json
import logging
import asyncio
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from sklearn.ensemble import IsolationForest
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OSIN-AnomalyDetection")

# Metrics
ANOMALIES_DETECTED = Counter('anomalies_detected_total', 'Total anomalies detected', ['service', 'type'])
PREDICTION_LATENCY = Histogram('anomaly_prediction_latency_seconds', 'Anomaly prediction latency')
FEATURE_IMPORTANCE = Gauge('anomaly_feature_importance', 'Feature importance scores (proxy)', ['feature'])
MODEL_READY = Gauge('anomaly_model_ready', 'Model readiness status (1=ready)')

class EventData(BaseModel):
    event: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class AnomalyDetector:
    def __init__(self, contamination=0.01, min_training_samples=100):
        self.contamination = contamination
        self.min_samples = min_training_samples
        self.model = IsolationForest(
            contamination=contamination, 
            random_state=42,
            n_estimators=100
        )
        self.data_buffer = []
        self.feature_names = [
            'latency_ms', 'message_size', 'processing_time', 
            'confidence', 'priority_score'
        ]
        self.is_fitted = False

    def _calculate_priority_score(self, priority: Optional[str]) -> float:
        priority_map = {'critical': 1.0, 'high': 0.75, 'medium': 0.5, 'low': 0.25}
        return priority_map.get(str(priority).lower(), 0.25)

    def extract_features(self, event: Dict[str, Any]) -> List[float]:
        try:
            return [
                float(event.get('latency_ms', 0) or 0),
                float(len(json.dumps(event).encode('utf-8'))),
                float(event.get('processing_time', 0) or 0),
                float(event.get('confidence', 0.5) or 0.5),
                self._calculate_priority_score(event.get('priority'))
            ]
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return [0.0] * len(self.feature_names)

    def update_model(self, event: Dict[str, Any]):
        features = self.extract_features(event)
        self.data_buffer.append(features)
        
        # Periodic Retraining
        if len(self.data_buffer) >= self.min_samples:
            X = np.array(self.data_buffer)
            self.model.fit(X)
            self.is_fitted = True
            MODEL_READY.set(1)
            
            # Note: IsolationForest doesn't have direct feature_importances_, 
            # we simulate it via variance of features in original data for now
            variances = np.var(X, axis=0)
            total_var = np.sum(variances)
            for i, name in enumerate(self.feature_names):
                FEATURE_IMPORTANCE.labels(feature=name).set(variances[i]/total_var if total_var > 0 else 0)
            
            # Keep rolling window
            self.data_buffer = self.data_buffer[-1000:]
            logger.info(f"Model retrained with {len(X)} samples.")

    def predict(self, event: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_fitted:
            return {"anomalous": False, "score": 0.0, "reason": "model_not_ready"}

        start_time = time.time()
        features = np.array([self.extract_features(event)])
        
        # IsolationForest: predict returns 1 for inlier, -1 for outlier
        prediction = self.model.predict(features)
        score = self.model.decision_function(features)[0]
        
        latency = time.time() - start_time
        PREDICTION_LATENCY.observe(latency)
        
        is_anomaly = prediction[0] == -1
        
        if is_anomaly:
            ANOMALIES_DETECTED.labels(
                service=event.get('service', 'unknown'),
                type=event.get('processed_type', 'event')
            ).inc()
            logger.warning(f"ANOMALY DETECTED in {event.get('id', 'unknown')} with score {score}")

        return {
            "anomalous": is_anomaly,
            "score": float(score),
            "timestamp": datetime.now().isoformat()
        }

# FastAPI App
app = FastAPI(title="OSIN v12 Anomaly Detection")
detector = AnomalyDetector()

@app.post("/detect")
async def detect(data: EventData):
    detector.update_model(data.event)
    result = detector.predict(data.event)
    return result

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "is_fitted": detector.is_fitted,
        "buffer_size": len(detector.data_buffer)
    }

if __name__ == "__main__":
    import uvicorn
    import time
    # Start Prometheus metrics on 8005
    start_http_server(8005)
    uvicorn.run(app, host="0.0.0.0", port=8004)
