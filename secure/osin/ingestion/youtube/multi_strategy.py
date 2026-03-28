from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import yt_dlp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from kafka import KafkaProducer
import json
import logging
import hashlib
import os
import time
from .monitoring import YouTubeMetricsCollector

@dataclass
class YouTubeConfig:
    """YouTube ingestion configuration"""
    # yt-dlp configuration
    yt_dlp_enabled: bool = True
    download_formats: List[str] = field(default_factory=lambda: [
        'best[height<=720]',  # Balance quality and size
        'worst'  # For metadata-only extraction
    ])
    
    # Official API configuration
    api_enabled: bool = True
    api_keys: List[str] = field(default_factory=list)
    
    # Content types to monitor
    content_types: List[str] = field(default_factory=lambda: [
        'trending', 'search', 'channel', 'playlist'
    ])
    
    # Monitoring targets
    monitored_channels: List[str] = field(default_factory=lambda: [
        'UCXuqSBlHAE6Xw-yeJA0Tunw',  # Linus Tech Tips
        'UCBJycsmduvYEL83R_U4JriQ',  # Marques Brownlee
        'UCsTcErHg8oDvUnTzoqsYeNw',  # CNN
        'UC16niRr50-MSBwiCO3Z0btA'   # BBC News
    ])
    
    search_keywords: List[str] = field(default_factory=lambda: [
        "breaking news", "emergency", "crisis", "disaster",
        "protest", "election", "summit", "trending",
        "earthquake", "fire", "flood", "storm"
    ])
    
    # Kafka configuration
    kafka_brokers: List[str] = field(default_factory=lambda: ['kafka:9092'])
    topics: Dict[str, str] = field(default_factory=lambda: {
        'videos': 'raw.youtube.videos',
        'comments': 'raw.youtube.comments',
        'metadata': 'raw.youtube.metadata'
    })
    
    # Rate limiting
    requests_per_day: int = 10000  # YouTube API quota

class MultiStrategyYouTubeIngestor:
    """Multi-strategy YouTube data collection"""
    
    def __init__(self, config: YouTubeConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,
            linger_ms=10,
            compression_type='snappy'
        )
        self.deduplicator = YouTubeDeduplicator()
        self.rate_limiter = YouTubeRateLimiter(config.requests_per_day)
        
        # Initialize monitoring
        self.metrics = YouTubeMetricsCollector()
        self.metrics.start_metrics_server()
        
        # Initialize YouTube clients
        self.yt_dlp_opts = self._initialize_yt_dlp_options()
        self.api_clients = []
        if config.api_enabled:
            self.api_clients = self._initialize_api_clients()
    
    def _initialize_yt_dlp_options(self) -> Dict[str, Any]:
        """Initialize yt-dlp options"""
        
        return {
            'format': ','.join(self.config.download_formats),
            'writesubtitles': True,  # Download subtitles for analysis
            'writeinfojson': True,    # Save metadata
            'skip_download': False,   # Actually download content
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'quiet': True,            # Reduce output noise
            'no_warnings': False,
            'extract_flat': False,    # Get full metadata
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if not self.config.download_formats else []
        }
    
    def _initialize_api_clients(self) -> List[Any]:
        """Initialize YouTube API clients"""
        
        clients = []
        
        for api_key in self.config.api_keys:
            try:
                client = build('youtube', 'v3', developerKey=api_key)
                clients.append(client)
            except Exception as e:
                logging.error(f"Failed to initialize YouTube API client: {e}")
        
        return clients
    
    async def start_ingestion(self):
        """Start multi-strategy YouTube ingestion"""
        
        logging.info("Starting YouTube multi-strategy ingestion")
        
        # Start yt-dlp based collection (if enabled)
        if self.config.yt_dlp_enabled:
            asyncio.create_task(self._yt_dlp_collection())
        
        # Start API-based collection (if enabled)
        if self.config.api_enabled and self.api_clients:
            asyncio.create_task(self._api_collection())
        
        # Start content discovery
        asyncio.create_task(self._content_discovery())
    
    async def _yt_dlp_collection(self):
        """Collect data using yt-dlp"""
        
        while True:
            try:
                # Method 1: Trending videos
                await self._collect_trending_videos()
                
                # Method 2: Keyword search
                await self._search_keywords()
                
                # Method 3: Channel monitoring
                await self._monitor_channels()
                
                # Method 4: Playlist monitoring
                await self._monitor_playlists()
                
                await asyncio.sleep(3600)  # Wait 1 hour between cycles
                
            except Exception as e:
                logging.error(f"yt-dlp collection error: {e}")
                await asyncio.sleep(300)
    
    async def _collect_trending_videos(self):
        """Collect trending videos from multiple regions"""
        
        regions = ["US", "GB", "DE", "FR", "JP", "IN", "BR", "RU"]
        
        for region in regions:
            if not self.rate_limiter.can_proceed('yt_dlp'):
                await asyncio.sleep(self.rate_limiter.get_wait_time('yt_dlp'))
            
            try:
                ydl = yt_dlp.YoutubeDL(self.yt_dlp_opts)
                
                # Extract trending videos
                info = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: ydl.extract_info(
                        f"https://www.youtube.com/feed/trending?gl={region}",
                        download=False
                    )
                )
                
                if info and 'entries' in info:
                    for video in info['entries']:
                        if video is None:
                            continue
                        
                        processed_video = self._process_yt_dlp_video(video, region)
                        
                        if not self.deduplicator.is_duplicate(processed_video):
                            start_time = time.time()
                            self.producer.send(self.config.topics['videos'], processed_video)
                            latency = time.time() - start_time
                            self.metrics.record_video_processed('yt_dlp')
                            self.metrics.record_ingestion_latency('video', latency)
                            
                            # Extract comments for high-engagement videos
                            if processed_video.get('engagement', {}).get('view_count', 0) > 10000:
                                await self._extract_video_comments(video['id'])
                
                self.rate_limiter.record_request('yt_dlp')
                
            except Exception as e:
                logging.error(f"Error collecting trending videos for {region}: {e}")
    
    async def _search_keywords(self):
        """Search videos by keywords"""
        
        for keyword in self.config.search_keywords:
            if not self.rate_limiter.can_proceed('yt_dlp'):
                await asyncio.sleep(self.rate_limiter.get_wait_time('yt_dlp'))
            
            try:
                ydl = yt_dlp.YoutubeDL(self.yt_dlp_opts)
                
                info = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ydl.extract_info(
                        f"ytsearch10:{keyword}",
                        download=False
                    )
                )
                
                if info and 'entries' in info:
                    for video in info['entries']:
                        if video is None:
                            continue
                        
                        processed_video = self._process_yt_dlp_video(video, 'search')
                        processed_video['search_keyword'] = keyword
                        
                        if not self.deduplicator.is_duplicate(processed_video):
                            start_time = time.time()
                            self.producer.send(self.config.topics['videos'], processed_video)
                            latency = time.time() - start_time
                            self.metrics.record_video_processed('yt_dlp')
                            self.metrics.record_ingestion_latency('video', latency)
                
                self.rate_limiter.record_request('yt_dlp')
                await asyncio.sleep(2)  # Rate limiting
                
            except Exception as e:
                logging.error(f"Error searching keyword '{keyword}': {e}")

    async def _monitor_channels(self):
        """Monitor channels for new content"""
        # Placeholder for channel monitoring logic
        pass

    async def _monitor_playlists(self):
        """Monitor playlists for new content"""
        # Placeholder for playlist monitoring logic
        pass

    async def _extract_video_comments(self, video_id: str):
        """Extract comments from video"""
        # Placeholder for comment extraction logic
        pass

    async def _content_discovery(self):
        """Ongoing content discovery"""
        # Placeholder for discovery logic
        pass
    
    async def _api_collection(self):
        """Collect data using official YouTube API"""
        
        if not self.api_clients:
            return
        
        client = self.api_clients[0]  # Implement client rotation
        
        while True:
            try:
                # Method 1: Search API
                await self._api_search_videos(client)
                
                # Method 2: Channel monitoring
                await self._api_monitor_channels(client)
                
                # Method 3: Trending videos
                await self._api_trending_videos(client)
                
                await asyncio.sleep(1800)  # Wait 30 minutes between API cycles
                
            except HttpError as e:
                if e.resp.status == 403:  # Quota exceeded
                    logging.warning("YouTube API quota exceeded")
                    await asyncio.sleep(3600)  # Wait 1 hour
                else:
                    logging.error(f"YouTube API error: {e}")
                    await asyncio.sleep(300)
            except Exception as e:
                logging.error(f"YouTube API collection error: {e}")
                await asyncio.sleep(300)
    
    async def _api_search_videos(self, client):
        """Search videos using YouTube API"""
        
        for keyword in self.config.search_keywords:
            if not self.rate_limiter.can_proceed('api'):
                await asyncio.sleep(self.rate_limiter.get_wait_time('api'))
            
            try:
                request = client.search().list(
                    part="snippet",
                    q=keyword,
                    type="video",
                    maxResults=50,
                    order="date",
                    publishedAfter=(datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
                )
                
                response = await asyncio.get_event_loop().run_in_executor(None, request.execute)
                
                for item in response.get('items', []):
                    # Get full video details
                    video_request = client.videos().list(
                        part="snippet,statistics,contentDetails",
                        id=item['id']['videoId']
                    )
                    video_response = await asyncio.get_event_loop().run_in_executor(None, video_request.execute)
                    
                    if video_response.get('items'):
                        video_data = self._process_api_video(
                            video_response['items'][0], 
                            keyword
                        )
                        
                        if not self.deduplicator.is_duplicate(video_data):
                            start_time = time.time()
                            self.producer.send(self.config.topics['videos'], video_data)
                            latency = time.time() - start_time
                            self.metrics.record_video_processed('api')
                            self.metrics.record_ingestion_latency('video', latency)
                
                self.rate_limiter.record_request('api')
                await asyncio.sleep(1)  # Rate limiting
                
            except HttpError as e:
                if e.resp.status == 403:
                    logging.warning(f"API quota exceeded for search: {keyword}")
                    break
                else:
                    logging.error(f"API search error for '{keyword}': {e}")

    async def _api_monitor_channels(self, client):
        """API based channel monitoring"""
        pass

    async def _api_trending_videos(self, client):
        """API based trending detection"""
        pass
    
    def _process_yt_dlp_video(self, video_info: Dict, source: str) -> Dict[str, Any]:
        """Process yt-dlp video info into standardized format"""
        
        return {
            "platform": "youtube",
            "id": video_info.get('id', ''),
            "title": video_info.get('title', ''),
            "description": video_info.get('description', ''),
            "channel": {
                "id": video_info.get('channel_id', ''),
                "name": video_info.get('channel', ''),
                "url": video_info.get('channel_url', '')
            },
            "engagement": {
                "view_count": video_info.get('view_count', 0),
                "like_count": video_info.get('like_count', 0),
                "comment_count": video_info.get('comment_count', 0)
            },
            "metadata": {
                "duration": video_info.get('duration', 0),
                "upload_date": video_info.get('upload_date', ''),
                "thumbnail": video_info.get('thumbnail', ''),
                "categories": video_info.get('categories', []),
                "tags": video_info.get('tags', []),
                "age_limit": video_info.get('age_limit', 0),
                "source": source
            },
            "content_analysis": {
                "subtitles_available": bool(video_info.get('automatic_captions', {})),
                "is_live": video_info.get('was_live', False),
                "has_chapters": bool(video_info.get('chapters', []))
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "source_tool": "yt_dlp",
                "processing_version": "2.0"
            }
        }
    
    def _process_api_video(self, video_item: Dict, keyword: str) -> Dict[str, Any]:
        """Process API video into standardized format"""
        
        snippet = video_item['snippet']
        statistics = video_item.get('statistics', {})
        content_details = video_item.get('contentDetails', {})
        
        return {
            "platform": "youtube",
            "id": video_item['id'],
            "title": snippet['title'],
            "description": snippet['description'],
            "channel": {
                "id": snippet['channelId'],
                "name": snippet['channelTitle']
            },
            "engagement": {
                "view_count": int(statistics.get('viewCount', 0)),
                "like_count": int(statistics.get('likeCount', 0)),
                "comment_count": int(statistics.get('commentCount', 0))
            },
            "metadata": {
                "published_at": snippet['publishedAt'],
                "duration": content_details.get('duration', ''),
                "dimension": content_details.get('dimension', ''),
                "definition": content_details.get('definition', ''),
                "caption": content_details.get('caption', ''),
                "search_keyword": keyword,
                "source": "official_api"
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }

class YouTubeDeduplicator:
    """YouTube content deduplication"""
    
    def __init__(self, cache_size: int = 50000):
        self.seen_videos = set()
        self.cache_size = cache_size
    
    def is_duplicate(self, video: Dict) -> bool:
        """Check if video is a duplicate"""
        
        video_hash = self._generate_video_hash(video)
        
        if video_hash in self.seen_videos:
            return True
        
        self.seen_videos.add(video_hash)
        
        if len(self.seen_videos) > self.cache_size:
            self._clean_cache()
        
        return False
    
    def _generate_video_hash(self, video: Dict) -> str:
        """Generate unique hash for video"""
        
        content = f"{video['id']}_{video['title'][:100]}_{video.get('metadata', {}).get('upload_date', '')}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _clean_cache(self):
        """Clean cache to maintain size"""
        
        items = list(self.seen_videos)
        self.seen_videos = set(items[-self.cache_size:])

class YouTubeRateLimiter:
    """YouTube-specific rate limiting"""
    
    def __init__(self, requests_per_day: int):
        self.limits = {
            'yt_dlp': 1000,  # Conservative limit for yt-dlp
            'api': requests_per_day
        }
        self.request_history = {
            'yt_dlp': [],
            'api': []
        }
    
    def can_proceed(self, method: str) -> bool:
        """Check if request can proceed"""
        
        self._clean_old_requests(method)
        return len(self.request_history[method]) < self.limits[method]
    
    def record_request(self, method: str):
        """Record a request"""
        
        self.request_history[method].append(datetime.utcnow())
    
    def get_wait_time(self, method: str) -> float:
        """Get time to wait until next request"""
        
        self._clean_old_requests(method)
        
        if len(self.request_history[method]) < self.limits[method]:
            return 0.0
        
        # Find when the oldest request will expire
        oldest = min(self.request_history[method])
        
        if method == 'api':
            wait_until = oldest + timedelta(days=1)  # Daily quota
        else:
            wait_until = oldest + timedelta(hours=1)  # Hourly limit for yt-dlp
        
        return max(0.0, (wait_until - datetime.utcnow()).total_seconds())
    
    def _clean_old_requests(self, method: str):
        """Remove old requests based on method"""
        
        if method == 'api':
            cutoff = datetime.utcnow() - timedelta(days=1)
        else:
            cutoff = datetime.utcnow() - timedelta(hours=1)
        
        self.request_history[method] = [
            t for t in self.request_history[method] 
            if t > cutoff
        ]

if __name__ == "__main__":
    config = YouTubeConfig()
    ingestor = MultiStrategyYouTubeIngestor(config)
    asyncio.run(ingestor.start_ingestion())
