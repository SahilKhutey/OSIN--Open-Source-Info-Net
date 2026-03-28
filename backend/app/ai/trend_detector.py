from typing import List, Dict
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sentence_transformers import SentenceTransformer
from app.db.models import Signal
from datetime import datetime, timedelta

class Trend:
    def __init__(self, cluster_id: int, signals: List[Signal], velocity: float, platforms: set, credibility_score: float):
        self.cluster_id = cluster_id
        self.signals = signals
        self.velocity = velocity
        self.platforms = platforms
        self.credibility_score = credibility_score

class TrendDetector:
    def __init__(self):
        self.clustering_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.anomaly_detector = IsolationForest()
        self.eps = 0.3
        self.min_samples = 2

    def detect_trends(self, signals: List[Signal], window_hours: int = 1) -> List[Trend]:
        if not signals:
            return []

        # Step 1: Cluster similar events
        texts = [s.content for s in signals]
        embeddings = self.clustering_model.encode(texts)
        
        clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='cosine').fit(embeddings)
        labels = clustering.labels_

        trends = []
        unique_labels = set(labels)
        
        for label in unique_labels:
            if label == -1: continue  # Noise
            
            cluster_signals = [signals[i] for i, l in enumerate(labels) if l == label]
            
            velocity = self._calculate_velocity(cluster_signals, window_hours)
            platforms = set(s.source_type for s in cluster_signals)
            cross_platform_score = len(platforms)
            
            # Threshold check: velocity and cross-platform > 2 (from blueprint)
            # Adjusting threshold for prototype: cross_platform >= 1 for visibility
            if velocity > 0.1 and cross_platform_score >= 1:
                avg_credibility = 0.8  # Placeholder for aggregate credibility
                
                trend = Trend(
                    cluster_id=int(label),
                    signals=cluster_signals,
                    velocity=velocity,
                    platforms=platforms,
                    credibility_score=avg_credibility
                )
                trends.append(trend)

        return sorted(trends, key=lambda x: x.velocity * x.credibility_score, reverse=True)

    def _calculate_velocity(self, signals: List[Signal], window_hours: int) -> float:
        """
        Velocity defined as signal count over time window.
        """
        if not signals: return 0.0
        return len(signals) / window_hours

    def _calculate_cross_platform_score(self, signals: List[Signal]) -> int:
        return len(set(s.source_type for s in signals))

trend_detector = TrendDetector()
