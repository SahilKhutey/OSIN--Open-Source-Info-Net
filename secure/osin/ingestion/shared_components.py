import hashlib
import re
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

class DeduplicationEngine:
    """Advanced deduplication across platforms"""
    
    def __init__(self, cache_size: int = 100000):
        self.content_cache = set()
        self.cache_size = cache_size
    
    def is_duplicate(self, content: Dict) -> bool:
        """Check if content is a duplicate"""
        
        content_hash = self._generate_content_hash(content)
        
        if content_hash in self.content_cache:
            return True
        
        # Add to cache and maintain size
        self.content_cache.add(content_hash)
        if len(self.content_cache) > self.cache_size:
            self._clean_cache()
        
        return False
    
    def _generate_content_hash(self, content: Dict) -> str:
        """Generate content hash for deduplication"""
        
        # Use id if available, otherwise title and snippet of text
        if 'id' in content and content['id']:
            return hashlib.sha256(str(content['id']).encode()).hexdigest()
            
        text_content = f"{content.get('title', '')}_{content.get('text', '')[:100]}"
        normalized = self._normalize_text(text_content)
        
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent hashing"""
        text = re.sub(r'\s+', ' ', text)
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _clean_cache(self):
        """Clean cache to maintain size"""
        items = list(self.content_cache)
        self.content_cache = set(items[-self.cache_size:])

class ContentCleaner:
    """Clean and normalize content"""
    
    def __init__(self):
        # Expanded emoji pattern
        self.emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
    
    def clean_content(self, content: Dict) -> Dict:
        """Clean content for processing"""
        cleaned = content.copy()
        
        for field in ['title', 'text', 'description', 'summary']:
            if field in cleaned and cleaned[field]:
                cleaned[field] = self._clean_text(cleaned[field])
        
        cleaned['cleaning_metadata'] = {
            'cleaned_at': datetime.utcnow().isoformat(),
            'cleaning_version': '2.0'
        }
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Clean individual text field"""
        if not text:
            return ""
        text = self.emoji_pattern.sub(r'', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

class AntiBlockingStrategy:
    """Anti-blocking strategies for web scraping"""
    
    def __init__(self):
        self.proxy_list = [
            "http://proxy1.com:8080",
            "http://proxy2.com:8080",
            "http://proxy3.com:8080"
        ]
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        ]
        self.current_proxy_index = 0
        self.current_ua_index = 0
    
    def get_request_headers(self) -> Dict[str, str]:
        """Get randomized request headers"""
        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        
        return {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def get_next_proxy(self) -> str:
        """Rotate proxies"""
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy

class RateLimiter:
    """Advanced sliding window rate limiting"""
    
    def __init__(self, requests_per_hour: int):
        self.requests_per_hour = requests_per_hour
        self.request_history = []
    
    def can_proceed(self) -> bool:
        """Check if request can proceed"""
        self._clean_old_requests()
        return len(self.request_history) < self.requests_per_hour
    
    def record_request(self):
        """Record a request"""
        self.request_history.append(datetime.utcnow())
    
    def _clean_old_requests(self):
        """Remove requests older than 1 hour"""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.request_history = [t for t in self.request_history if t > cutoff]
