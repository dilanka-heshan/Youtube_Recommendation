"""
Improved YouTube service with rate limiting, error handling, and ethical considerations
"""

import os
import time
import logging
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from app.core.config import settings
from app.core.security import SecurityUtils

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_period: int = 100, period_seconds: int = 100):
        self.calls_per_period = calls_per_period
        self.period_seconds = period_seconds
        self.calls = []
    
    def is_allowed(self) -> bool:
        """Check if a call is allowed under rate limits"""
        now = time.time()
        
        # Remove old calls outside the current period
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.period_seconds]
        
        # Check if we can make another call
        if len(self.calls) < self.calls_per_period:
            self.calls.append(now)
            return True
        
        return False
    
    def time_until_reset(self) -> int:
        """Get seconds until rate limit resets"""
        if not self.calls:
            return 0
        
        oldest_call = min(self.calls)
        return max(0, int(self.period_seconds - (time.time() - oldest_call)))


class YouTubeService:
    """
    Enhanced YouTube service with security, rate limiting, and ethical considerations
    """
    
    def __init__(self, api_key: str):
        """Initialize YouTube service with rate limiting"""
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Rate limiter based on YouTube API quotas
        self.rate_limiter = RateLimiter(
            calls_per_period=settings.youtube_rate_limit,
            period_seconds=100
        )
        
        # Track quota usage
        self.quota_used = 0
        self.quota_limit = settings.youtube_quota_limit
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        return self.rate_limiter.is_allowed()
    
    def _check_quota(self, cost: int = 1) -> bool:
        """Check if request is within daily quota"""
        return (self.quota_used + cost) <= self.quota_limit
    
    def _update_quota(self, cost: int = 1):
        """Update quota usage"""
        self.quota_used += cost
        logger.info(f"YouTube API quota used: {self.quota_used}/{self.quota_limit}")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL with validation"""
        if not SecurityUtils.validate_youtube_url(url):
            return None
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                # Validate video ID format
                if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    return video_id
        
        return None
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a YouTube video with rate limiting"""
        if not self._check_rate_limit():
            logger.warning("YouTube API rate limit exceeded")
            return None
        
        if not self._check_quota(1):
            logger.warning("YouTube API quota limit exceeded")
            return None
        
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails,status',
                id=video_id
            )
            response = request.execute()
            self._update_quota(1)
            
            if not response['items']:
                logger.info(f"Video not found: {video_id}")
                return None
            
            video = response['items'][0]
            snippet = video['snippet']
            statistics = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            status = video.get('status', {})
            
            # Sanitize and validate data
            result = {
                'video_id': video_id,
                'title': SecurityUtils.sanitize_input(snippet.get('title', ''), 200),
                'description': SecurityUtils.sanitize_input(snippet.get('description', ''), 5000),
                'channel_title': SecurityUtils.sanitize_input(snippet.get('channelTitle', ''), 100),
                'channel_id': snippet.get('channelId', ''),
                'published_at': snippet.get('publishedAt', ''),
                'duration': content_details.get('duration', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'tags': snippet.get('tags', [])[:10],  # Limit tags
                'category_id': snippet.get('categoryId', ''),
                'default_language': snippet.get('defaultLanguage', ''),
                'privacy_status': status.get('privacyStatus', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'embed_html': status.get('embeddable', False)
            }
            
            logger.info(f"Successfully retrieved video details for: {video_id}")
            return result
            
        except HttpError as e:
            logger.error(f"YouTube API HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_video_details: {e}")
            return None
    
    def get_video_details_by_url(self, url: str) -> Optional[Dict]:
        """Get video details using YouTube URL with validation"""
        video_id = self.extract_video_id(url)
        if not video_id:
            logger.warning(f"Invalid YouTube URL: {url}")
            return None
        return self.get_video_details(video_id)
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for YouTube videos with rate limiting and validation"""
        if not self._check_rate_limit():
            logger.warning("YouTube API rate limit exceeded for search")
            return []
        
        if not self._check_quota(100):  # Search costs 100 quota units
            logger.warning("YouTube API quota limit exceeded for search")
            return []
        
        # Limit max_results to prevent abuse
        max_results = min(max_results, 50)
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=SecurityUtils.sanitize_input(query, 500),
                type='video',
                maxResults=max_results,
                order='relevance',
                safeSearch='moderate'  # Filter inappropriate content
            )
            response = request.execute()
            self._update_quota(100)
            
            videos = []
            for item in response['items']:
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                videos.append({
                    'video_id': video_id,
                    'title': SecurityUtils.sanitize_input(snippet.get('title', ''), 200),
                    'description': SecurityUtils.sanitize_input(snippet.get('description', ''), 1000),
                    'channel_title': SecurityUtils.sanitize_input(snippet.get('channelTitle', ''), 100),
                    'published_at': snippet.get('publishedAt', ''),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'url': f'https://www.youtube.com/watch?v={video_id}'
                })
            
            logger.info(f"Successfully searched for: {query}, found {len(videos)} videos")
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API HTTP error in search: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in search_videos: {e}")
            return []
    
    def get_channel_details(self, channel_id: str) -> Optional[Dict]:
        """Get details about a YouTube channel with validation"""
        if not self._check_rate_limit():
            logger.warning("YouTube API rate limit exceeded for channel details")
            return None
        
        if not self._check_quota(1):
            logger.warning("YouTube API quota limit exceeded for channel details")
            return None
        
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=SecurityUtils.sanitize_input(channel_id, 100)
            )
            response = request.execute()
            self._update_quota(1)
            
            if not response['items']:
                logger.info(f"Channel not found: {channel_id}")
                return None
            
            channel = response['items'][0]
            snippet = channel['snippet']
            statistics = channel.get('statistics', {})
            
            result = {
                'channel_id': channel_id,
                'title': SecurityUtils.sanitize_input(snippet.get('title', ''), 100),
                'description': SecurityUtils.sanitize_input(snippet.get('description', ''), 1000),
                'custom_url': snippet.get('customUrl', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0))
            }
            
            logger.info(f"Successfully retrieved channel details for: {channel_id}")
            return result
            
        except HttpError as e:
            logger.error(f"YouTube API HTTP error in channel details: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_channel_details: {e}")
            return None
    
    def get_quota_status(self) -> Dict:
        """Get current quota usage status"""
        return {
            'quota_used': self.quota_used,
            'quota_limit': self.quota_limit,
            'quota_remaining': self.quota_limit - self.quota_used,
            'rate_limit_reset_in': self.rate_limiter.time_until_reset()
        }
