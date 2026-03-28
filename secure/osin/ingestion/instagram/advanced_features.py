from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import statistics
import random
import re
from collections import Counter

class InstagramIntelligence:
    """Advanced Instagram intelligence gathering"""
    
    def __init__(self):
        self.profile_analyzer = ProfileAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.trend_detector = TrendDetector()
    
    async def analyze_profile_engagement(self, profile_data: List[Dict]) -> Dict[str, Any]:
        """Analyze profile engagement patterns"""
        
        if not profile_data:
            return {}
        
        # Extract engagement metrics
        engagement_data = []
        for post in profile_data:
            if post.get('type') == 'post':
                engagement = post.get('engagement', {})
                engagement_data.append({
                    'likes': engagement.get('likes', 0),
                    'comments': engagement.get('comments', 0),
                    'views': engagement.get('video_views', 0),
                    'created_at': post.get('metadata', {}).get('created_at')
                })
        
        if not engagement_data:
            return {}
        
        # Calculate engagement metrics
        likes = [e['likes'] for e in engagement_data if e['likes'] > 0]
        comments = [e['comments'] for e in engagement_data if e['comments'] > 0]
        
        analysis = {
            'engagement_metrics': {
                'avg_likes': statistics.mean(likes) if likes else 0,
                'avg_comments': statistics.mean(comments) if comments else 0,
                'engagement_rate': await self._calculate_engagement_rate(engagement_data),
                'peak_engagement_time': await self._find_peak_engagement_time(engagement_data),
                'engagement_volatility': await self._calculate_volatility(likes + comments)
            },
            'content_performance': await self._analyze_content_performance(engagement_data),
            'audience_insights': await self._analyze_audience_behavior(engagement_data)
        }
        
        return analysis
    
    async def _calculate_engagement_rate(self, engagement_data: List[Dict]) -> float:
        """Calculate engagement rate"""
        
        if not engagement_data:
            return 0.0
        
        total_engagement = sum(
            e.get('likes', 0) + e.get('comments', 0) + e.get('views', 0)
            for e in engagement_data
        )
        
        follower_count = 10000  # Default assumption, would come from profile data
        
        return (total_engagement / (follower_count * len(engagement_data))) * 100 if follower_count > 0 else 0
    
    async def _find_peak_engagement_time(self, engagement_data: List[Dict]) -> Dict[str, Any]:
        """Find peak engagement time patterns"""
        
        hourly_engagement = {}
        
        for data in engagement_data:
            if 'created_at' in data:
                try:
                    dt = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
                    hour = dt.hour
                    engagement_score = data.get('likes', 0) + data.get('comments', 0)
                    
                    if hour not in hourly_engagement:
                        hourly_engagement[hour] = []
                    hourly_engagement[hour].append(engagement_score)
                except:
                    continue
        
        hourly_avg = {
            hour: statistics.mean(scores) 
            for hour, scores in hourly_engagement.items() 
            if scores
        }
        
        peak_hour = max(hourly_avg.items(), key=lambda x: x[1]) if hourly_avg else (0, 0)
        
        return {
            'peak_hour': peak_hour[0],
            'peak_engagement': peak_hour[1],
            'hourly_distribution': hourly_avg
        }
    
    async def _calculate_volatility(self, values: List[int]) -> float:
        """Calculate engagement volatility"""
        
        if len(values) < 2:
            return 0.0
        
        return statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) > 0 else 0
    
    async def _analyze_content_performance(self, engagement_data: List[Dict]) -> Dict[str, Any]:
        """Analyze content performance metrics"""
        return {"status": "placeholder"}
        
    async def _analyze_audience_behavior(self, engagement_data: List[Dict]) -> Dict[str, Any]:
        """Analyze audience behavior patterns"""
        return {"status": "placeholder"}

class ProfileAnalyzer:
    """Analyze Instagram profile characteristics"""
    
    async def analyze_profile_authenticity(self, profile_data: Dict) -> Dict[str, Any]:
        """Analyze profile authenticity indicators"""
        
        authenticity_score = 0
        indicators = []
        
        if profile_data.get('full_name'):
            authenticity_score += 0.2
            indicators.append('has_full_name')
        
        if profile_data.get('biography'):
            authenticity_score += 0.2
            indicators.append('has_biography')
        
        metadata = profile_data.get('metadata', {})
        followers_str = str(metadata.get('followers', '0')).replace(',', '')
        following_str = str(metadata.get('following', '0')).replace(',', '')
        
        try:
            followers = int(re.sub(r'[^0-9]', '', followers_str))
            following = int(re.sub(r'[^0-9]', '', following_str))
            
            if followers > 0 and following > 0:
                ratio = followers / following
                if 0.5 <= ratio <= 5:
                    authenticity_score += 0.3
                    indicators.append('healthy_follow_ratio')
        except ValueError:
            pass
        
        if metadata.get('is_business', False):
            authenticity_score += 0.15
            indicators.append('business_account')
        
        if profile_data.get('is_verified', False):
            authenticity_score += 0.15
            indicators.append('verified_account')
        
        return {
            'authenticity_score': min(1.0, authenticity_score),
            'indicators': indicators,
            'profile_age_days': await self._estimate_profile_age(profile_data),
            'suspicious_patterns': await self._detect_suspicious_patterns(profile_data)
        }
    
    async def _estimate_profile_age(self, profile_data: Dict) -> int:
        """Estimate profile age based on first post"""
        return 365
    
    async def _detect_suspicious_patterns(self, profile_data: Dict) -> List[str]:
        """Detect suspicious profile patterns"""
        
        suspicious = []
        bio = profile_data.get('biography', '')
        if bio.count('#') > 10:
            suspicious.append('excessive_hashtags_in_bio')
        
        followers = str(profile_data.get('metadata', {}).get('followers', '0'))
        if followers.endswith(('000', '0000')):
            suspicious.append('round_follower_numbers')
        
        return suspicious

class ContentAnalyzer:
    """Analyze Instagram content characteristics"""
    
    async def analyze_content_themes(self, posts_data: List[Dict]) -> Dict[str, Any]:
        """Analyze content themes and topics"""
        
        all_captions = []
        all_hashtags = []
        media_types = []
        
        for post in posts_data:
            if post.get('caption'):
                all_captions.append(post['caption'])
            
            if post.get('metadata', {}).get('tags'):
                all_hashtags.extend(post['metadata']['tags'])
            
            if post.get('metadata', {}).get('is_video'):
                media_types.append('video')
            else:
                media_types.append('photo')
        
        themes = await self._extract_themes(all_captions)
        
        return {
            'content_themes': themes,
            'popular_hashtags': Counter(all_hashtags).most_common(10),
            'media_type_distribution': Counter(media_types),
            'content_sentiment': await self._analyze_sentiment(all_captions),
            'posting_frequency': await self._calculate_posting_frequency(posts_data)
        }
    
    async def _extract_themes(self, captions: List[str]) -> Dict[str, int]:
        """Extract content themes from captions"""
        
        theme_keywords = {
            'news': ['breaking', 'news', 'update', 'report'],
            'lifestyle': ['life', 'style', 'daily', 'routine'],
            'technology': ['tech', 'digital', 'innovation', 'ai'],
            'travel': ['travel', 'vacation', 'explore', 'journey'],
            'food': ['food', 'recipe', 'meal', 'cooking'],
            'fitness': ['fitness', 'workout', 'health', 'exercise'],
            'fashion': ['fashion', 'style', 'outfit', 'trend']
        }
        
        theme_counts = {}
        all_text = ' '.join(captions).lower()
        
        for theme, keywords in theme_keywords.items():
            count = sum(1 for keyword in keywords if keyword in all_text)
            if count > 0:
                theme_counts[theme] = count
        
        return theme_counts
    
    async def _analyze_sentiment(self, captions: List[str]) -> Dict[str, float]:
        """Analyze sentiment of captions"""
        
        positive_words = ['good', 'great', 'amazing', 'awesome', 'love', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry']
        
        positive_count = 0
        negative_count = 0
        total_words = 0
        
        for caption in captions:
            words = caption.lower().split()
            total_words += len(words)
            
            for word in words:
                if word in positive_words:
                    positive_count += 1
                elif word in negative_words:
                    negative_count += 1
        
        if total_words == 0:
            return {'positive': 0, 'negative': 0, 'neutral': 1}
        
        return {
            'positive': positive_count / total_words,
            'negative': negative_count / total_words,
            'neutral': 1 - (positive_count + negative_count) / total_words
        }
    
    async def _calculate_posting_frequency(self, posts_data: List[Dict]) -> Dict[str, Any]:
        """Calculate posting frequency patterns"""
        
        if not posts_data:
            return {}
        
        timestamps = []
        for post in posts_data:
            created_at = post.get('metadata', {}).get('created_at')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    timestamps.append(dt)
                except:
                    continue
        
        if len(timestamps) < 2:
            return {}
        
        timestamps.sort(reverse=True)
        time_diffs = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i-1] - timestamps[i]).total_seconds() / 3600
            time_diffs.append(diff)
        
        return {
            'avg_hours_between_posts': statistics.mean(time_diffs) if time_diffs else 0,
            'posting_consistency': 1 / (statistics.stdev(time_diffs) + 1) if len(time_diffs) > 1 else 1,
            'total_posts_analyzed': len(timestamps),
            'date_range': {
                'first': min(timestamps).isoformat(),
                'last': max(timestamps).isoformat()
            }
        }

class TrendDetector:
    """Detect trends from Instagram content"""
    
    async def detect_emerging_trends(self, hashtag_data: List[Dict], 
                                   timeframe_hours: int = 24) -> List[Dict]:
        """Detect emerging hashtag trends"""
        
        recent_hashtags = []
        cutoff_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
        
        for data in hashtag_data:
            created_at = data.get('metadata', {}).get('created_at')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if dt > cutoff_time:
                        recent_hashtags.append(data)
                except:
                    continue
        
        hashtag_freq = Counter()
        for data in recent_hashtags:
            tags = data.get('metadata', {}).get('tags', [])
            hashtag_freq.update(tags)
        
        trend_scores = {}
        for hashtag, freq in hashtag_freq.items():
            trend_scores[hashtag] = freq * (1 + random.random())
        
        top_trends = sorted(trend_scores.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return [
            {
                'hashtag': tag,
                'trend_score': score,
                'frequency': hashtag_freq[tag],
                'detected_at': datetime.utcnow().isoformat()
            }
            for tag, score in top_trends
        ]
    
    async def analyze_hashtag_networks(self, hashtag_data: List[Dict]) -> Dict[str, Any]:
        """Analyze hashtag co-occurrence networks"""
        
        hashtag_pairs = []
        for data in hashtag_data:
            tags = data.get('metadata', {}).get('tags', [])
            for i in range(len(tags)):
                for j in range(i + 1, len(tags)):
                    pair = tuple(sorted([tags[i], tags[j]]))
                    hashtag_pairs.append(pair)
        
        pair_counts = Counter(hashtag_pairs)
        hashtag_connections = {}
        for (tag1, tag2), count in pair_counts.items():
            if tag1 not in hashtag_connections:
                hashtag_connections[tag1] = []
            if tag2 not in hashtag_connections:
                hashtag_connections[tag2] = []
            hashtag_connections[tag1].append({'connected_to': tag2, 'strength': count})
            hashtag_connections[tag2].append({'connected_to': tag1, 'strength': count})
        
        centrality = {}
        for tag, connections in hashtag_connections.items():
            centrality[tag] = sum(conn['strength'] for conn in connections)
        
        return {
            'network_analysis': {
                'total_connections': len(pair_counts),
                'most_central_hashtags': dict(sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]),
                'strongest_connections': dict(sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:20])
            },
            'community_detection': await self._detect_hashtag_communities(hashtag_connections)
        }
    
    async def _detect_hashtag_communities(self, hashtag_connections: Dict) -> List[Dict]:
        """Detect communities of related hashtags"""
        communities = []
        processed_tags = set()
        
        for tag, connections in hashtag_connections.items():
            if tag in processed_tags:
                continue
            
            community = await self._find_connected_component(tag, hashtag_connections, processed_tags)
            if len(community) > 1:
                communities.append({
                    'tags': list(community),
                    'size': len(community),
                    'central_tags': await self._find_central_tags(community, hashtag_connections),
                    'theme': await self._infer_community_theme(list(community))
                })
        
        return sorted(communities, key=lambda x: x['size'], reverse=True)
    
    async def _find_connected_component(self, start_tag: str, connections: Dict, 
                                      processed_tags: set) -> set:
        """Find all hashtags connected to start_tag"""
        component = set()
        queue = [start_tag]
        
        while queue:
            current_tag = queue.pop(0)
            if current_tag in processed_tags or current_tag in component:
                continue
            
            component.add(current_tag)
            processed_tags.add(current_tag)
            
            tag_connections = connections.get(current_tag, [])
            for conn in tag_connections:
                connected_tag = conn['connected_to']
                if connected_tag not in processed_tags and connected_tag not in component:
                    queue.append(connected_tag)
        
        return component
    
    async def _find_central_tags(self, community: set, connections: Dict) -> List[str]:
        """Find most central tags in community"""
        centrality = {}
        for tag in community:
            tag_connections = connections.get(tag, [])
            internal_connections = [
                conn for conn in tag_connections 
                if conn['connected_to'] in community
            ]
            centrality[tag] = sum(conn['strength'] for conn in internal_connections)
        return [t for t, s in sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    async def _infer_community_theme(self, tags: List[str]) -> str:
        """Infer theme of hashtag community"""
        tag_string = ' '.join(tags).lower()
        theme_keywords = {
            'politics': ['vote', 'election', 'government', 'policy'],
            'news': ['breaking', 'update', 'report', 'live'],
            'technology': ['tech', 'ai', 'digital', 'innovation'],
            'entertainment': ['movie', 'music', 'celebrity', 'show'],
            'sports': ['game', 'team', 'player', 'win'],
            'lifestyle': ['life', 'style', 'daily', 'routine'],
            'business': ['business', 'company', 'market', 'finance'],
            'health': ['health', 'medical', 'doctor', 'wellness'],
            'travel': ['travel', 'vacation', 'destination'],
            'food': ['food', 'recipe', 'cooking', 'restaurant'],
            'education': ['education', 'school', 'learning'],
            'environment': ['climate', 'environment', 'green'],
            'social': ['social', 'community', 'people', 'society']
        }
        theme_scores = {theme: sum(1 for kw in kws if kw in tag_string) for theme, kws in theme_keywords.items()}
        relevant_themes = {t: s for t, s in theme_scores.items() if s > 0}
        return max(relevant_themes.items(), key=lambda x: x[1])[0] if relevant_themes else 'general'
