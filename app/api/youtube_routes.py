"""
YouTube API routes with security and rate limiting
"""

import time
import logging
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    YouTubeVideoRequest, YouTubeSearchRequest, 
    YouTubeChannelRequest, YouTubeCommentsRequest
)
from app.services.youtube_service import YouTubeService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/youtube", tags=["YouTube"])

# Initialize YouTube service
youtube_service = None
if settings.youtube_api_key:
    try:
        youtube_service = YouTubeService(settings.youtube_api_key)
        logger.info("YouTube service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize YouTube service: {e}")


def get_youtube_service():
    """Dependency to get YouTube service"""
    if not youtube_service:
        raise HTTPException(
            status_code=503, 
            detail="YouTube API is not configured. Please set YOUTUBE_API_KEY in environment variables."
        )
    return youtube_service


@router.post("/video-details", summary="Get YouTube video details")
async def get_youtube_video_details(
    request: YouTubeVideoRequest,
    service: YouTubeService = Depends(get_youtube_service)
):
    """Get detailed information about a YouTube video"""
    try:
        video_details = service.get_video_details_by_url(request.video_url)
        
        if not video_details:
            raise HTTPException(status_code=404, detail="Video not found or invalid URL")
        
        logger.info(f"Retrieved video details for: {video_details['title'][:50]}...")
        
        return {
            "status": "success",
            "video_details": video_details,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video details: {e}")
        raise HTTPException(status_code=500, detail="Error fetching video details")


@router.post("/search", summary="Search YouTube videos")
async def search_youtube_videos(
    request: YouTubeSearchRequest,
    service: YouTubeService = Depends(get_youtube_service)
):
    """Search for YouTube videos with content filtering"""
    try:
        videos = service.search_videos(request.query, request.max_results)
        
        logger.info(f"Search completed for '{request.query}': {len(videos)} results")
        
        return {
            "status": "success",
            "query": request.query,
            "results_count": len(videos),
            "videos": videos,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error searching videos: {e}")
        raise HTTPException(status_code=500, detail="Error searching videos")


@router.get("/video/{video_id}", summary="Get video by ID")
async def get_video_by_id(
    video_id: str,
    service: YouTubeService = Depends(get_youtube_service)
):
    """Get YouTube video details by video ID"""
    try:
        video_details = service.get_video_details(video_id)
        
        if not video_details:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "status": "success",
            "video_details": video_details,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video by ID: {e}")
        raise HTTPException(status_code=500, detail="Error fetching video details")


@router.post("/channel-details", summary="Get YouTube channel details")
async def get_youtube_channel_details(
    request: YouTubeChannelRequest,
    service: YouTubeService = Depends(get_youtube_service)
):
    """Get detailed information about a YouTube channel"""
    try:
        channel_details = service.get_channel_details(request.channel_id)
        
        if not channel_details:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        return {
            "status": "success",
            "channel_details": channel_details,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching channel details: {e}")
        raise HTTPException(status_code=500, detail="Error fetching channel details")


@router.post("/recommend-similar", summary="Get similar video recommendations")
async def recommend_similar_youtube_videos(
    request: YouTubeVideoRequest,
    service: YouTubeService = Depends(get_youtube_service)
):
    """Get recommendations based on a YouTube video's content"""
    try:
        # Get video details
        video_details = service.get_video_details_by_url(request.video_url)
        
        if not video_details:
            raise HTTPException(status_code=404, detail="Video not found or invalid URL")
        
        # Create search query from video title and tags
        search_terms = []
        if video_details.get('title'):
            # Take first few words from title
            title_words = video_details['title'].split()[:5]
            search_terms.extend(title_words)
        
        if video_details.get('tags'):
            # Add some tags
            search_terms.extend(video_details['tags'][:3])
        
        search_query = ' '.join(search_terms)
        
        # Search for similar videos
        similar_videos = service.search_videos(search_query, 5)
        
        # Filter out the original video
        original_video_id = video_details['video_id']
        similar_videos = [v for v in similar_videos if v['video_id'] != original_video_id]
        
        logger.info(f"Generated {len(similar_videos)} similar video recommendations")
        
        return {
            "status": "success",
            "based_on_video": {
                "title": video_details['title'],
                "video_id": video_details['video_id']
            },
            "similar_videos": similar_videos[:4],  # Return top 4 similar videos
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendations")


@router.get("/quota-status", summary="Get API quota status")
async def get_quota_status(
    service: YouTubeService = Depends(get_youtube_service)
):
    """Get current YouTube API quota usage status"""
    try:
        quota_status = service.get_quota_status()
        
        return {
            "status": "success",
            "quota_status": quota_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error getting quota status: {e}")
        raise HTTPException(status_code=500, detail="Error getting quota status")
