""" Supabase databse service for Youtube recommendation system"""

import logging
import time
from typing import Dict, List , Optional , Any
from supabase import create_client, Client
from app.core.config import Settings
from app.core.security import SecurityUtils, DataPrivacy

logger = logging.getLogger(__name__)

class DatabaseService:
    """Supabase database service with YouTube schema support"""

    def __init__(self):
        """Initialize the Supabase client"""
        try:
            self.supabase: Client = create_client(
                Settings.supabase_url,
                Settings.supabase_key
            )
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase = None

    def _check_connection(self) -> bool:
        """Check if the Supabase client is connected"""
        return self.supabase is not None
    
    #chanel operations
    async def get_all_channels(self) -> List[Dict]:
        """Get all channels from the database"""
        if not self._check_connection():
            raise Exception("Supabase client is not initialized")
        
        try:
            response = self.supabase.table("channels").select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch channels: {e}")
            return []
        
    async def get_channel_by_id(self, channel_id: str) -> Optional[Dict]:
        """Get a channel by its ID"""
        if not self._check_connection():
            raise Exception("Supabase client is not initialized")
        
        try:
            reponse = self.supabase.table("channels").select("*").eq("id", channel_id).execute()
        except Exception as e:
            logger.error(f"Failed to fetch channel by ID {channel_id}: {e}")
            return None
        
    async def create_channel(self, channel_data:Dict) -> Optional[Dict]:
        """Create a new channel in the database"""
        if not self._check_connection():
            raise Exception("Supabase client is not initialized")

        try:
            sanitized_data = {
                "id": SecurityUtils.sanitize_input(channel_data.get("id", ""),100),
                "title": SecurityUtils.sanitize_input(channel_data.get("title", ""), 100),
                "description": SecurityUtils.sanitize_input(channel_data.get("description", ""), 500),
                "published_at": channel_data.get("published_at"),
                "subscriber_count": channel_data.get("subscriber_count", 0),
                "view_count": channel_data.get("view_count", 0),
                "video_count": channel_data.get("video_count", 0),
                "thumbnail_url": SecurityUtils.sanitize_input(channel_data.get("thumbnail_url", ""), 200),
            }

            response = self.supabase.table("channels").insert(sanitized_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to create channel: {e}")
            return None
        
    #video Operations
    async def get_all_videos(self, limit:int = 100) -> List[Dict]:
        """Get all videos from the database"""
        if not self._check_connection():
            raise Exception("Supabase client is not initialized")

        try:
            response = (
                self.supabase.table("videos")
                .select("*")
                .limit(limit)
                .order("published_at", desc=True)
                .execute()
                )
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch videos: {e}")
            return []
        
    async def get_video_by_id(self, video_id: str) -> Optional[Dict]:
        """Get a video by its ID"""
        if not self._check_connection():
            raise Exception("Supabase client is not initialized")
        
        try:
            response = (
                self.supabase.table("videos")
                .select("* , channels(title , subscriber_count)")
                .eq("id", video_id)
                .execute()
                )
            return response.data[0] if response.data else None
        
        except Exception as e:
            logger.error(f"Failed to fetch video by ID {video_id}: {e}")
            return None
        
    async def get_video_by_channel(self, channel_id: str, limit: int = 50) -> List[Dict]:
        """Get videos by channel """
        if not self._check_connection():
            raise Exception("Supabase client is not initialized")
    
        try:
            response = (
                self.supabase.table("videos")
                .select("*")
                .eq("channel_id", channel_id)
                .limit(limit)
                .order("published_at", desc=True)
                .execute()
            )
            return response.data
    
        except Exception as e:
            logger.error(f"Failed to fetch videos by channel ID {channel_id}: {e}")
            return []
    
    async def create_video(self, video_data: Dict) -> Optional[Dict]:
        """Create new video"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            sanitized_data = {
                "id": SecurityUtils.sanitize_input(video_data.get("id", ""), 100),
                "title": SecurityUtils.sanitize_input(video_data.get("title", ""), 300),
                "description": SecurityUtils.sanitize_input(video_data.get("description", ""), 5000),
                "tags": video_data.get("tags", []),
                "published_at": video_data.get("published_at"),
                "thumbnail_url": SecurityUtils.sanitize_input(video_data.get("thumbnail_url", ""), 500),
                "channel_id": SecurityUtils.sanitize_input(video_data.get("channel_id", ""), 100),
                "embedding_id": video_data.get("embedding_id")
            }
            
            response = self.supabase.table("videos").insert(sanitized_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None
    

    async def search_videos_by_tags(self, tags: List[str], limit: int = 20) -> List[Dict]:
        """Search videos by tags"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            # Use array overlap operator for tag search
            response = (
                self.supabase.table("videos")
                .select("*, channels(title)")
                .filter("tags", "ov", tags)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error searching videos by tags: {e}")
            return []
        

    #User Operations
    async def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Create new user"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            sanitized_data = {
                "email": SecurityUtils.sanitize_input(user_data.get("email", ""), 255),
                "preferences": user_data.get("preferences", {}),
                "embedding_id": user_data.get("embedding_id")
            }
            
            response = self.supabase.table("users").insert(sanitized_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
        
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            response = self.supabase.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
        
    async def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user preferences"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            response = (
                self.supabase.table("users")
                .update({"preferences": preferences})
                .eq("id", user_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    #interaction operations
    async def track_interaction(self, user_id: str, video_id: str, interaction_type: str) -> bool:
        """Track user interaction with video"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            valid_types = ["watch", "like", "share", "click"]
            if interaction_type not in valid_types:
                raise ValueError(f"Invalid interaction type. Must be one of: {valid_types}")
            
            interaction_data = {
                "user_id": user_id,
                "video_id": SecurityUtils.sanitize_input(video_id, 100),
                "type": interaction_type
            }
            
            response = self.supabase.table("interactions").insert(interaction_data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error tracking interaction: {e}")
            return False
    
    async def get_user_interactions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user interaction history"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            response = (
                self.supabase.table("interactions")
                .select("*, videos(title, channel_id)")
                .eq("user_id", user_id)
                .order("timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error fetching user interactions: {e}")
            return []
        
    async def get_video_interactions(self, video_id: str) -> List[Dict]:
        """Get all interactions for a video"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            response = (
                self.supabase.table("interactions")
                .select("*")
                .eq("video_id", video_id)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error fetching video interactions: {e}")
            return []
        
    #Newsletter Operations
async def create_newsletter(self, user_id: str, video_ids: List[str]) -> Optional[str]:
    """Create a newsletter with multiple videos"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        # Create newsletter record
        newsletter_data = {
            "user_id": user_id
        }
        
        newsletter_response = self.supabase.table("newsletters").insert(newsletter_data).execute()
        
        if not newsletter_response.data:
            return None
            
        newsletter_id = newsletter_response.data[0]["id"]
        
        # Create newsletter_videos records
        newsletter_videos = []
        for video_id in video_ids:
            newsletter_videos.append({
                "newsletter_id": newsletter_id,
                "video_id": SecurityUtils.sanitize_input(video_id, 100)
            })
        
        if newsletter_videos:
            self.supabase.table("newsletter_videos").insert(newsletter_videos).execute()
        
        logger.info(f"Newsletter created with {len(video_ids)} videos for user {user_id}")
        return newsletter_id
        
    except Exception as e:
        logger.error(f"Error creating newsletter: {e}")
        return None

async def log_newsletter_send(self, user_id: str, video_ids: List[str]) -> Optional[str]:
    """Log newsletter send with multiple videos"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        return await self.create_newsletter(user_id, video_ids)
    except Exception as e:
        logger.error(f"Error logging newsletter send: {e}")
        return None
    
async def mark_newsletter_video_clicked(self, newsletter_id: str, video_id: str) -> bool:
    """Mark specific video in newsletter as clicked"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        response = (
            self.supabase.table("newsletter_videos")
            .update({"clicked": True})
            .eq("newsletter_id", newsletter_id)
            .eq("video_id", video_id)
            .execute()
        )
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"Error marking newsletter video clicked: {e}")
        return False
    
async def mark_newsletter_video_clicked_by_user(self, user_id: str, video_id: str) -> bool:
    """Mark video as clicked in user's most recent newsletter"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        # Find the most recent newsletter for this user containing this video
        response = (
            self.supabase.table("newsletter_videos")
            .select("id, newsletter_id, newsletters!inner(user_id, sent_at)")
            .eq("video_id", video_id)
            .eq("newsletters.user_id", user_id)
            .order("newsletters.sent_at", desc=True)
            .limit(1)
            .execute()
        )
        
        if not response.data:
            return False
            
        newsletter_video_id = response.data[0]["id"]
        
        # Mark as clicked
        update_response = (
            self.supabase.table("newsletter_videos")
            .update({"clicked": True})
            .eq("id", newsletter_video_id)
            .execute()
       )
        
        return len(update_response.data) > 0
        
    except Exception as e:
        logger.error(f"Error marking newsletter video clicked by user: {e}")
        return False

async def get_newsletter_by_id(self, newsletter_id: str) -> Optional[Dict]:
    """Get newsletter with all its videos"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        # Get newsletter info
        newsletter_response = (
            self.supabase.table("newsletters")
            .select("*, users(email)")
            .eq("id", newsletter_id)
            .execute()
        )
        
        if not newsletter_response.data:
            return None
            
        newsletter = newsletter_response.data[0]
        
        # Get newsletter videos
        videos_response = (
            self.supabase.table("newsletter_videos")
            .select("*, videos(id, title, thumbnail_url, channels(title))")
            .eq("newsletter_id", newsletter_id)
            .execute()
        )
        
        newsletter["videos"] = videos_response.data
        return newsletter
        
    except Exception as e:
        logger.error(f"Error fetching newsletter: {e}")
        return None

async def get_user_newsletters(self, user_id: str, limit: int = 20) -> List[Dict]:
    """Get user's newsletters with video details"""
    if not self._check_connection():
        raise Exception("Database connection not available")

    try:
        # Get newsletters
        newsletters_response = (
            self.supabase.table("newsletters")
            .select("*")
            .eq("user_id", user_id)
            .order("sent_at", desc=True)
            .limit(limit)
            .execute()
        )
        
        newsletters = newsletters_response.data
        
        # Get videos for each newsletter
        for newsletter in newsletters:
            videos_response = (
                self.supabase.table("newsletter_videos")
                .select("*, videos(id, title, thumbnail_url)")
                .eq("newsletter_id", newsletter["id"])
                .execute()
            )
            newsletter["videos"] = videos_response.data
            
        return newsletters
    
    except Exception as e:
        logger.error(f"Error fetching user newsletters: {e}")
        return []
    
async def get_newsletter_stats(self, user_id: str) -> Dict:
    """Get comprehensive newsletter statistics for user"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        # Get all newsletters for user
        newsletters_response = (
            self.supabase.table("newsletters")
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )
        
        newsletter_ids = [n["id"] for n in newsletters_response.data]
        
        if not newsletter_ids:
            return {
                "total_newsletters": 0,
                "total_videos_sent": 0,
                "total_videos_clicked": 0,
                "click_rate": 0,
                "newsletters_with_clicks": 0
            }
        
        # Get all newsletter videos
        videos_response = (
            self.supabase.table("newsletter_videos")
            .select("clicked, newsletter_id")
            .in_("newsletter_id", newsletter_ids)
            .execute()
        )
        
        videos = videos_response.data
        total_videos = len(videos)
        total_clicked = sum(1 for v in videos if v.get("clicked", False))
        
        # Count newsletters with at least one click
        newsletters_with_clicks = len(set(
            v["newsletter_id"] for v in videos if v.get("clicked", False)
        ))
        
        return {
            "total_newsletters": len(newsletter_ids),
            "total_videos_sent": total_videos,
            "total_videos_clicked": total_clicked,
            "click_rate": (total_clicked / total_videos * 100) if total_videos > 0 else 0,
            "newsletters_with_clicks": newsletters_with_clicks
        }
        
    except Exception as e:
        logger.error(f"Error fetching newsletter stats: {e}")
        return {
            "total_newsletters": 0,
            "total_videos_sent": 0,
            "total_videos_clicked": 0,
            "click_rate": 0,
            "newsletters_with_clicks": 0
        }

async def get_newsletter_performance(self, newsletter_id: str) -> Dict:
    """Get performance metrics for a specific newsletter"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        # Get newsletter videos with click status
        response = (
            self.supabase.table("newsletter_videos")
            .select("clicked, videos(title)")
            .eq("newsletter_id", newsletter_id)
            .execute()
        )
        
        videos = response.data
        total_videos = len(videos)
        clicked_videos = sum(1 for v in videos if v.get("clicked", False))
        
        # Get video performance details
        video_performance = []
        for video in videos:
            video_performance.append({
                "title": video.get("videos", {}).get("title", "Unknown"),
                "clicked": video.get("clicked", False)
            })
        
        return {
            "newsletter_id": newsletter_id,
            "total_videos": total_videos,
            "clicked_videos": clicked_videos,
           "click_rate": (clicked_videos / total_videos * 100) if total_videos > 0 else 0,
            "video_performance": video_performance
        }
        
    except Exception as e:
        logger.error(f"Error fetching newsletter performance: {e}")
        return {}
    
async def get_most_clicked_videos_in_newsletters(self, limit: int = 10) -> List[Dict]:
    """Get videos that are most clicked in newsletters"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        # Use raw SQL for this complex query
        response = self.supabase.rpc("get_most_clicked_newsletter_videos", {"limit_count": limit}).execute()
        
        if response.data:
            return response.data
        
        # Fallback method if RPC doesn't exist
        response = (
            self.supabase.table("newsletter_videos")
            .select("video_id, videos(title, channels(title)), clicked")
            .eq("clicked", True)
            .execute()
        )
        
        # Count clicks per video
        video_clicks = {}
        for item in response.data:
            video_id = item["video_id"]
            video_clicks[video_id] = video_clicks.get(video_id, 0) + 1
        
        # Sort by click count
        sorted_videos = sorted(video_clicks.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        # Get video details
        # Get video details
        result = []
        for video_id, click_count in sorted_videos:
            video_response = (
                self.supabase.table("videos")
                .select("title, channels(title)")
                .eq("id", video_id)
                .execute()
            )
            
            if video_response.data:
                video = video_response.data[0]
                result.append({
                    "video_id": video_id,
                    "title": video["title"],
                    "channel_title": video.get("channels", {}).get("title", "Unknown"),
                    "newsletter_clicks": click_count
                })
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching most clicked newsletter videos: {e}")
        return []
    
    #feedback operation
async def save_feedback(self, user_id: str, video_id: str, rating: int) -> bool:
        """Save user feedback for video"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            if rating < -1 or rating > 5:
                raise ValueError("Rating must be between -1 and 5")
            
            feedback_data = {
                "user_id": user_id,
                "video_id": SecurityUtils.sanitize_input(video_id, 100),
                "rating": rating
            }
            
            # Check if feedback already exists
            existing = (
                self.supabase.table("feedback")
                .select("id")
                .eq("user_id", user_id)
                .eq("video_id", video_id)
                .execute()
            )
            
            if existing.data:
                # Update existing feedback
                response = (
                    self.supabase.table("feedback")
                    .update({"rating": rating})
                   .eq("user_id", user_id)
                    .eq("video_id", video_id)
                    .execute()
                )
            else:
                # Insert new feedback
                response = self.supabase.table("feedback").insert(feedback_data).execute()
            
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False
        
async def get_video_feedback(self, video_id: str) -> Dict:
        """Get aggregated feedback for video"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            response = (
                self.supabase.table("feedback")
                .select("rating")
                .eq("video_id", video_id)
                .execute()
            )
            
            ratings = [f["rating"] for f in response.data]
            if not ratings:
                return {"average_rating": 0, "total_ratings": 0}
            
            return {
                "average_rating": sum(ratings) / len(ratings),
                "total_ratings": len(ratings),
                "rating_distribution": {
                    "5": ratings.count(5),
                    "4": ratings.count(4),
                    "3": ratings.count(3),
                    "2": ratings.count(2),
                    "1": ratings.count(1),
                    "0": ratings.count(0),
                    "-1": ratings.count(-1)
                }
            }
        except Exception as e:
            logger.error(f"Error fetching video feedback: {e}")
            return {"average_rating": 0, "total_ratings": 0}
        
async def get_user_preferred_channels(self, user_id: str) -> List[str]:
        """Get channels user has interacted with most"""
        if not self._check_connection():
            raise Exception("Database connection not available")
        
        try:
            response = (
                self.supabase.table("interactions")
                .select("videos(channel_id)")
                .eq("user_id", user_id)
                .execute()
            )
            
            # Count channel interactions
            channel_counts = {}
            for interaction in response.data:
                if interaction.get("videos") and interaction["videos"].get("channel_id"):
                    channel_id = interaction["videos"]["channel_id"]
                    channel_counts[channel_id] = channel_counts.get(channel_id, 0) + 1
            
            # Return top channels
            return sorted(channel_counts.keys(), key=lambda x: channel_counts[x], reverse=True)[:10]
            
        except Exception as e:
            logger.error(f"Error fetching user preferred channels: {e}")
            return []


async def get_trending_tags(self, limit: int = 20, user_id: str = None) -> List[Dict]:
    """Get trending tags from recent videos, personalized based on user's watch history"""
    if not self._check_connection():
        raise Exception("Database connection not available")
    
    try:
        # Get all tags from recent videos (last 30 days)
        response = (
            self.supabase.table("videos")
            .select("tags, id")
            .gte("published_at", "now() - interval '30 days'")
            .execute()
        )
        
        # Count tag frequency globally
        global_tag_counts = {}
        video_tags_map = {}  # Map video_id to its tags
        
        for video in response.data:
            video_id = video.get("id")
            tags = video.get("tags", [])
            video_tags_map[video_id] = tags
            
            for tag in tags:
                global_tag_counts[tag] = global_tag_counts.get(tag, 0) + 1
        
        # If no user_id provided, return global trending tags
        if not user_id:
            trending = sorted(global_tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            return [{"tag": tag, "count": count, "relevance_score": 0, "user_interaction": 0} for tag, count in trending]
        
        # Get user's interaction history
        user_interactions = await self.get_user_interactions(user_id, limit=200)
        user_watched_videos = [interaction.get("video_id") for interaction in user_interactions if interaction.get("type") in ["watch", "click"]]
        
        # Get user's preferences
        user_prefs = await self.get_user_by_id(user_id)
        user_preferred_tags = []
        if user_prefs and user_prefs.get("preferences"):
            user_preferred_tags = user_prefs["preferences"].get("preferred_tags", [])
        
        # Calculate user's tag preferences from watch history
        user_tag_counts = {}
        user_tag_interactions = {}
        
        for video_id in user_watched_videos:
            if video_id in video_tags_map:
                for tag in video_tags_map[video_id]:
                    user_tag_counts[tag] = user_tag_counts.get(tag, 0) + 1
                    user_tag_interactions[tag] = user_tag_interactions.get(tag, 0) + 1
        
        # Calculate personalized relevance scores
        personalized_tags = {}
        
        for tag, global_count in global_tag_counts.items():
            # Base score from global popularity
            popularity_score = global_count
            
            # User interaction bonus
            user_interaction_count = user_tag_counts.get(tag, 0)
            interaction_bonus = user_interaction_count * 2  # Weight user interactions higher
            
            # User preference bonus
            preference_bonus = 5 if tag.lower() in [t.lower() for t in user_preferred_tags] else 0
            
            # Related tags bonus (tags that appear with user's preferred tags)
            related_bonus = 0
            if user_tag_counts:
                # Calculate how often this tag appears with user's watched tags
                for user_tag in user_tag_counts.keys():
                    if user_tag != tag:
                        # Check co-occurrence in videos
                        co_occurrence = self._calculate_tag_co_occurrence(tag, user_tag, video_tags_map)
                        related_bonus += co_occurrence * 0.5
            
            # Novelty factor - slightly prefer tags user hasn't seen much
            novelty_factor = 1.0
            if user_interaction_count > 0:
                novelty_factor = max(0.5, 1.0 - (user_interaction_count / 10))  # Diminish for overexposed tags
            
            # Calculate final relevance score
            relevance_score = (
                popularity_score * 0.4 +  # 40% global popularity
                interaction_bonus * 0.3 +  # 30% user interaction history
                preference_bonus * 0.2 +   # 20% explicit preferences
                related_bonus * 0.1        # 10% related tags
            ) * novelty_factor
            
            personalized_tags[tag] = {
                "tag": tag,
                "count": global_count,
                "user_interaction": user_interaction_count,
                "relevance_score": round(relevance_score, 2),
                "popularity_score": popularity_score,
                "interaction_bonus": interaction_bonus,
                "preference_bonus": preference_bonus,
                "related_bonus": round(related_bonus, 2),
                "novelty_factor": round(novelty_factor, 2)
            }
        
        # Sort by relevance score and return top tags
        trending = sorted(
            personalized_tags.values(), 
            key=lambda x: x["relevance_score"], 
            reverse=True
        )[:limit]
        
        # Add ranking information
        for i, tag_info in enumerate(trending):
            tag_info["rank"] = i + 1
            tag_info["is_preferred"] = tag_info["tag"].lower() in [t.lower() for t in user_preferred_tags]
            tag_info["is_familiar"] = tag_info["user_interaction"] > 0
        
        logger.info(f"Generated {len(trending)} personalized trending tags for user {user_id}")
        return trending
        
    except Exception as e:
        logger.error(f"Error fetching personalized trending tags: {e}")
        # Fallback to global trending tags
        try:
            response = (
                self.supabase.table("videos")
                .select("tags")
                .gte("published_at", "now() - interval '30 days'")
                .execute()
            )
            
            tag_counts = {}
            for video in response.data:
                if video.get("tags"):
                    for tag in video["tags"]:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            trending = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            return [{"tag": tag, "count": count, "relevance_score": 0, "user_interaction": 0} for tag, count in trending]
        except:
            return []

# Global database service instance
db_service = DatabaseService()