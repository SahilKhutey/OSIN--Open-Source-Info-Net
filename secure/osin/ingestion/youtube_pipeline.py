from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from kafka import KafkaProducer
import json
import asyncio
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from architecture import IngestionConfig
from shared_components import DeduplicationEngine, ContentCleaner
from monitoring import monitor
import time

class YouTubeIngestionEngine:
    """YouTube video and comment intelligence collection"""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.youtube_services = self._initialize_youtube_services()
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.quota_manager = YouTubeQuotaManager()
        self.deduplicator = DeduplicationEngine()
        self.cleaner = ContentCleaner()
    
    def _initialize_youtube_services(self) -> List[Any]:
        """Initialize multiple YouTube API services"""
        
        services = []
        # NOTE: Keys should be managed via environment variables in production
        api_keys = [
            "API_KEY_1", "API_KEY_2", "API_KEY_3"  # Rotate keys
        ]
        
        for api_key in api_keys:
            try:
                service = build('youtube', 'v3', developerKey=api_key)
                services.append(service)
            except Exception as e:
                logging.error(f"Failed to initialize YouTube service: {e}")
        
        return services
    
    async def collect_trending_videos(self):
        """Collect trending videos from multiple regions"""
        
        regions = ["US", "GB", "DE", "FR", "JP", "IN", "BR", "RU", "CN"]
        
        for region in regions:
            for service in self.youtube_services:
                try:
                    if not self.quota_manager.can_make_request('videos.list'):
                        continue
                        
                    start_time = time.time()
                    videos = await self._fetch_trending_videos(service, region)
                    self.quota_manager.record_request('videos.list')
                    
                    for video in videos:
                        video = self.cleaner.clean_content(video)
                        if not self.deduplicator.is_duplicate(video):
                            self.producer.send("raw.youtube.videos", video)
                            latency = time.time() - start_time
                            monitor.record_request('youtube', 'success', latency)
                            monitor.record_content_volume('youtube', 'video', 1)
                    
                    # Also fetch comments for high-engagement videos
                    top_videos = [v for v in videos if v['engagement']['view_count'] > 10000]
                    for video in top_videos:
                        if self.quota_manager.can_make_request('commentThreads.list'):
                            await self._fetch_video_comments(service, video['id'])
                            self.quota_manager.record_request('commentThreads.list')
                    
                    await asyncio.sleep(1)  # Rate limiting
                    
                except HttpError as e:
                    if e.resp.status == 403:  # Quota exceeded
                        logging.warning(f"YouTube quota exceeded for region {region}")
                        continue
                    else:
                        logging.error(f"YouTube API error: {e}")
    
    async def _fetch_trending_videos(self, service, region_code: str) -> List[Dict[str, Any]]:
        """Fetch trending videos for a region"""
        
        # In a real environment, .execute() is blocking, but we use it here as per user request
        request = service.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=50
        )
        
        response = request.execute()
        videos = []
        
        for item in response.get('items', []):
            video_data = self._process_video(item, region_code)
            videos.append(video_data)
        
        return videos
    
    # ... (other methods as provided in the snippet)
    async def _fetch_video_comments(self, service, video_id: str):
        """Fetch comments for a video"""
        
        try:
            request = service.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                order="relevance"
            )
            
            response = request.execute()
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comment_data = self._process_comment(comment, video_id)
                self.producer.send("raw.youtube.comments", comment_data)
        
        except HttpError as e:
            if "commentsDisabled" in str(e):
                logging.debug(f"Comments disabled for video {video_id}")
            else:
                logging.error(f"Error fetching comments: {e}")

    def _process_video(self, video_item: Dict, region_code: str) -> Dict[str, Any]:
        """Process YouTube video into standardized format"""
        
        snippet = video_item['snippet']
        statistics = video_item.get('statistics', {})
        content_details = video_item.get('contentDetails', {})
        
        return {
            "platform": "youtube",
            "type": "video",
            "id": video_item['id'],
            "title": snippet['title'],
            "description": snippet['description'],
            "channel": {
                "id": snippet['channelId'],
                "title": snippet['channelTitle']
            },
            "engagement": {
                "view_count": int(statistics.get('viewCount', 0)),
                "like_count": int(statistics.get('likeCount', 0)),
                "comment_count": int(statistics.get('commentCount', 0))
            },
            "metadata": {
                "published_at": snippet['publishedAt'],
                "region": region_code,
                "duration": content_details.get('duration', ''),
                "dimension": content_details.get('dimension', ''),
                "definition": content_details.get('definition', ''),
                "caption": content_details.get('caption', ''),
                "licensed_content": content_details.get('licensedContent', False)
            },
            "content_analysis": {
                "tags": snippet.get('tags', []),
                "category_id": snippet['categoryId'],
                "live_broadcast_content": snippet.get('liveBroadcastContent', 'none')
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }
    
    def _process_comment(self, comment: Dict, video_id: str) -> Dict[str, Any]:
        """Process YouTube comment"""
        
        return {
            "platform": "youtube",
            "type": "comment",
            "id": comment['id'],
            "text": comment['textDisplay'],
            "author": {
                "id": comment['authorChannelId']['value'] if 'authorChannelId' in comment else None,
                "name": comment['authorDisplayName']
            },
            "video_id": video_id,
            "engagement": {
                "like_count": int(comment.get('likeCount', 0)),
                "reply_count": int(comment.get('replyCount', 0))
            },
            "metadata": {
                "published_at": comment['publishedAt'],
                "updated_at": comment['updatedAt'],
                "moderation_status": comment.get('moderationStatus', 'published')
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat()
            }
        }
    
    async def search_keywords(self, keywords: List[str]):
        """Search for videos by keywords"""
        
        for keyword in keywords:
            for service in self.youtube_services:
                try:
                    if not self.quota_manager.can_make_request('search.list'):
                        continue
                        
                    request = service.search().list(
                        part="snippet",
                        q=keyword,
                        type="video",
                        maxResults=50,
                        order="date",  # Most recent first
                        publishedAfter=(datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
                    )
                    
                    response = request.execute()
                    self.quota_manager.record_request('search.list')
                    
                    for item in response.get('items', []):
                        if not self.quota_manager.can_make_request('videos.list'):
                            continue
                            
                        # Get full video details
                        video_request = service.videos().list(
                            part="snippet,statistics",
                            id=item['id']['videoId']
                        )
                        video_response = video_request.execute()
                        self.quota_manager.record_request('videos.list')
                        
                        if video_response.get('items'):
                            video_data = self._process_video(
                                video_response['items'][0], 
                                "search"
                            )
                            video_data['search_keyword'] = keyword
                            self.producer.send("raw.youtube.videos", video_data)
                    
                    await asyncio.sleep(1)  # Rate limiting
                    
                except HttpError as e:
                    logging.error(f"YouTube search error for '{keyword}': {e}")
                    continue

# YouTube quota management
class YouTubeQuotaManager:
    """Manage YouTube API quota usage"""
    
    def __init__(self):
        self.quota_usage = {}
        self.quota_limits = {
            'videos.list': 1,
            'search.list': 100,
            'commentThreads.list': 1
        }
    
    def can_make_request(self, method: str) -> bool:
        """Check if we can make a request without exceeding quota"""
        
        today = datetime.utcnow().date()
        daily_usage = self.quota_usage.get(today, {})
        method_usage = daily_usage.get(method, 0)
        
        return method_usage < self.quota_limits.get(method, 10000)
    
    def record_request(self, method: str):
        """Record a API request"""
        
        today = datetime.utcnow().date()
        
        if today not in self.quota_usage:
            self.quota_usage[today] = {}
        
        self.quota_usage[today][method] = self.quota_usage[today].get(method, 0) + 1

if __name__ == "__main__":
    monitor.start_metrics_server(port=8000)
    config = IngestionConfig()
    engine = YouTubeIngestionEngine(config)
    
    # Start collection
    asyncio.run(engine.collect_trending_videos())
