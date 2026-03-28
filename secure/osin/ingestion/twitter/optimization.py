from typing import Dict, List, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from statistics import mean, median
import logging

class TwitterPerformanceOptimizer:
    """Optimize Twitter ingestion performance"""
    
    def __init__(self):
        self.metrics = {
            'tweets_processed': 0,
            'processing_times': [],
            'error_rates': [],
            'throughput': 0
        }
        self.optimization_strategies = {
            'batch_processing': True,
            'connection_pooling': True,
            'compression': True,
            'adaptive_rate_limiting': True
        }
    
    async def optimize_ingestion(self, ingestor) -> Dict[str, Any]:
        """Continuously optimize ingestion performance"""
        
        while True:
            try:
                # Monitor current performance
                current_metrics = await self._collect_metrics(ingestor)
                
                # Adjust strategies based on performance
                optimizations = await self._adjust_strategies(current_metrics)
                
                # Apply optimizations
                await self._apply_optimizations(ingestor, optimizations)
                
                # Log performance
                self._log_performance(current_metrics, optimizations)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logging.error(f"Optimization error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_metrics(self, ingestor) -> Dict[str, Any]:
        """Collect metrics from the ingestor - Simplified implementation"""
        # In a real implementation, this would query the ingestor's internal state
        # or a monitoring service.
        return {
            'throughput': getattr(ingestor, 'current_throughput', 500),
            'error_rate': getattr(ingestor, 'current_error_rate', 0.05),
            'avg_processing_time': mean(self.metrics['processing_times']) if self.metrics['processing_times'] else 0.5
        }

    async def _apply_optimizations(self, ingestor, optimizations: Dict[str, Any]):
        """Apply optimization strategies to the ingestor"""
        if 'batch_size' in optimizations:
            ingestor.config.max_tweets_per_query = optimizations['batch_size']
        
        if 'rate_limit_reduction' in optimizations:
            ingestor.config.requests_per_hour = int(ingestor.config.requests_per_hour * optimizations['rate_limit_reduction'])
        
        if 'rate_limit_increase' in optimizations:
            ingestor.config.requests_per_hour = int(ingestor.config.requests_per_hour * optimizations['rate_limit_increase'])

    def _log_performance(self, metrics: Dict, optimizations: Dict):
        """Log performance metrics and optimizations"""
        logging.info(f"Ingestion Metrics: {metrics}")
        logging.info(f"Applied Optimizations: {optimizations}")

    async def _adjust_strategies(self, metrics: Dict) -> Dict[str, Any]:
        """Adjust optimization strategies based on metrics"""
        
        strategies = {}
        
        # Batch processing optimization
        if metrics.get('throughput', 0) < 1000:  # tweets/minute
            strategies['batch_size'] = min(metrics.get('throughput', 100) * 2, 10000)
        else:
            strategies['batch_size'] = 2000  # Optimal batch size
        
        # Rate limiting adjustment
        error_rate = metrics.get('error_rate', 0)
        if error_rate > 0.1:  # High error rate
            strategies['rate_limit_reduction'] = 0.8  # Reduce by 20%
        elif error_rate < 0.01:  # Low error rate
            strategies['rate_limit_increase'] = 1.2  # Increase by 20%
        
        # Connection pooling
        avg_processing_time = metrics.get('avg_processing_time', 0)
        if avg_processing_time > 1.0:  # Slow processing
            strategies['increase_connections'] = True
        
        return strategies

class AdaptiveSearchStrategy:
    """Adapt search strategies based on signal quality"""
    
    def __init__(self):
        self.query_performance = {}
        self.topic_discovery = TopicDiscovery()
    
    async def optimize_search_queries(self, current_queries: List[str]) -> List[str]:
        """Optimize search queries based on performance"""
        
        optimized_queries = current_queries.copy()
        
        # Remove poorly performing queries
        for query in current_queries:
            performance = self.query_performance.get(query, {'score': 0})
            if performance['score'] < 0.3:  # Low performance threshold
                optimized_queries.remove(query)
        
        # Add new discovered topics
        new_topics = await self.topic_discovery.find_trending_topics()
        optimized_queries.extend(new_topics[:5])  # Add top 5 new topics
        
        # Ensure diversity
        optimized_queries = self._ensure_query_diversity(optimized_queries)
        
        return optimized_queries[-50:]  # Keep recent 50 queries
    
    def _ensure_query_diversity(self, queries: List[str]) -> List[str]:
        """Ensure query diversity across topics"""
        
        # Categorize queries
        categories = {
            'breaking_news': ['breaking news', 'emergency', 'crisis'],
            'politics': ['election', 'protest', 'government'],
            'disasters': ['earthquake', 'fire', 'flood', 'storm'],
            'technology': ['cyber attack', 'data breach', 'tech news']
        }
        
        # Ensure representation from each category
        diversified_queries = []
        for category, keywords in categories.items():
            category_queries = [q for q in queries if any(kw in q for kw in keywords)]
            if category_queries:
                # Find best in category or first one
                best_query = max(category_queries, 
                    key=lambda q: self.query_performance.get(q, {'score': 0})['score'])
                diversified_queries.append(best_query)
        
        # Add remaining high-performing queries
        remaining_queries = [q for q in queries if q not in diversified_queries]
        remaining_queries.sort(key=lambda q: self.query_performance.get(q, {'score': 0})['score'], 
                              reverse=True)
        
        diversified_queries.extend(remaining_queries[:20])  # Top 20 remaining
        
        return diversified_queries

class TopicDiscovery:
    """Discover new trending topics"""
    
    async def find_trending_topics(self) -> List[str]:
        """Discover currently trending topics"""
        
        # This would integrate with:
        # - Twitter trending API
        # - Google Trends
        # - News aggregators
        # - Social media heat maps
        
        trending_topics = []
        
        try:
            # Simulate topic discovery
            # In production, this would call various APIs
            simulated_topics = [
                "climate protest", "tech conference", "sports event",
                "economic news", "health update", "entertainment news"
            ]
            
            # Filter based on relevance
            relevant_topics = await self._filter_relevant_topics(simulated_topics)
            trending_topics.extend(relevant_topics)
            
        except Exception as e:
            logging.error(f"Topic discovery error: {e}")
        
        return trending_topics
    
    async def _filter_relevant_topics(self, topics: List[str]) -> List[str]:
        """Filter topics for relevance to OSINT"""
        
        relevant_keywords = [
            'protest', 'election', 'summit', 'crisis', 'emergency',
            'attack', 'disaster', 'breakthrough', 'scandal', 'investigation'
        ]
        
        return [topic for topic in topics 
                if any(kw in topic.lower() for kw in relevant_keywords)]

if __name__ == "__main__":
    # Example usage / test
    optimizer = TwitterPerformanceOptimizer()
    print("TwitterPerformanceOptimizer initialized")
