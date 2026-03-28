import praw
from kafka import KafkaProducer
import json
import asyncio
from datetime import datetime
import logging
from typing import List, Dict, Any
from architecture import IngestionConfig
from shared_components import DeduplicationEngine, ContentCleaner
from monitoring import monitor
from flask import Flask, jsonify
import time
import threading

class RedditIngestionEngine:
    """Scalable Reddit data ingestion using PRAW"""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.reddit_clients = self._initialize_reddit_clients()
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.subreddit_monitor = SubredditMonitor()
        self.deduplicator = DeduplicationEngine()
        self.cleaner = ContentCleaner()
    
    def _initialize_reddit_clients(self) -> List[praw.Reddit]:
        """Initialize multiple Reddit clients for load balancing"""
        
        clients = []
        
        # Multiple client configurations for rate limiting
        # NOTE: In production, these should be loaded from secure environment variables or a vault
        client_configs = [
            {
                'client_id': 'CLIENT_ID_1',
                'client_secret': 'CLIENT_SECRET_1',
                'user_agent': 'osin_reddit_ingestor_v1'
            },
            {
                'client_id': 'CLIENT_ID_2', 
                'client_secret': 'CLIENT_SECRET_2',
                'user_agent': 'osin_reddit_ingestor_v2'
            }
        ]
        
        for cfg in client_configs:
            client = praw.Reddit(
                client_id=cfg['client_id'],
                client_secret=cfg['client_secret'],
                user_agent=cfg['user_agent']
            )
            clients.append(client)
        
        return clients
    
    def get_monitored_subreddits(self) -> List[str]:
        """Get list of subreddits to monitor"""
        
        return [
            # News and current events
            'worldnews', 'news', 'politics', 'economics',
            # Regional subreddits
            'europe', 'asia', 'canada', 'australia',
            # Specific topics
            'technology', 'science', 'environment', 'climate',
            'cybersecurity', 'programming', 'futurology',
            # Breaking news
            'breakingnews', 'crisis', 'emergency'
        ]
    
    async def stream_subreddits(self):
        """Stream from multiple subreddits"""
        
        subreddits = self.get_monitored_subreddits()
        
        # Create tasks for each subreddit
        tasks = []
        for subreddit_name in subreddits:
            task = asyncio.create_task(
                self._monitor_subreddit(subreddit_name)
            )
            tasks.append(task)
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)
    
    async def _monitor_subreddit(self, subreddit_name: str):
        """Monitor a specific subreddit"""
        
        client = self.reddit_clients[0]  # Round-robin clients logic could be added here
        
        try:
            subreddit = client.subreddit(subreddit_name)
            
            # Stream new submissions
            for submission in subreddit.stream.submissions(skip_existing=True):
                if submission is None:
                    continue
                
                start_time = time.time()
                processed_data = self._process_submission(submission, subreddit_name)
                processed_data = self.cleaner.clean_content(processed_data)
                
                if not self.deduplicator.is_duplicate(processed_data):
                    self.producer.send("raw.reddit.posts", processed_data)
                    
                    # Record activity for health monitor and metrics
                    health_monitor.record_activity()
                    latency = time.time() - start_time
                    monitor.record_request('reddit', 'success', latency)
                    monitor.record_content_volume('reddit', 'submission', 1)
                
                # Also stream comments for high-engagement posts
                if submission.score > 100:
                    await self._stream_comments(submission)
        
        except Exception as e:
            logging.error(f"Error monitoring subreddit {subreddit_name}: {e}")
            await asyncio.sleep(30)
    
    async def _stream_comments(self, submission):
        """Stream comments for a submission"""
        
        submission.comments.replace_more(limit=0)  # Remove MoreComments objects
        
        for comment in submission.comments.list():
            if comment is None:
                continue
            
            comment_data = self._process_comment(comment, submission.id)
            comment_data = self.cleaner.clean_content(comment_data)
            
            if not self.deduplicator.is_duplicate(comment_data):
                self.producer.send("raw.reddit.comments", comment_data)
                health_monitor.record_activity()
    
    def _process_submission(self, submission, subreddit_name: str) -> Dict[str, Any]:
        """Process Reddit submission into standardized format"""
        
        return {
            "platform": "reddit",
            "type": "submission",
            "id": submission.id,
            "title": submission.title,
            "text": submission.selftext,
            "author": str(submission.author) if submission.author else "[deleted]",
            "subreddit": subreddit_name,
            "engagement": {
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "total_awards": submission.total_awards_received
            },
            "metadata": {
                "created_utc": submission.created_utc,
                "url": submission.url,
                "permalink": submission.permalink,
                "nsfw": submission.over_18,
                "spoiler": submission.spoiler,
                "locked": submission.locked,
                "stickied": submission.stickied
            },
            "content_metadata": {
                "domain": submission.domain,
                "is_self": submission.is_self,
                "is_video": submission.is_video,
                "media_only": submission.media_only
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }
    
    def _process_comment(self, comment, submission_id: str) -> Dict[str, Any]:
        """Process Reddit comment"""
        
        return {
            "platform": "reddit",
            "type": "comment",
            "id": comment.id,
            "text": comment.body,
            "author": str(comment.author) if comment.author else "[deleted]",
            "submission_id": submission_id,
            "engagement": {
                "score": comment.score,
                "total_awards": comment.total_awards_received,
                "controversiality": comment.controversiality
            },
            "metadata": {
                "created_utc": comment.created_utc,
                "permalink": comment.permalink,
                "is_submitter": comment.is_submitter,
                "stickied": comment.stickied
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat()
            }
        }

class SubredditMonitor:
    """Monitor subreddit activity and adjust collection strategy"""
    
    def __init__(self):
        self.subreddit_activity = {}
        self.optimization_threshold = 100  # posts per hour
    
    async def optimize_monitoring(self, subreddit_name: str, activity_level: int):
        """Optimize monitoring based on activity level"""
        
        self.subreddit_activity[subreddit_name] = activity_level
        
        if activity_level > self.optimization_threshold:
            # High activity - use sampling
            return "sampling"
        else:
            # Normal activity - stream everything
            return "full_stream"

# Health monitoring setup
app = Flask(__name__)

class HealthMonitor:
    def __init__(self):
        self.last_activity = datetime.utcnow()
        self.processed_count = 0
        self.lock = threading.Lock()
        
    def record_activity(self):
        with self.lock:
            self.last_activity = datetime.utcnow()
            self.processed_count += 1

health_monitor = HealthMonitor()

@app.route('/health')
def health_check():
    with health_monitor.lock:
        last_act = health_monitor.last_activity
        count = health_monitor.processed_count
        
    time_since_last_activity = (datetime.utcnow() - last_act).total_seconds()
    
    if time_since_last_activity > 300:  # 5 minutes
        return jsonify({"status": "unhealthy", "reason": "No recent activity"}), 503
    
    return jsonify({
        "status": "healthy",
        "last_activity": last_act.isoformat(),
        "processed_count": count
    }), 200

def run_health_server():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    monitor.start_metrics_server(port=8000)
    # Start health server in background thread
    health_thread = threading.Thread(target=run_health_server)
    health_thread.daemon = True
    health_thread.start()
    
    # Initialize and start Reddit ingestion
    config = IngestionConfig()
    engine = RedditIngestionEngine(config)
    
    # Start streaming
    asyncio.run(engine.stream_subreddits())
