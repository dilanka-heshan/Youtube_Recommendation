"""
Core API routes with security and rate limiting
"""

import time
import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import (
    RecommendationRequest, RecommendationResponse, 
    UserPreferences, HealthResponse
)
from app.services.recommendation_service import RecommendationService
from app.core.config import settings
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize recommendation service
recommendation_service = RecommendationService()

# Sample data (in production, use a database)
SAMPLE_ITEMS = [
    {
        "item_id": "1",
        "title": "Python Programming Guide",
        "description": "Complete guide to Python programming with examples",
        "category": "Programming",
        "rating": 4.5
    },
    {
        "item_id": "2", 
        "title": "Data Science Handbook",
        "description": "Essential data science techniques and algorithms",
        "category": "Data Science",
        "rating": 4.8
    },
    {
        "item_id": "3",
        "title": "Machine Learning Basics",
        "description": "Introduction to machine learning concepts",
        "category": "Machine Learning",
        "rating": 4.3
    },
    {
        "item_id": "4",
        "title": "Web Development with FastAPI",
        "description": "Build modern web APIs with FastAPI framework",
        "category": "Web Development",
        "rating": 4.6
    },
    {
        "item_id": "5",
        "title": "Data Visualization Techniques",
        "description": "Advanced data visualization with Python libraries",
        "category": "Data Science",
        "rating": 4.4
    },
    {
        "item_id": "6",
        "title": "Cybersecurity Fundamentals",
        "description": "Essential cybersecurity concepts and practices",
        "category": "Security",
        "rating": 4.7
    }
]

user_preferences = {}


@router.get("/", summary="Root endpoint")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the Ethical Recommendation System API",
        "version": settings.api_version,
        "features": [
            "Content-based recommendations",
            "YouTube integration",
            "Privacy protection",
            "Bias mitigation",
            "Rate limiting"
        ]
    }


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Comprehensive health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="recommendation-system",
        youtube_api="configured" if settings.youtube_api_key else "not configured",
        version=settings.api_version,
        timestamp=time.time()
    )


@router.get("/items", summary="Get all items")
async def get_all_items():
    """Get all available items with metadata"""
    return {
        "items": SAMPLE_ITEMS,
        "total_count": len(SAMPLE_ITEMS),
        "categories": list(set(item["category"] for item in SAMPLE_ITEMS))
    }


@router.get("/items/{item_id}", summary="Get specific item")
async def get_item(item_id: str):
    """Get a specific item by ID"""
    item = next((item for item in SAMPLE_ITEMS if item["item_id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/user/preferences", summary="Set user preferences")
async def set_user_preferences(preferences: UserPreferences):
    """Set user preferences with validation"""
    try:
        user_preferences[preferences.user_id] = {
            "categories": preferences.categories,
            "keywords": preferences.keywords,
            "updated_at": time.time()
        }
        
        logger.info(f"Preferences set for user: {preferences.user_id[:8]}...")
        
        return {
            "message": f"Preferences set successfully",
            "user_id": preferences.user_id,
            "categories_count": len(preferences.categories),
            "keywords_count": len(preferences.keywords)
        }
        
    except Exception as e:
        logger.error(f"Error setting user preferences: {e}")
        raise HTTPException(status_code=500, detail="Error setting preferences")


@router.get("/user/{user_id}/preferences", summary="Get user preferences")
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    if user_id not in user_preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    return user_preferences[user_id]


@router.post("/recommendations", response_model=RecommendationResponse, summary="Get recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Get recommendations with ethical considerations"""
    try:
        # Convert sample items to DataFrame
        items_df = pd.DataFrame(SAMPLE_ITEMS)
        
        # Get recommendations using the service
        if request.item_id:
            recommendations_df = recommendation_service.get_content_based_recommendations(
                items_df, 
                request.item_id, 
                request.num_recommendations,
                diversify=True
            )
        else:
            recommendations_df = recommendation_service.get_personalized_recommendations(
                request.user_id,
                items_df,
                request.num_recommendations
            )
        
        # Convert to list of dictionaries
        recommendations = recommendations_df.to_dict('records')
        
        # Track user interaction for learning
        recommendation_service.track_user_interaction(
            request.user_id, 
            request.item_id or "general", 
            "recommendation_request"
        )
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {request.user_id[:8]}...")
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=recommendations,
            status="success",
            timestamp=time.time(),
            total_count=len(recommendations)
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendations")


@router.get("/categories", summary="Get all categories")
async def get_categories():
    """Get all available categories"""
    categories = list(set(item["category"] for item in SAMPLE_ITEMS))
    return {
        "categories": categories,
        "total_count": len(categories)
    }


@router.get("/items/category/{category}", summary="Get items by category")
async def get_items_by_category(category: str):
    """Get items by category"""
    filtered_items = [item for item in SAMPLE_ITEMS 
                     if item["category"].lower() == category.lower()]
    
    if not filtered_items:
        raise HTTPException(status_code=404, detail="No items found for this category")
    
    return {
        "category": category,
        "items": filtered_items,
        "total_count": len(filtered_items)
    }


@router.post("/recommendations/feedback", summary="Provide recommendation feedback")
async def recommendation_feedback(
    user_id: str,
    item_id: str,
    feedback_type: str,  # "like", "dislike", "clicked", "ignored"
    rating: float = None
):
    """
    Collect user feedback on recommendations for improving the system
    """
    try:
        # Validate feedback type
        valid_feedback = ["like", "dislike", "clicked", "ignored", "rated"]
        if feedback_type not in valid_feedback:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid feedback type. Must be one of: {valid_feedback}"
            )
        
        # Track the feedback
        recommendation_service.track_user_interaction(
            user_id, 
            item_id, 
            f"feedback_{feedback_type}"
        )
        
        logger.info(f"Received feedback: {feedback_type} from user {user_id[:8]}... for item {item_id}")
        
        return {
            "message": "Feedback recorded successfully",
            "feedback_type": feedback_type,
            "item_id": item_id
        }
        
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail="Error recording feedback")
