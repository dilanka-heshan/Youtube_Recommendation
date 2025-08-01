"""
Recommendation service with ethical considerations and bias mitigation
"""

import logging
import time
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings
from app.core.security import DataPrivacy

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Ethical recommendation service with bias mitigation and transparency
    """
    
    def __init__(self):
        self.user_interactions = {}  # Store user interaction history
        self.content_cache = {}  # Cache for content-based recommendations
        self.diversity_factor = 0.2  # Factor to promote diversity
    
    def get_content_based_recommendations(
        self, 
        items_df: pd.DataFrame, 
        item_id: Optional[str] = None, 
        num_recommendations: int = 5,
        diversify: bool = True
    ) -> pd.DataFrame:
        """
        Generate content-based recommendations with diversity promotion
        
        Args:
            items_df: DataFrame containing items
            item_id: Optional base item for similarity
            num_recommendations: Number of recommendations
            diversify: Whether to promote diversity in recommendations
            
        Returns:
            DataFrame with recommendations
        """
        try:
            # Ensure we don't exceed limits
            num_recommendations = min(num_recommendations, settings.max_recommendations)
            
            # Combine title and description for content analysis
            items_df['content'] = items_df['title'] + ' ' + items_df['description']
            
            # Create TF-IDF vectors
            tfidf = TfidfVectorizer(
                stop_words='english',
                max_features=1000,  # Limit features for performance
                ngram_range=(1, 2)  # Include bigrams for better context
            )
            tfidf_matrix = tfidf.fit_transform(items_df['content'])
            
            # Calculate cosine similarity
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            
            if item_id:
                # Find similar items to the given item
                try:
                    idx = items_df[items_df['item_id'] == item_id].index[0]
                    sim_scores = list(enumerate(cosine_sim[idx]))
                    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                    
                    # Exclude the item itself
                    sim_scores = sim_scores[1:num_recommendations+1]
                    
                    if diversify:
                        # Promote diversity by selecting from different categories
                        sim_scores = self._diversify_recommendations(
                            sim_scores, items_df, num_recommendations
                        )
                    
                    item_indices = [i[0] for i in sim_scores]
                    recommendations = items_df.iloc[item_indices]
                    
                except (IndexError, KeyError):
                    logger.warning(f"Item not found: {item_id}")
                    recommendations = self._get_default_recommendations(items_df, num_recommendations)
            else:
                # Return diverse top-rated items
                recommendations = self._get_default_recommendations(items_df, num_recommendations)
            
            # Add recommendation scores and explanations
            recommendations = self._add_recommendation_metadata(recommendations, item_id)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in content-based recommendations: {e}")
            return self._get_fallback_recommendations(items_df, num_recommendations)
    
    def _diversify_recommendations(
        self, 
        sim_scores: List[tuple], 
        items_df: pd.DataFrame, 
        num_recommendations: int
    ) -> List[tuple]:
        """
        Promote diversity in recommendations by category
        
        Args:
            sim_scores: List of similarity scores
            items_df: Items DataFrame
            num_recommendations: Target number of recommendations
            
        Returns:
            Diversified list of similarity scores
        """
        try:
            diversified = []
            used_categories = set()
            
            # First pass: select from different categories
            for score_tuple in sim_scores:
                if len(diversified) >= num_recommendations:
                    break
                
                idx = score_tuple[0]
                category = items_df.iloc[idx]['category']
                
                if category not in used_categories:
                    diversified.append(score_tuple)
                    used_categories.add(category)
            
            # Second pass: fill remaining slots with highest scores
            for score_tuple in sim_scores:
                if len(diversified) >= num_recommendations:
                    break
                
                if score_tuple not in diversified:
                    diversified.append(score_tuple)
            
            return diversified[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error in diversification: {e}")
            return sim_scores[:num_recommendations]
    
    def _get_default_recommendations(
        self, 
        items_df: pd.DataFrame, 
        num_recommendations: int
    ) -> pd.DataFrame:
        """
        Get default recommendations (top-rated with diversity)
        
        Args:
            items_df: Items DataFrame
            num_recommendations: Number of recommendations
            
        Returns:
            DataFrame with default recommendations
        """
        try:
            # Sort by rating and promote diversity
            sorted_items = items_df.sort_values(['rating'], ascending=False)
            
            # Select diverse items by category
            recommendations = []
            used_categories = set()
            
            # First pass: one item per category
            for _, item in sorted_items.iterrows():
                if len(recommendations) >= num_recommendations:
                    break
                
                if item['category'] not in used_categories:
                    recommendations.append(item)
                    used_categories.add(item['category'])
            
            # Second pass: fill remaining slots
            for _, item in sorted_items.iterrows():
                if len(recommendations) >= num_recommendations:
                    break
                
                if not any(rec['item_id'] == item['item_id'] for rec in recommendations):
                    recommendations.append(item)
            
            return pd.DataFrame(recommendations[:num_recommendations])
            
        except Exception as e:
            logger.error(f"Error in default recommendations: {e}")
            return items_df.nlargest(num_recommendations, 'rating')
    
    def _get_fallback_recommendations(
        self, 
        items_df: pd.DataFrame, 
        num_recommendations: int
    ) -> pd.DataFrame:
        """
        Fallback recommendations in case of errors
        
        Args:
            items_df: Items DataFrame
            num_recommendations: Number of recommendations
            
        Returns:
            Simple fallback recommendations
        """
        try:
            return items_df.head(num_recommendations)
        except Exception:
            return pd.DataFrame()
    
    def _add_recommendation_metadata(
        self, 
        recommendations: pd.DataFrame, 
        base_item_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Add metadata to recommendations for transparency
        
        Args:
            recommendations: Recommendations DataFrame
            base_item_id: Base item ID for explanation
            
        Returns:
            DataFrame with added metadata
        """
        try:
            recommendations = recommendations.copy()
            
            # Add recommendation reason
            if base_item_id:
                recommendations['recommendation_reason'] = f"Similar to item {base_item_id}"
            else:
                recommendations['recommendation_reason'] = "Top-rated content"
            
            # Add timestamp
            recommendations['recommended_at'] = time.time()
            
            # Add confidence score (simplified)
            recommendations['confidence'] = np.random.uniform(0.7, 0.95, len(recommendations))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error adding metadata: {e}")
            return recommendations
    
    def track_user_interaction(
        self, 
        user_id: str, 
        item_id: str, 
        interaction_type: str,
        anonymize: bool = True
    ):
        """
        Track user interactions for improving recommendations
        
        Args:
            user_id: User identifier
            item_id: Item identifier
            interaction_type: Type of interaction (view, like, etc.)
            anonymize: Whether to anonymize user data
        """
        try:
            # Anonymize user ID for privacy
            if anonymize:
                user_id = DataPrivacy.anonymize_user_data({'user_id': user_id})['user_id']
            
            if user_id not in self.user_interactions:
                self.user_interactions[user_id] = []
            
            interaction = {
                'item_id': item_id,
                'interaction_type': interaction_type,
                'timestamp': time.time()
            }
            
            self.user_interactions[user_id].append(interaction)
            
            # Keep only recent interactions (privacy)
            retention_time = settings.data_retention_days * 24 * 60 * 60
            current_time = time.time()
            
            self.user_interactions[user_id] = [
                interaction for interaction in self.user_interactions[user_id]
                if current_time - interaction['timestamp'] < retention_time
            ]
            
            logger.info(f"Tracked interaction: {interaction_type} for user {user_id[:8]}...")
            
        except Exception as e:
            logger.error(f"Error tracking user interaction: {e}")
    
    def get_personalized_recommendations(
        self, 
        user_id: str, 
        items_df: pd.DataFrame, 
        num_recommendations: int = 5
    ) -> pd.DataFrame:
        """
        Get personalized recommendations based on user history
        
        Args:
            user_id: User identifier
            items_df: Available items
            num_recommendations: Number of recommendations
            
        Returns:
            Personalized recommendations
        """
        try:
            # Anonymize user ID for lookup
            anon_user_id = DataPrivacy.anonymize_user_data({'user_id': user_id})['user_id']
            
            if anon_user_id not in self.user_interactions:
                # No history, return default recommendations
                return self._get_default_recommendations(items_df, num_recommendations)
            
            # Get user's interaction history
            user_history = self.user_interactions[anon_user_id]
            
            # Find categories user has interacted with
            interacted_items = [interaction['item_id'] for interaction in user_history]
            user_categories = items_df[items_df['item_id'].isin(interacted_items)]['category'].unique()
            
            # Prefer items from user's preferred categories
            preferred_items = items_df[items_df['category'].isin(user_categories)]
            
            if len(preferred_items) >= num_recommendations:
                recommendations = preferred_items.nlargest(num_recommendations, 'rating')
            else:
                # Mix preferred and general recommendations
                preferred_count = len(preferred_items)
                general_count = num_recommendations - preferred_count
                
                general_items = items_df[~items_df['category'].isin(user_categories)]
                general_recs = general_items.nlargest(general_count, 'rating')
                
                recommendations = pd.concat([preferred_items, general_recs])
            
            return self._add_recommendation_metadata(recommendations, None)
            
        except Exception as e:
            logger.error(f"Error in personalized recommendations: {e}")
            return self._get_default_recommendations(items_df, num_recommendations)
