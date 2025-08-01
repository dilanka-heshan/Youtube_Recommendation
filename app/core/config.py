"""
Configuration settings for the Recommendation System API
Following security best practices and ethical guidelines
"""

import os
from typing import Optional
from pydantic import validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation and security measures"""
    
    # API Configuration
    api_title: str = "Recommendation System API"
    api_description: str = "A secure and ethical recommendation system with YouTube integration"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "127.0.0.1"  # More secure default than 0.0.0.0
    port: int = 8000
    
    # Security Settings
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Settings - Restrict origins in production
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # YouTube API Configuration
    youtube_api_key: Optional[str] = None
    youtube_quota_limit: int = 10000  # Daily quota limit
    youtube_rate_limit: int = 100  # Requests per 100 seconds

    #Supabase Configuration
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Recommendation Settings
    max_recommendations: int = 20  # Limit to prevent abuse
    default_recommendations: int = 5
    
    # Data Privacy Settings
    data_retention_days: int = 30  # How long to keep user data
    anonymize_logs: bool = True
    
    @validator('youtube_api_key')
    def validate_youtube_api_key(cls, v):
        """Ensure YouTube API key is properly configured"""
        if v and v == "your_youtube_api_key_here":
            return None
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Ensure secret key is changed from default"""
        if v == "change-this-in-production":
            print("WARNING: Using default secret key. Change this in production!")
        return v
    
    @validator('supabase_url')
    def validate_supabase_url(cls, v):
        """Ensure Supabase URL is provided"""
        if not v:
            print("WARNING: Supabase URL is not set. Please configure it in the environment.")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "default": "100/minute",
    "youtube_api": "10/minute",  # More conservative for external API
    "recommendations": "20/minute"
}
