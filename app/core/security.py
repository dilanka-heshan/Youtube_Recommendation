"""
Security utilities for the recommendation system
Implements security best practices and data protection
"""

import hashlib
import secrets
import re
from typing import Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks
        
        Args:
            input_string: Raw input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not input_string:
            return ""
        
        # Limit length
        sanitized = input_string[:max_length]
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';]', '', sanitized)
        
        # Strip whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """
        Validate YouTube URL format
        
        Args:
            url: YouTube URL to validate
            
        Returns:
            True if valid YouTube URL
        """
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            valid_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com']
            
            if parsed.netloc not in valid_domains:
                return False
            
            # Check for video ID pattern
            video_id_pattern = r'[a-zA-Z0-9_-]{11}'
            if 'youtube.com' in parsed.netloc:
                return 'v=' in url and re.search(video_id_pattern, url)
            elif 'youtu.be' in parsed.netloc:
                return re.search(video_id_pattern, parsed.path)
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def hash_user_id(user_id: str) -> str:
        """
        Hash user ID for privacy protection
        
        Args:
            user_id: Original user ID
            
        Returns:
            Hashed user ID
        """
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)


class DataPrivacy:
    """Data privacy and GDPR compliance utilities"""
    
    @staticmethod
    def anonymize_user_data(data: dict) -> dict:
        """
        Anonymize user data for logging and analytics
        
        Args:
            data: User data dictionary
            
        Returns:
            Anonymized data dictionary
        """
        anonymized = data.copy()
        
        # Remove or hash sensitive fields
        sensitive_fields = ['user_id', 'email', 'ip_address']
        
        for field in sensitive_fields:
            if field in anonymized:
                if field == 'user_id':
                    anonymized[field] = SecurityUtils.hash_user_id(anonymized[field])
                else:
                    anonymized[field] = '[REDACTED]'
        
        return anonymized
    
    @staticmethod
    def is_data_expired(timestamp: float, retention_days: int = 30) -> bool:
        """
        Check if user data has exceeded retention period
        
        Args:
            timestamp: Data creation timestamp
            retention_days: Number of days to retain data
            
        Returns:
            True if data should be deleted
        """
        import time
        current_time = time.time()
        retention_seconds = retention_days * 24 * 60 * 60
        
        return (current_time - timestamp) > retention_seconds


class InputValidator:
    """Input validation for API endpoints"""
    
    @staticmethod
    def validate_recommendation_request(user_id: str, num_recommendations: int) -> tuple[bool, str]:
        """
        Validate recommendation request parameters
        
        Args:
            user_id: User identifier
            num_recommendations: Number of recommendations requested
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not user_id or len(user_id.strip()) == 0:
            return False, "User ID is required"
        
        if len(user_id) > 100:
            return False, "User ID too long"
        
        if num_recommendations < 1:
            return False, "Number of recommendations must be positive"
        
        if num_recommendations > 50:  # Reasonable limit
            return False, "Too many recommendations requested (max: 50)"
        
        return True, ""
    
    @staticmethod
    def validate_search_query(query: str) -> tuple[bool, str]:
        """
        Validate search query parameters
        
        Args:
            query: Search query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or len(query.strip()) == 0:
            return False, "Search query is required"
        
        if len(query) > 500:
            return False, "Search query too long (max: 500 characters)"
        
        # Check for potentially malicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'eval\(',
            r'exec\('
        ]
        
        query_lower = query.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, query_lower):
                return False, "Invalid characters in search query"
        
        return True, ""
