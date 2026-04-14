"""
Threat Prediction Engine - OSIN ML Forecasting Core
Machine learning for intelligence confidence and threat forecasting
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import logging

class ThreatPredictor:
    def __init__(self, entity_store):
        self.entity_store = entity_store
        self.models: Dict[str, RandomForestRegressor] = {}
        self.scaler = StandardScaler()
        self.prediction_history: List[Dict] = []
        self.logger = logging.getLogger("osin-threat-predictor")
    
    def train_models(self):
        """Train Random Forest models on historical threat_signal entities"""
        self.logger.info("Retraining threat forecasting models")
        
        # 1. Gather historical data
        data = self._gather_historical_data()
        if len(data) < 20:
            self.logger.warning("Insufficient data for training")
            return
            
        # 2. Train for 24h horizon
        X = np.array([[d['timestamp'].timestamp(), d['confidence']] for d in data[:-1]])
        y = np.array([d['confidence'] for d in data[1:]])
        
        model = RandomForestRegressor(n_estimators=100)
        model.fit(X, y)
        self.models['24h'] = model
        self.logger.info("Threat forecasting model (24h) trained successfully")
    
    def predict_future_intensity(self, horizon="24h") -> Dict[str, Any]:
        """Predict prospective intelligence confidence/threat level"""
        if horizon not in self.models:
            return {"error": "Model not trained"}
            
        # Use latest data point as feature
        latest = self._gather_historical_data()
        if not latest: return {"error": "No data"}
        
        last = latest[-1]
        X_next = np.array([[datetime.now().timestamp(), last['confidence']]])
        
        prediction = self.models[horizon].predict(X_next)[0]
        result = {
            "prediction": float(prediction),
            "threat_level": "CRITICAL" if prediction > 0.8 else "HIGH" if prediction > 0.6 else "LOW",
            "timestamp": datetime.now().isoformat()
        }
        self.prediction_history.append(result)
        return result

    def _gather_historical_data(self) -> List[Dict]:
        entities = [
            e for e in self.entity_store.entities.values() 
            if e.get('type') == 'threat_signal'
        ]
        data = []
        for e in entities:
            try:
                ts = datetime.fromisoformat(e['properties'].get('processed_at', datetime.now().isoformat()))
                data.append({'timestamp': ts, 'confidence': e['confidence']})
            except: continue
        return sorted(data, key=lambda x: x['timestamp'])
