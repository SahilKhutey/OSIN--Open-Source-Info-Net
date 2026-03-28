from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from playwright.async_api import async_playwright
import requests
from kafka import KafkaProducer
import json
import logging
import hashlib
import random
import time
from urllib.parse import quote_plus
import statistics

@dataclass
class LinkedInConfig:
    """LinkedIn ingestion configuration"""
    # Playwright configuration
    playwright_enabled: bool = True
    headless_browser: bool = True
    browser_concurrency: int = 2
    page_load_timeout: int = 30000
    
    # Proxy configuration
    proxy_enabled: bool = True
    proxy_list: List[str] = field(default_factory=lambda: [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:8080"
    ])
    
    # Session management
    session_rotation: bool = True
    max_sessions_per_hour: int = 50
    
    # Content types to monitor
    content_types: List[str] = field(default_factory=lambda: [
        'jobs', 'profiles', 'companies', 'posts', 'groups'
    ])
    
    # Search targets
    job_keywords: List[str] = field(default_factory=lambda: [
        "cybersecurity", "data scientist", "ai engineer", 
        "machine learning", "blockchain", "cloud architect"
    ])
    
    company_targets: List[str] = field(default_factory=lambda: [
        "microsoft", "google", "amazon", "meta", "apple",
        "tesla", "netflix", "uber", "airbnb", "linkedin"
    ])
    
    # Kafka configuration
    kafka_brokers: List[str] = field(default_factory=lambda: ['kafka:9092'])
    topics: Dict[str, str] = field(default_factory=lambda: {
        'jobs': 'raw.linkedin.jobs',
        'profiles': 'raw.linkedin.profiles',
        'companies': 'raw.linkedin.companies',
        'posts': 'raw.linkedin.posts'
    })
    
    # Rate limiting
    requests_per_hour: int = 100
    delay_between_requests: int = 36

class MultiStrategyLinkedInIngestor:
    """Multi-strategy LinkedIn data collection"""
    
    def __init__(self, config: LinkedInConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,
            linger_ms=10,
            compression_type='snappy'
        )
        self.deduplicator = LinkedInDeduplicator()
        self.rate_limiter = LinkedInRateLimiter(config.requests_per_hour)
        self.session_manager = LinkedInSessionManager()
        self.proxy_rotator = ProxyRotator(config.proxy_list)
        self.browser_contexts = []
    
    async def start_ingestion(self):
        """Start multi-strategy LinkedIn ingestion"""
        
        logging.info("Starting LinkedIn multi-strategy ingestion")
        if self.config.playwright_enabled:
            asyncio.create_task(self._playwright_monitoring())
        asyncio.create_task(self._content_discovery())
    
    async def _playwright_monitoring(self):
        """Monitor LinkedIn using Playwright"""
        
        async with async_playwright() as p:
            for i in range(self.config.browser_concurrency):
                browser = await p.chromium.launch(
                    headless=self.config.headless_browser,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080}
                )
                self.browser_contexts.append((browser, context))
            
            try:
                while True:
                    for keyword in self.config.job_keywords:
                        if not self.rate_limiter.can_proceed('playwright'):
                            await asyncio.sleep(self.rate_limiter.get_wait_time('playwright'))
                        
                        await self._monitor_linkedin_jobs(keyword, self.browser_contexts[0][1])
                        self.rate_limiter.record_request('playwright')
                        await asyncio.sleep(self.config.delay_between_requests)
                    
                    for company in self.config.company_targets:
                        if not self.rate_limiter.can_proceed('playwright'):
                            await asyncio.sleep(self.rate_limiter.get_wait_time('playwright'))
                        
                        await self._monitor_linkedin_company(company, self.browser_contexts[0][1])
                        self.rate_limiter.record_request('playwright')
                        await asyncio.sleep(self.config.delay_between_requests)
                    
                    await asyncio.sleep(3600)
                    
            except Exception as e:
                logging.error(f"Playwright monitoring error: {e}")
                await asyncio.sleep(300)
            finally:
                for browser, context in self.browser_contexts:
                    await context.close()
                    await browser.close()
    
    async def _monitor_linkedin_jobs(self, keyword: str, context):
        """Monitor LinkedIn jobs"""
        try:
            proxy = self.proxy_rotator.get_next_proxy()
            page = await context.new_page()
            if self.config.proxy_enabled and proxy:
                await page.route("**/*", lambda route: route.continue_(proxy=proxy))
            
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(keyword)}"
            await page.goto(search_url, timeout=self.config.page_load_timeout)
            await page.wait_for_selector("body", timeout=10000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            job_listings = await page.query_selector_all(".jobs-search-results-list li")
            for job_element in job_listings[:10]:
                try:
                    job_data = await self._extract_job_data(job_element, page, keyword)
                    if job_data and not self.deduplicator.is_duplicate(job_data):
                        self.producer.send(self.config.topics['jobs'], job_data)
                except Exception as e:
                    logging.error(f"Error extracting job data: {e}")
                    continue
            await page.close()
        except Exception as e:
            logging.error(f"Error monitoring LinkedIn jobs for {keyword}: {e}")
    
    async def _monitor_linkedin_company(self, company: str, context):
        """Monitor LinkedIn company page"""
        try:
            proxy = self.proxy_rotator.get_next_proxy()
            page = await context.new_page()
            if self.config.proxy_enabled and proxy:
                await page.route("**/*", lambda route: route.continue_(proxy=proxy))
            
            company_url = f"https://www.linkedin.com/company/{company}"
            await page.goto(company_url, timeout=self.config.page_load_timeout)
            await page.wait_for_selector("body", timeout=10000)
            
            company_data = await self._extract_company_data(page, company)
            if company_data and not self.deduplicator.is_duplicate(company_data):
                self.producer.send(self.config.topics['companies'], company_data)
            
            await self._extract_company_posts(page, company, context)
            await page.close()
        except Exception as e:
            logging.error(f"Error monitoring LinkedIn company {company}: {e}")
    
    async def _extract_job_data(self, job_element, page, keyword: str) -> Optional[Dict[str, Any]]:
        """Extract job data"""
        try:
            job_data = await job_element.evaluate("""(element) => {
                const titleElement = element.querySelector('h3 a');
                const companyElement = element.querySelector('h4 a');
                const locationElement = element.querySelector('.job-search-card__location');
                const timeElement = element.querySelector('time');
                return {
                    title: titleElement ? titleElement.textContent.trim() : '',
                    url: titleElement ? titleElement.href : '',
                    company: companyElement ? companyElement.textContent.trim() : '',
                    companyUrl: companyElement ? companyElement.href : '',
                    location: locationElement ? locationElement.textContent.trim() : '',
                    postedTime: timeElement ? timeElement.textContent.trim() : '',
                    postedDateTime: timeElement ? timeElement.getAttribute('datetime') : ''
                };
            }""")
            if not job_data or not job_data.get('title'):
                return None
            return {
                "platform": "linkedin",
                "type": "job",
                "id": hashlib.sha256(job_data['url'].encode()).hexdigest()[:16] if job_data['url'] else f"job_{int(time.time())}",
                "title": job_data['title'],
                "company": job_data['company'],
                "location": job_data['location'],
                "url": job_data['url'],
                "metadata": {
                    "posted_time": job_data['postedTime'],
                    "posted_datetime": job_data['postedDateTime'],
                    "search_keyword": keyword,
                    "source": "playwright"
                },
                "processing_metadata": {
                    "collected_at": datetime.utcnow().isoformat(),
                    "processing_version": "2.0"
                }
            }
        except Exception as e:
            logging.error(f"Error extracting job data: {e}")
            return None
    
    async def _extract_company_data(self, page, company: str) -> Optional[Dict[str, Any]]:
        """Extract company data"""
        try:
            company_data = await page.evaluate("""() => {
                const nameElement = document.querySelector('h1.top-card-layout__title');
                const descriptionElement = document.querySelector('.core-section-container__content p');
                const employeesElement = document.querySelector('[data-test-id="about-us__employees"]');
                const industryElement = document.querySelector('[data-test-id="about-us__industry"]');
                const websiteElement = document.querySelector('[data-test-id="about-us__website"]');
                return {
                    name: nameElement ? nameElement.textContent.trim() : '',
                    description: descriptionElement ? descriptionElement.textContent.trim() : '',
                    employees: employeesElement ? employeesElement.textContent.trim() : '',
                    industry: industryElement ? industryElement.textContent.trim() : '',
                    website: websiteElement ? websiteElement.href : '',
                    url: window.location.href
                };
            }""")
            if not company_data or not company_data.get('name'):
                return None
            return {
                "platform": "linkedin",
                "type": "company",
                "id": hashlib.sha256(company.encode()).hexdigest()[:16],
                "name": company_data['name'],
                "description": company_data['description'],
                "url": company_data['url'],
                "metadata": {
                    "employees": company_data['employees'],
                    "industry": company_data['industry'],
                    "website": company_data['website'],
                    "source": "playwright"
                },
                "processing_metadata": {
                    "collected_at": datetime.utcnow().isoformat(),
                    "processing_version": "2.0"
                }
            }
        except Exception as e:
            logging.error(f"Error extracting company data for {company}: {e}")
            return None
    
    async def _extract_company_posts(self, page, company: str, context):
        """Extract recent posts"""
        try:
            posts_section = await page.query_selector('[data-test-id="posts-section"]')
            if not posts_section: return
            post_elements = await page.query_selector_all('[data-test-id="post-item"]')
            for post_element in post_elements[:5]:
                try:
                    post_data = await post_element.evaluate("""(element) => {
                        const authorElement = element.querySelector('.update-components-actor__title');
                        const contentElement = element.querySelector('.update-components-text');
                        const timeElement = element.querySelector('time');
                        const reactionsElement = element.querySelector('[data-test-id="reaction-count"]');
                        return {
                            author: authorElement ? authorElement.textContent.trim() : '',
                            content: contentElement ? contentElement.textContent.trim() : '',
                            timePosted: timeElement ? timeElement.textContent.trim() : '',
                            reactions: reactionsElement ? reactionsElement.textContent.trim() : '0'
                        };
                    }""")
                    if post_data and post_data.get('content'):
                        processed_post = {
                            "platform": "linkedin",
                            "type": "post",
                            "id": hashlib.sha256(f"{company}_{int(time.time())}_{random.randint(1,1000)}".encode()).hexdigest()[:16],
                            "content": post_data['content'],
                            "author": post_data['author'],
                            "company": company,
                            "metadata": { "time_posted": post_data['timePosted'], "reactions": post_data['reactions'], "source": "playwright" },
                            "processing_metadata": { "collected_at": datetime.utcnow().isoformat(), "processing_version": "2.0" }
                        }
                        if not self.deduplicator.is_duplicate(processed_post):
                            self.producer.send(self.config.topics['posts'], processed_post)
                except Exception as e:
                    logging.error(f"Error extracting post data: {e}")
                    continue
        except Exception as e:
            logging.error(f"Error extracting company posts for {company}: {e}")

    async def _content_discovery(self):
        """Placeholder for content discovery"""
        pass

class LinkedInDeduplicator:
    """LinkedIn content deduplication"""
    def __init__(self, cache_size: int = 10000):
        self.seen_content = set()
        self.cache_size = cache_size
    def is_duplicate(self, content: Dict) -> bool:
        content_hash = self._generate_content_hash(content)
        if content_hash in self.seen_content: return True
        self.seen_content.add(content_hash)
        if len(self.seen_content) > self.cache_size: self._clean_cache()
        return False
    def _generate_content_hash(self, content: Dict) -> str:
        identifier = content.get('url', '') or content.get('id', '') or content.get('content', '')
        timestamp = content.get('processing_metadata', {}).get('collected_at', '')
        normalized = f"{identifier}_{timestamp}"
        return hashlib.sha256(normalized.encode()).hexdigest()
    def _clean_cache(self):
        items = list(self.seen_content)
        self.seen_content = set(items[-self.cache_size:])

class LinkedInRateLimiter:
    """LinkedIn-specific rate limiting"""
    def __init__(self, requests_per_hour: int):
        self.limits = {'playwright': requests_per_hour, 'api': 0}
        self.request_history = {'playwright': []}
    def can_proceed(self, method: str) -> bool:
        self._clean_old_requests(method)
        return len(self.request_history[method]) < self.limits[method]
    def record_request(self, method: str):
        self.request_history[method].append(datetime.utcnow())
    def get_wait_time(self, method: str) -> float:
        self._clean_old_requests(method)
        if len(self.request_history[method]) < self.limits[method]: return 0.0
        oldest = min(self.request_history[method])
        wait_until = oldest + timedelta(hours=1)
        return max(0.0, (wait_until - datetime.utcnow()).total_seconds())
    def _clean_old_requests(self, method: str):
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.request_history[method] = [t for t in self.request_history[method] if t > cutoff]

class LinkedInSessionManager:
    """Manage LinkedIn browser sessions"""
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(hours=2)
    async def get_session(self) -> Dict[str, Any]:
        session_id = f"session_{int(datetime.utcnow().timestamp())}"
        session = {
            'id': session_id,
            'created_at': datetime.utcnow(),
            'valid_until': datetime.utcnow() + self.session_timeout,
            'user_agent': "Mozilla/5.0",
            'headers': {}
        }
        self.sessions[session_id] = session
        return session

class ProxyRotator:
    """Rotate through proxy servers"""
    def __init__(self, proxy_list: List[str]):
        self.proxy_list = proxy_list
        self.current_index = 0
    def get_next_proxy(self) -> Optional[str]:
        if not self.proxy_list: return None
        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        return proxy

class LinkedInIntelligence:
    """Advanced LinkedIn intelligence gathering"""
    def __init__(self):
        self.job_analyzer = JobMarketAnalyzer()
        self.company_analyzer = CompanyAnalyzer()
        self.skill_analyzer = SkillAnalyzer()
    async def analyze_job_market_trends(self, job_data: List[Dict]) -> Dict[str, Any]:
        if not job_data: return {}
        job_titles = [j.get('title', '') for j in job_data if j.get('type') == 'job']
        return {
            'market_trends': await self.job_analyzer.analyze_trends(job_titles),
            'skill_demand': await self.skill_analyzer.analyze_skill_demand([]), # Placeholder
            'industry_analysis': await self._analyze_industries(job_titles)
        }
    async def _analyze_industries(self, job_titles: List[str]) -> Dict[str, Any]:
        industry_keywords = {'technology': ['software', 'developer', 'engineer'], 'finance': ['bank', 'investment']}
        industry_counts = {}
        for title in job_titles:
            title_lower = title.lower()
            for industry, keywords in industry_keywords.items():
                if any(k in title_lower for k in keywords):
                    industry_counts[industry] = industry_counts.get(industry, 0) + 1
        return {'industry_distribution': industry_counts}

class JobMarketAnalyzer:
    async def analyze_trends(self, job_titles: List[str]) -> Dict[str, Any]:
        if not job_titles: return {}
        title_counts = {t: job_titles.count(t) for t in set(job_titles)}
        return {'popular_roles': dict(sorted(title_counts.items(), key=lambda x: x[1], reverse=True)[:10])}

class CompanyAnalyzer:
    async def analyze_company_growth(self, company_data: List[Dict]) -> Dict[str, Any]:
        return {"status": "placeholder"}

class SkillAnalyzer:
    async def analyze_skill_demand(self, skills: List[str]) -> Dict[str, Any]:
        return {"status": "placeholder"}
