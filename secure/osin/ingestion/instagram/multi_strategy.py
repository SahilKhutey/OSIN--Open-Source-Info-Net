from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import instaloader
from playwright.async_api import async_playwright
from kafka import KafkaProducer
import json
import logging
import hashlib
import os
import tempfile
import time
from .monitoring import InstagramMetricsCollector
from .advanced_features import InstagramIntelligence

@dataclass
class InstagramConfig:
    """Instagram ingestion configuration"""
    # instaloader configuration
    instaloader_enabled: bool = True
    instaloader_settings: Dict[str, Any] = field(default_factory=lambda: {
        'download_pictures': False,  # Metadata only for legal reasons
        'download_videos': False,
        'download_video_thumbnails': False,
        'download_geotags': False,
        'download_comments': True,
        'save_metadata': True,
        'post_metadata_txt_pattern': None,  # Don't save files
        'max_connection_attempts': 3
    })
    
    # Playwright configuration (fallback)
    playwright_enabled: bool = True
    headless_browser: bool = True
    
    # Target monitoring
    monitored_profiles: List[str] = field(default_factory=lambda: [
        "cnn", "bbcnews", "reuters", "apnews",  # News organizations
        "whitehouse", "un", "nato",  # Government/orgs
        "natgeo", "sciencechannel", "techcrunch"  # Content creators
    ])
    
    monitored_hashtags: List[str] = field(default_factory=lambda: [
        "breakingnews", "emergency", "crisis", "disaster",
        "protest", "election", "climate", "technology"
    ])
    
    # Kafka configuration
    kafka_brokers: List[str] = field(default_factory=lambda: ['kafka:9092'])
    topics: Dict[str, str] = field(default_factory=lambda: {
        'posts': 'raw.instagram.posts',
        'stories': 'raw.instagram.stories',
        'profiles': 'raw.instagram.profiles'
    })
    
    # Rate limiting (critical for Instagram)
    requests_per_hour: int = 200  # Very conservative
    delay_between_requests: int = 18  # seconds

class MultiStrategyInstagramIngestor:
    """Multi-strategy Instagram data collection"""
    
    def __init__(self, config: InstagramConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,
            linger_ms=10,
            compression_type='snappy'
        )
        self.deduplicator = InstagramDeduplicator()
        self.rate_limiter = InstagramRateLimiter(config.requests_per_hour)
        self.intelligence = InstagramIntelligence()
        
        # Initialize monitoring
        self.metrics = InstagramMetricsCollector()
        self.metrics.start_metrics_server()
        
        # Initialize tools
        self.instaloader = None
        self.playwright = None
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize Instagram data collection tools"""
        
        # Initialize instaloader
        if self.config.instaloader_enabled:
            try:
                self.instaloader = instaloader.Instaloader(
                    **self.config.instaloader_settings
                )
                # Set up session if available
                if os.getenv('INSTAGRAM_SESSION'):
                    session_file = f"session-{os.getenv('INSTAGRAM_USERNAME')}"
                    if os.path.exists(session_file):
                        self.instaloader.load_session_from_file(
                            os.getenv('INSTAGRAM_USERNAME'),
                            session_file
                        )
            except Exception as e:
                logging.error(f"Failed to initialize instaloader: {e}")
                self.instaloader = None
    
    async def start_ingestion(self):
        """Start multi-strategy Instagram ingestion"""
        
        logging.info("Starting Instagram multi-strategy ingestion")
        
        # Start instaloader monitoring (if enabled)
        if self.config.instaloader_enabled and self.instaloader:
            asyncio.create_task(self._instaloader_monitoring())
        
        # Start Playwright monitoring (if enabled)
        if self.config.playwright_enabled:
            asyncio.create_task(self._playwright_monitoring())
        
        # Start content discovery
        asyncio.create_task(self._content_discovery())
        
        # Start intelligence analysis
        asyncio.create_task(self._periodic_intelligence_analysis())
    
    async def _periodic_intelligence_analysis(self):
        """Perform periodic intelligence analysis on collected data"""
        
        while True:
            try:
                logging.info("Starting periodic Instagram intelligence analysis")
                # In a real system, this would fetch recent data from Kafka or a database
                # For now, we'll analyze the monitored profiles
                
                for profile in self.config.monitored_profiles:
                    # Intelligence gathering would be performed here
                    pass
                
                await asyncio.sleep(86400)  # Once per day
                
            except Exception as e:
                logging.error(f"Intelligence analysis error: {e}")
                await asyncio.sleep(3600)
    
    async def _instaloader_monitoring(self):
        """Monitor Instagram using instaloader"""
        
        while True:
            try:
                # Monitor profiles
                for profile in self.config.monitored_profiles:
                    if not self.rate_limiter.can_proceed('instaloader'):
                        await asyncio.sleep(self.rate_limiter.get_wait_time('instaloader'))
                    
                    await self._monitor_instaloader_profile(profile)
                    self.rate_limiter.record_request('instaloader')
                    await asyncio.sleep(self.config.delay_between_requests)
                
                # Monitor hashtags
                for hashtag in self.config.monitored_hashtags:
                    if not self.rate_limiter.can_proceed('instaloader'):
                        await asyncio.sleep(self.rate_limiter.get_wait_time('instaloader'))
                    
                    await self._monitor_instaloader_hashtag(hashtag)
                    self.rate_limiter.record_request('instaloader')
                    await asyncio.sleep(self.config.delay_between_requests)
                
                await asyncio.sleep(3600)  # Wait 1 hour between cycles
                
            except Exception as e:
                logging.error(f"Instaloader monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_instaloader_profile(self, profile: str):
        """Monitor a specific Instagram profile"""
        
        try:
            # Get profile metadata
            profile_obj = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: instaloader.Profile.from_username(
                    self.instaloader.context, 
                    profile
                )
            )
            
            # Process profile information
            profile_data = self._process_instaloader_profile(profile_obj)
            self.producer.send(self.config.topics['profiles'], profile_data)
            
            # Get recent posts
            # instaloader post objects should be handled carefully
            def get_posts_list():
                return list(profile_obj.get_posts())
            
            posts = await asyncio.get_event_loop().run_in_executor(None, get_posts_list)
            
            for post in posts[:10]:  # Limit to 10 most recent posts
                post_data = self._process_instaloader_post(post, profile)
                
                if not self.deduplicator.is_duplicate(post_data):
                    start_time = time.time()
                    self.producer.send(self.config.topics['posts'], post_data)
                    latency = time.time() - start_time
                    self.metrics.record_posts_collected('instaloader')
                    self.metrics.record_collection_latency('instaloader', latency)
                
                # Get post comments
                def get_comments_list():
                    return list(post.get_comments())
                
                comments = await asyncio.get_event_loop().run_in_executor(None, get_comments_list)
                
                for comment in comments:
                    comment_data = self._process_instaloader_comment(comment, post.shortcode)
                    self.producer.send(self.config.topics['posts'], comment_data)
        
        except instaloader.exceptions.ProfileNotExistsException:
            logging.warning(f"Instagram profile not found: {profile}")
        except Exception as e:
            logging.error(f"Error monitoring profile {profile}: {e}")
    
    async def _monitor_instaloader_hashtag(self, hashtag: str):
        """Monitor posts by hashtag"""
        
        try:
            # Get hashtag posts
            def get_hashtag_posts():
                return list(instaloader.Hashtag.from_name(
                    self.instaloader.context, 
                    hashtag.replace('#', '')
                ).get_posts())
            
            posts = await asyncio.get_event_loop().run_in_executor(None, get_hashtag_posts)
            
            for post in posts[:20]:  # Limit to 20 posts per hashtag
                post_data = self._process_instaloader_post(post, f"hashtag_{hashtag}")
                
                if not self.deduplicator.is_duplicate(post_data):
                    self.producer.send(self.config.topics['posts'], post_data)
        
        except Exception as e:
            logging.error(f"Error monitoring hashtag {hashtag}: {e}")
    
    async def _playwright_monitoring(self):
        """Monitor Instagram using Playwright (headless browser)"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.config.headless_browser)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            while True:
                try:
                    # Monitor public pages that can't be accessed via API
                    for profile in self.config.monitored_profiles:
                        if not self.rate_limiter.can_proceed('playwright'):
                            await asyncio.sleep(self.rate_limiter.get_wait_time('playwright'))
                        
                        await self._monitor_playwright_profile(page, profile)
                        self.rate_limiter.record_request('playwright')
                        await asyncio.sleep(self.config.delay_between_requests)
                    
                    await asyncio.sleep(3600)  # Wait 1 hour between cycles
                    
                except Exception as e:
                    logging.error(f"Playwright monitoring error: {e}")
                    await asyncio.sleep(300)
            
            await browser.close()
    
    async def _monitor_playwright_profile(self, page, profile: str):
        """Monitor profile using Playwright"""
        
        try:
            await page.goto(f"https://www.instagram.com/{profile}/")
            
            # Wait for page load
            await page.wait_for_selector("article", timeout=30000)
            
            # Extract public information
            profile_data = await self._extract_playwright_profile_data(page, profile)
            self.producer.send(self.config.topics['profiles'], profile_data)
            
            # Extract recent posts (publicly available)
            posts_data = await self._extract_playwright_posts(page, profile)
            for post in posts_data:
                if not self.deduplicator.is_duplicate(post):
                    start_time = time.time()
                    self.producer.send(self.config.topics['posts'], post)
                    latency = time.time() - start_time
                    self.metrics.record_posts_collected('playwright')
                    self.metrics.record_collection_latency('playwright', latency)
        
        except Exception as e:
            logging.error(f"Playwright error for {profile}: {e}")

    async def _content_discovery(self):
        """Ongoing content discovery - placeholder"""
        pass
    
    def _process_instaloader_profile(self, profile) -> Dict[str, Any]:
        """Process instaloader profile into standardized format"""
        
        return {
            "platform": "instagram",
            "type": "profile",
            "id": profile.userid,
            "username": profile.username,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "followers": profile.followers,
            "following": profile.followees,
            "is_private": profile.is_private,
            "is_verified": profile.is_verified,
            "metadata": {
                "posts_count": profile.mediacount,
                "profile_pic_url": profile.profile_pic_url,
                "external_url": profile.external_url,
                "business_category": profile.business_category_name,
                "is_business": profile.is_business_account
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "source": "instaloader",
                "processing_version": "2.0"
            }
        }
    
    def _process_instaloader_post(self, post, source: str) -> Dict[str, Any]:
        """Process instaloader post into standardized format"""
        
        return {
            "platform": "instagram",
            "type": "post",
            "id": post.shortcode,
            "caption": post.caption,
            "owner": {
                "id": post.owner_id,
                "username": post.owner_username
            },
            "engagement": {
                "likes": post.likes,
                "comments": post.comments,
                "video_views": post.video_view_count
            },
            "metadata": {
                "created_at": post.date_utc.isoformat(),
                "is_video": post.is_video,
                "url": f"https://www.instagram.com/p/{post.shortcode}",
                "location": post.location,
                "tags": post.caption_hashtags,
                "mentions": post.caption_mentions,
                "source": source
            },
            "media_metadata": {
                "media_count": post.mediacount if hasattr(post, 'mediacount') else 1,
                "dimensions": f"{post.video_width}x{post.video_height}" if post.is_video else "",
                "duration": post.video_duration if post.is_video else 0
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "source_tool": "instaloader",
                "processing_version": "2.0"
            }
        }
    
    def _process_instaloader_comment(self, comment, post_id: str) -> Dict[str, Any]:
        """Process instaloader comment"""
        
        return {
            "platform": "instagram",
            "type": "comment",
            "id": comment.id,
            "text": comment.text,
            "owner": {
                "id": comment.owner_id,
                "username": comment.owner_username
            },
            "post_id": post_id,
            "engagement": {
                "likes": comment.likes_count
            },
            "metadata": {
                "created_at": comment.created_at_utc.isoformat(),
                "is_restricted": comment.is_restricted
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "source_tool": "instaloader",
                "processing_version": "2.0"
            }
        }
    
    async def _extract_playwright_profile_data(self, page, profile: str) -> Dict[str, Any]:
        """Extract profile data using Playwright"""
        
        try:
            # Extract basic profile information from public page
            profile_data = await page.evaluate("""() => {
                const profileElement = document.querySelector('header section');
                if (!profileElement) return null;
                
                return {
                    username: profileElement.querySelector('h2')?.textContent,
                    full_name: profileElement.querySelector('span')?.textContent,
                    biography: profileElement.querySelector('.-vDIg span')?.textContent,
                    posts_count: document.querySelector('header section ul li:nth-child(1) span')?.textContent,
                    followers: document.querySelector('header section ul li:nth-child(2) span')?.textContent,
                    following: document.querySelector('header section ul li:nth-child(3) span')?.textContent
                };
            }""")
            
            return {
                "platform": "instagram",
                "type": "profile",
                "username": profile,
                "full_name": profile_data.get('full_name', '') if profile_data else '',
                "biography": profile_data.get('biography', '') if profile_data else '',
                "metadata": {
                    "posts_count": profile_data.get('posts_count', '0') if profile_data else '0',
                    "followers": profile_data.get('followers', '0') if profile_data else '0',
                    "following": profile_data.get('following', '0') if profile_data else '0',
                    "source": "playwright"
                },
                "processing_metadata": {
                    "collected_at": datetime.utcnow().isoformat(),
                    "processing_version": "2.0"
                }
            }
            
        except Exception as e:
            logging.error(f"Playwright profile extraction error: {e}")
            return {}
    
    async def _extract_playwright_posts(self, page, profile: str) -> List[Dict[str, Any]]:
        """Extract posts using Playwright"""
        
        try:
            posts_data = await page.evaluate("""() => {
                const posts = [];
                const postElements = document.querySelectorAll('article div div div a');
                
                postElements.forEach((element, index) => {
                    if (index >= 9) return; // Limit to 9 posts
                    
                    const href = element.getAttribute('href');
                    const img = element.querySelector('img');
                    
                    posts.push({
                        url: href,
                        thumbnail: img?.getAttribute('src'),
                        alt: img?.getAttribute('alt')
                    });
                });
                
                return posts;
            }""")
            
            processed_posts = []
            for post in posts_data:
                processed_posts.append({
                    "platform": "instagram",
                    "type": "post",
                    "url": f"https://www.instagram.com{post['url']}",
                    "thumbnail": post['thumbnail'],
                    "alt_text": post['alt'],
                    "metadata": {
                        "source": "playwright",
                        "profile": profile
                    },
                    "processing_metadata": {
                        "collected_at": datetime.utcnow().isoformat(),
                        "processing_version": "2.0"
                    }
                })
            
            return processed_posts
            
        except Exception as e:
            logging.error(f"Playwright posts extraction error: {e}")
            return []

class InstagramDeduplicator:
    """Instagram content deduplication"""
    
    def __init__(self, cache_size: int = 50000):
        self.seen_content = set()
        self.cache_size = cache_size
    
    def is_duplicate(self, content: Dict) -> bool:
        """Check if content is a duplicate"""
        
        content_hash = self._generate_content_hash(content)
        
        if content_hash in self.seen_content:
            return True
        
        self.seen_content.add(content_hash)
        
        if len(self.seen_content) > self.cache_size:
            self._clean_cache()
        
        return False
    
    def _generate_content_hash(self, content: Dict) -> str:
        """Generate unique hash for content"""
        
        # Use URL + timestamp for deduplication
        url = content.get('url', content.get('id', ''))
        timestamp = content.get('processing_metadata', {}).get('collected_at', '')
        
        normalized = f"{url}_{timestamp}"
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _clean_cache(self):
        """Clean cache to maintain size"""
        
        items = list(self.seen_content)
        self.seen_content = set(items[-self.cache_size:])

class InstagramRateLimiter:
    """Instagram-specific rate limiting"""
    
    def __init__(self, requests_per_hour: int):
        self.limits = {
            'instaloader': requests_per_hour,
            'playwright': 100  # More conservative for browser automation
        }
        self.request_history = {
            'instaloader': [],
            'playwright': []
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
        
        # Find when the oldest request will expire (1 hour window)
        oldest = min(self.request_history[method])
        wait_until = oldest + timedelta(hours=1)
        
        return max(0.0, (wait_until - datetime.utcnow()).total_seconds())
    
    def _clean_old_requests(self, method: str):
        """Remove requests older than 1 hour"""
        
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.request_history[method] = [
            t for t in self.request_history[method] 
            if t > cutoff
        ]

if __name__ == "__main__":
    config = InstagramConfig()
    ingestor = MultiStrategyInstagramIngestor(config)
    asyncio.run(ingestor.start_ingestion())
