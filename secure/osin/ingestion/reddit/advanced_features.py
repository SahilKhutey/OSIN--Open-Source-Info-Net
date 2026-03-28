from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import statistics

class SubredditIntelligence:
    """Advanced subreddit monitoring and intelligence"""
    
    def __init__(self):
        self.subreddit_metrics = {}
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
    
    async def analyze_subreddit_health(self, subreddit: str, recent_data: List[Dict]) -> Dict[str, Any]:
        """Analyze subreddit health and activity patterns"""
        
        analysis = {
            'subreddit': subreddit,
            'timestamp': datetime.utcnow().isoformat(),
            'activity_metrics': await self._calculate_activity_metrics(recent_data),
            'content_quality': await self._assess_content_quality(recent_data),
            'trend_analysis': await self._analyze_trends(recent_data),
            'anomaly_detection': await self._detect_anomalies(recent_data)
        }
        
        return analysis
    
    async def _calculate_activity_metrics(self, data: List[Dict]) -> Dict[str, float]:
        """Calculate subreddit activity metrics"""
        
        if not data:
            return {}
        
        submission_counts = len([d for d in data if d.get('type') == 'submission'])
        comment_counts = len([d for d in data if d.get('type') == 'comment'])
        
        engagement_scores = [
            d.get('engagement', {}).get('score', 0) 
            for d in data 
            if d.get('engagement')
        ]
        
        return {
            'submissions_per_hour': submission_counts / 24,  # Assuming 24h data
            'comments_per_hour': comment_counts / 24,
            'avg_engagement_score': statistics.mean(engagement_scores) if engagement_scores else 0,
            'active_users': len(set(d.get('author') for d in data if d.get('author'))),
            'content_diversity': await self._calculate_content_diversity(data)
        }
    
    async def _calculate_content_diversity(self, data: List[Dict]) -> float:
        """Calculate content diversity score"""
        
        if not data:
            return 0.0
        
        # Analyze title/text diversity using basic metrics
        titles = [d.get('title', '') for d in data if d.get('title')]
        
        if not titles:
            return 0.0
        
        # Simple diversity metric (could be enhanced with NLP)
        unique_words = len(set(' '.join(titles).lower().split()))
        total_words = len(' '.join(titles).split())
        
        return unique_words / total_words if total_words > 0 else 0.0

    async def _assess_content_quality(self, data: List[Dict]) -> Dict[str, Any]:
        """Simple quality assessment based on engagement metrics"""
        if not data:
            return {}
        scores = [d.get('engagement', {}).get('score', 0) for d in data]
        return {
            'median_engagement': statistics.median(scores) if scores else 0,
            'high_quality_ratio': len([s for s in scores if s > 100]) / len(scores) if scores else 0
        }

    async def _analyze_trends(self, data: List[Dict]) -> List[Dict]:
        """Calls the trend analyzer"""
        # In a real scenario, would organize by subreddit first
        return await self.trend_analyzer.detect_emerging_topics({'all': data})

    async def _detect_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Calls the anomaly detector"""
        return await self.anomaly_detector.detect_anomalies(data)

class TrendAnalyzer:
    """Analyze trends across Reddit data"""
    
    async def detect_emerging_topics(self, subreddit_data: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect emerging topics across subreddits"""
        
        emerging_topics = []
        
        # Analyze word frequency trends
        word_trends = await self._analyze_word_frequency_trends(subreddit_data)
        
        # Detect spikes in specific topics
        topic_spikes = await self._detect_topic_spikes(word_trends)
        
        # Cross-subreddit correlation
        correlated_topics = await self._find_correlated_topics(subreddit_data)
        
        emerging_topics.extend(topic_spikes)
        emerging_topics.extend(correlated_topics)
        
        return emerging_topics
    
    async def _analyze_word_frequency_trends(self, data: Dict[str, List[Dict]]) -> Dict[str, List[float]]:
        """Analyze word frequency trends over time"""
        
        # This would implement proper time-series analysis
        # For now, return simplified structure
        return {
            'breaking': [10, 15, 20, 25, 30],  # Increasing trend
            'crisis': [5, 8, 12, 9, 7],        # Fluctuating
            'protest': [2, 3, 15, 20, 18]       # Spike and sustain
        }

    async def _detect_topic_spikes(self, word_trends: Dict[str, List[float]]) -> List[Dict]:
        """Simple spike detection"""
        spikes = []
        for word, trend in word_trends.items():
            if len(trend) > 1 and trend[-1] > trend[-2] * 2:
                spikes.append({'topic': word, 'growth': trend[-1]/trend[-2]})
        return spikes

    async def _find_correlated_topics(self, data: Dict[str, List[Dict]]) -> List[Dict]:
        """Placeholder for cross-subreddit correlation"""
        return []

class AnomalyDetector:
    """Detect anomalies in Reddit activity"""
    
    async def detect_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Detect anomalous activity patterns"""
        
        anomalies = []
        
        # Volume anomalies
        volume_anomalies = await self._detect_volume_anomalies(data)
        anomalies.extend(volume_anomalies)
        
        # Engagement anomalies
        engagement_anomalies = await self._detect_engagement_anomalies(data)
        anomalies.extend(engagement_anomalies)
        
        # Temporal anomalies
        temporal_anomalies = await self._detect_temporal_anomalies(data)
        anomalies.extend(temporal_anomalies)
        
        return anomalies
    
    async def _detect_volume_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Detect volume anomalies using statistical methods"""
        
        if len(data) < 10:
            return []
        
        # Simple Z-score based anomaly detection
        volumes = [1] * len(data)  # Placeholder - would use actual volume metrics
        mean_volume = statistics.mean(volumes)
        stdev_volume = statistics.stdev(volumes) if len(volumes) > 1 else 0
        
        anomalies = []
        for i, volume in enumerate(volumes):
            if stdev_volume == 0: continue
            z_score = abs(volume - mean_volume) / stdev_volume
            
            if z_score > 3:  # 3 standard deviations
                anomalies.append({
                    'type': 'volume_anomaly',
                    'z_score': z_score,
                    'timestamp': data[i].get('metadata', {}).get('created_utc', ''),
                    'severity': 'high' if z_score > 5 else 'medium'
                })
        
        return anomalies

    async def _detect_engagement_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Placeholder for engagement anomaly detection"""
        return []
        
    async def _detect_temporal_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Placeholder for temporal anomaly detection"""
        return []
