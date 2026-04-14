"""
OSIN Global Forecasting Engine
Predicts large-scale events and risk propagation across the synthetic civilization
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

class GlobalForecastingEngine:
    """Uses historic patterns to project future civilization risk states"""
    def __init__(self):
        # Models for different risk vectors
        self.risk_model = GradientBoostingRegressor(n_estimators=50)
        self.is_trained = False
        self.risk_thresholds = {"Elevated": 0.4, "High": 0.7, "Extreme": 0.9}

    async def train_baseline(self, historical_data: List[Dict]):
        """Trains the regressor on synthetic history to establish standard risk behavior"""
        if not historical_data: return
        X = []
        y = []
        for d in historical_data:
            # Features: [hour, day_of_week, prev_stability, activity]
            X.append([datetime.fromisoformat(d['timestamp']).hour, 
                      datetime.fromisoformat(d['timestamp']).weekday(),
                      d.get('stability', 0.8),
                      d.get('activity', 0.5)])
            y.append(d.get('next_risk', 0.2))
        
        self.risk_model.fit(X, y)
        self.is_trained = True

    async def generate_forecast(self, current_state: Dict) -> Dict:
        """Projects the civilization state into a 24-hour look-ahead risk forecast"""
        if not self.is_trained: return {"status": "Warming up", "risk_score": 0.2, "level": "Stability"}
        
        now = datetime.now()
        features = [[now.hour, now.weekday(), current_state.get('stability', 0.85), 0.5]]
        prediction = self.risk_model.predict(features)[0]
        
        level = "Stable"
        for k, v in sorted(self.risk_thresholds.items(), key=lambda x: x[1], reverse=True):
            if prediction >= v:
                level = k
                break
                
        return {
            "forecast_timestamp": datetime.now().isoformat(),
            "predicted_risk": float(prediction),
            "threat_level": level,
            "confidence": 0.82
        }
