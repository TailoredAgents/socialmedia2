"""
Twitter Service Layer
Integration Specialist Component - Service layer for Twitter operations with database integration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import asdict

from backend.integrations.twitter_client import twitter_client, TwitterPost, TwitterThread, TwitterAnalytics
from backend.auth.social_oauth import oauth_manager
from backend.db.models import User, ContentItem, ContentPerformanceSnapshot, UserSetting
from backend.services.similarity_service import similarity_service
from backend.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class TwitterService:
    """
    Twitter service layer with database integration and intelligent content management
    
    Features:
    - Automated posting with performance tracking
    - Thread management and optimization
    - Analytics collection and storage
    - Content repurposing suggestions
    - Engagement monitoring
    - Rate limit management
    """
    
    def __init__(self):
        """Initialize Twitter service"""
        self.platform = "twitter"
        self.max_thread_length = 25  # Twitter's thread limit
        self.optimal_posting_hours = [9, 12, 15, 18, 21]  # Based on general best practices
        
        logger.info("TwitterService initialized")
    
    async def post_content(
        self,
        user_id: int,
        content: str,
        media_files: Optional[List[bytes]] = None,
        media_types: Optional[List[str]] = None,
        alt_texts: Optional[List[str]] = None,
        schedule_for: Optional[datetime] = None,
        is_thread: bool = False,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Post content to Twitter with comprehensive tracking
        
        Args:
            user_id: User ID
            content: Content to post (or thread content)
            media_files: Optional media files
            media_types: Media MIME types
            alt_texts: Alt text for accessibility
            schedule_for: Schedule posting time
            is_thread: Whether content should be posted as thread
            db: Database session
            
        Returns:
            Posting result with tracking information
        """
        try:
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid Twitter connection found")
            
            # Handle media uploads
            media_ids = []
            if media_files and media_types:
                for i, (media_data, media_type) in enumerate(zip(media_files, media_types)):
                    alt_text = alt_texts[i] if alt_texts and i < len(alt_texts) else None
                    media_id = await twitter_client.upload_media(
                        access_token, media_data, media_type, alt_text
                    )
                    media_ids.append(media_id)
            
            # Determine if content should be split into thread
            if is_thread or len(content) > 280:
                thread_content = self._split_into_thread(content)
                result = await self._post_thread(
                    access_token, thread_content, media_ids, user_id, db
                )
            else:
                result = await self._post_single_tweet(
                    access_token, content, media_ids, user_id, db
                )
            
            logger.info(f"Successfully posted Twitter content for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to post Twitter content: {e}")
            raise
    
    async def _post_single_tweet(
        self,
        access_token: str,
        content: str,
        media_ids: List[str],
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Post a single tweet and track it"""
        try:
            # Validate tweet content
            is_valid, error_msg = twitter_client.is_valid_tweet_text(content)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Post tweet
            tweet = await twitter_client.post_tweet(
                access_token=access_token,
                text=content,
                media_ids=media_ids if media_ids else None
            )
            
            # Store in database
            content_item = await self._store_content_item(
                user_id=user_id,
                content=content,
                platform_post_id=tweet.id,
                tweet_data=tweet,
                db=db
            )
            
            # Schedule analytics collection
            await self._schedule_analytics_collection(tweet.id, user_id, db)
            
            return {
                "status": "success",
                "type": "single_tweet",
                "tweet_id": tweet.id,
                "content_item_id": content_item.id,
                "tweet_url": f"https://twitter.com/i/web/status/{tweet.id}",
                "posted_at": tweet.created_at.isoformat(),
                "metrics": asdict(tweet.public_metrics) if hasattr(tweet, 'public_metrics') else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to post single tweet: {e}")
            raise
    
    async def _post_thread(
        self,
        access_token: str,
        thread_content: List[str],
        media_ids: List[str],
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Post a Twitter thread and track it"""
        try:
            # Distribute media across thread tweets
            media_per_tweet = self._distribute_media_across_thread(media_ids, len(thread_content))
            
            # Post thread
            thread = await twitter_client.post_thread(
                access_token=access_token,
                tweets=thread_content,
                media_per_tweet=media_per_tweet
            )
            
            # Store thread tweets in database
            content_items = []
            for i, tweet in enumerate(thread.tweets):
                content_item = await self._store_content_item(
                    user_id=user_id,
                    content=tweet.text,
                    platform_post_id=tweet.id,
                    tweet_data=tweet,
                    parent_content_id=thread.thread_id if i > 0 else None,
                    db=db
                )
                content_items.append(content_item)
                
                # Schedule analytics for each tweet
                await self._schedule_analytics_collection(tweet.id, user_id, db)
            
            return {
                "status": "success",
                "type": "thread",
                "thread_id": thread.thread_id,
                "tweet_count": thread.total_tweets,
                "content_item_ids": [item.id for item in content_items],
                "thread_url": f"https://twitter.com/i/web/status/{thread.thread_id}",
                "posted_at": thread.created_at.isoformat(),
                "tweets": [
                    {
                        "tweet_id": tweet.id,
                        "content": tweet.text,
                        "position": i + 1
                    }
                    for i, tweet in enumerate(thread.tweets)
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to post thread: {e}")
            raise
    
    def _split_into_thread(self, content: str, max_length: int = 270) -> List[str]:
        """
        Split long content into thread-appropriate chunks
        
        Args:
            content: Long content to split
            max_length: Maximum characters per tweet
            
        Returns:
            List of tweet texts
        """
        if len(content) <= max_length:
            return [content]
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        tweets = []
        current_tweet = ""
        
        for paragraph in paragraphs:
            # If paragraph fits in current tweet
            if len(current_tweet + paragraph) <= max_length:
                current_tweet += paragraph + '\n\n'
            else:
                # Finish current tweet if it has content
                if current_tweet.strip():
                    tweets.append(current_tweet.strip())
                    current_tweet = ""
                
                # If paragraph is too long, split by sentences
                if len(paragraph) > max_length:
                    sentences = paragraph.split('. ')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        
                        # Add period if not present
                        if not sentence.endswith('.') and not sentence.endswith('!') and not sentence.endswith('?'):
                            sentence += '.'
                        
                        if len(current_tweet + sentence) <= max_length:
                            current_tweet += sentence + ' '
                        else:
                            if current_tweet.strip():
                                tweets.append(current_tweet.strip())
                            current_tweet = sentence + ' '
                else:
                    current_tweet = paragraph + '\n\n'
        
        # Add remaining content
        if current_tweet.strip():
            tweets.append(current_tweet.strip())
        
        # Limit thread length
        if len(tweets) > self.max_thread_length:
            tweets = tweets[:self.max_thread_length]
            tweets[-1] += " [cont'd...]"
        
        # Add thread numbering
        if len(tweets) > 1:
            for i in range(len(tweets)):
                tweets[i] = f"{i+1}/{len(tweets)} {tweets[i]}"
        
        return tweets
    
    def _distribute_media_across_thread(self, media_ids: List[str], tweet_count: int) -> List[List[str]]:
        """Distribute media IDs across thread tweets"""
        if not media_ids:
            return [[] for _ in range(tweet_count)]
        
        media_per_tweet = [[] for _ in range(tweet_count)]
        
        # Put media in first tweet by default, distribute if many media files
        if len(media_ids) <= 4:  # Twitter's media limit per tweet
            media_per_tweet[0] = media_ids
        else:
            # Distribute across multiple tweets
            media_per_chunk = 4
            for i, media_id in enumerate(media_ids):
                tweet_index = min(i // media_per_chunk, tweet_count - 1)
                if len(media_per_tweet[tweet_index]) < 4:
                    media_per_tweet[tweet_index].append(media_id)
        
        return media_per_tweet
    
    async def _store_content_item(
        self,
        user_id: int,
        content: str,
        platform_post_id: str,
        tweet_data: TwitterPost,
        parent_content_id: Optional[str] = None,
        db: Session = None
    ) -> ContentItem:
        """Store content item in database with Twitter-specific data"""
        try:
            # Extract hashtags and mentions
            hashtags = twitter_client.extract_hashtags(content)
            mentions = twitter_client.extract_mentions(content)
            
            # Create content item
            content_item = ContentItem(
                user_id=user_id,
                content=content,
                platform=self.platform,
                content_type="text",
                status="published",
                platform_post_id=platform_post_id,
                platform_url=f"https://twitter.com/i/web/status/{platform_post_id}",
                published_at=tweet_data.created_at,
                hashtags=hashtags,
                mentions=mentions,
                parent_content_id=parent_content_id
            )
            
            # Add initial metrics
            if hasattr(tweet_data, 'public_metrics') and tweet_data.public_metrics:
                content_item.likes_count = tweet_data.public_metrics.get('like_count', 0)
                content_item.shares_count = tweet_data.public_metrics.get('retweet_count', 0)
                content_item.comments_count = tweet_data.public_metrics.get('reply_count', 0)
                content_item.reach_count = tweet_data.public_metrics.get('impression_count', 0)
            
            if db:
                db.add(content_item)
                db.commit()
                db.refresh(content_item)
            
            logger.info(f"Stored Twitter content item {content_item.id}")
            return content_item
            
        except Exception as e:
            if db:
                db.rollback()
            logger.error(f"Failed to store content item: {e}")
            raise
    
    async def _schedule_analytics_collection(self, tweet_id: str, user_id: int, db: Session):
        """Schedule analytics collection for a tweet"""
        # This would typically integrate with a task queue like Celery
        # For now, we'll collect analytics immediately
        try:
            await asyncio.sleep(5)  # Brief delay to allow Twitter to process
            await self.collect_tweet_analytics(user_id, tweet_id, db)
        except Exception as e:
            logger.error(f"Failed to schedule analytics collection: {e}")
    
    async def collect_tweet_analytics(
        self,
        user_id: int,
        tweet_id: str,
        db: Session
    ) -> TwitterAnalytics:
        """
        Collect and store analytics for a specific tweet
        
        Args:
            user_id: User ID
            tweet_id: Tweet ID
            db: Database session
            
        Returns:
            Analytics data
        """
        try:
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid Twitter connection found")
            
            # Get analytics from Twitter
            analytics = await twitter_client.get_tweet_analytics(access_token, tweet_id)
            
            # Update content item with latest metrics
            content_item = db.query(ContentItem).filter(
                ContentItem.platform_post_id == tweet_id,
                ContentItem.user_id == user_id
            ).first()
            
            if content_item:
                content_item.likes_count = analytics.likes
                content_item.shares_count = analytics.retweets
                content_item.comments_count = analytics.replies
                content_item.reach_count = analytics.impressions
                content_item.engagement_rate = analytics.engagement_rate
                content_item.last_performance_update = datetime.utcnow()
                
                # Update performance tier based on engagement
                content_item.performance_tier = self._calculate_performance_tier(analytics.engagement_rate)
                
                # Create performance snapshot
                snapshot = ContentPerformanceSnapshot(
                    content_item_id=content_item.id,
                    likes_count=analytics.likes,
                    shares_count=analytics.retweets,
                    comments_count=analytics.replies,
                    reach_count=analytics.impressions,
                    engagement_rate=analytics.engagement_rate,
                    platform_metrics={
                        "bookmarks": analytics.bookmarks,
                        "quotes": analytics.quotes,
                        "url_clicks": analytics.url_clicks,
                        "profile_clicks": analytics.profile_clicks
                    }
                )
                
                db.add(snapshot)
                db.commit()
            
            logger.info(f"Collected analytics for tweet {tweet_id}")
            return analytics
            
        except Exception as e:
            if db:
                db.rollback()
            logger.error(f"Failed to collect tweet analytics: {e}")
            raise
    
    def _calculate_performance_tier(self, engagement_rate: float) -> str:
        """Calculate performance tier based on engagement rate"""
        if engagement_rate >= 10.0:
            return "viral"
        elif engagement_rate >= 5.0:
            return "high"
        elif engagement_rate >= 2.0:
            return "medium"
        elif engagement_rate >= 0.5:
            return "low"
        else:
            return "poor"
    
    async def get_content_suggestions(
        self,
        user_id: int,
        topic: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get Twitter-specific content suggestions
        
        Args:
            user_id: User ID
            topic: Content topic
            db: Database session
            
        Returns:
            Content suggestions with Twitter-specific optimizations
        """
        try:
            # Get recommendations from similarity service
            recommendations = await similarity_service.get_content_recommendations(
                topic=topic,
                target_platform=self.platform,
                db=db
            )
            
            # Add Twitter-specific enhancements
            twitter_suggestions = []
            
            for rec in recommendations:
                # Optimize content for Twitter
                optimized_suggestions = []
                for suggestion in rec.content_suggestions:
                    # Check if content needs to be threaded
                    is_thread = len(suggestion.content) > 280
                    thread_preview = None
                    
                    if is_thread:
                        thread_content = self._split_into_thread(suggestion.content)
                        thread_preview = {
                            "tweet_count": len(thread_content),
                            "preview": thread_content[0] if thread_content else ""
                        }
                    
                    optimized_suggestions.append({
                        **suggestion.__dict__,
                        "is_thread": is_thread,
                        "thread_preview": thread_preview,
                        "hashtags": twitter_client.extract_hashtags(suggestion.content),
                        "mentions": twitter_client.extract_mentions(suggestion.content),
                        "character_count": len(suggestion.content)
                    })
                
                twitter_suggestions.append({
                    **rec.__dict__,
                    "content_suggestions": optimized_suggestions,
                    "twitter_specific": {
                        "optimal_posting_times": self.optimal_posting_hours,
                        "trending_hashtags": await self._get_trending_hashtags(user_id, db),
                        "thread_recommendations": self._get_thread_recommendations(topic)
                    }
                })
            
            return {
                "status": "success",
                "topic": topic,
                "platform": self.platform,
                "suggestions": twitter_suggestions
            }
            
        except Exception as e:
            logger.error(f"Failed to get Twitter content suggestions: {e}")
            raise
    
    async def _get_trending_hashtags(self, user_id: int, db: Session) -> List[str]:
        """Get trending hashtags (simplified implementation)"""
        # In a real implementation, this would use Twitter's trending API
        # For now, return general trending hashtags
        return ["#AI", "#Tech", "#Innovation", "#Productivity", "#Business"]
    
    def _get_thread_recommendations(self, topic: str) -> Dict[str, Any]:
        """Get thread-specific recommendations"""
        return {
            "suggested_structure": [
                "Hook/attention grabber",
                "Main insight or story",
                "Supporting details",
                "Call to action or conclusion"
            ],
            "optimal_length": "5-10 tweets",
            "engagement_tips": [
                "Start with a compelling hook",
                "Use numbered lists for clarity",
                "Include a call to action",
                "Ask questions to encourage replies"
            ]
        }
    
    async def get_user_timeline(
        self,
        user_id: int,
        limit: int = 20,
        include_analytics: bool = True,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get user's Twitter timeline with analytics
        
        Args:
            user_id: User ID
            limit: Number of tweets to return
            include_analytics: Include analytics data
            db: Database session
            
        Returns:
            Timeline data with analytics
        """
        try:
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid Twitter connection found")
            
            # Get user profile to get user ID
            profile = await twitter_client.get_user_profile(access_token)
            twitter_user_id = profile.get("id")
            
            if not twitter_user_id:
                raise Exception("Failed to get Twitter user ID")
            
            # Get user tweets
            tweets = await twitter_client.get_user_tweets(
                access_token=access_token,
                user_id=twitter_user_id,
                max_results=limit
            )
            
            # Enhance with analytics if requested
            enhanced_tweets = []
            for tweet in tweets:
                tweet_data = {
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat(),
                    "public_metrics": tweet.public_metrics,
                    "hashtags": twitter_client.extract_hashtags(tweet.text),
                    "mentions": twitter_client.extract_mentions(tweet.text),
                    "url": f"https://twitter.com/i/web/status/{tweet.id}"
                }
                
                if include_analytics:
                    try:
                        analytics = await twitter_client.get_tweet_analytics(access_token, tweet.id)
                        tweet_data["analytics"] = {
                            "engagement_rate": analytics.engagement_rate,
                            "impressions": analytics.impressions,
                            "url_clicks": analytics.url_clicks,
                            "profile_clicks": analytics.profile_clicks
                        }
                    except Exception as e:
                        logger.warning(f"Failed to get analytics for tweet {tweet.id}: {e}")
                        tweet_data["analytics"] = None
                
                enhanced_tweets.append(tweet_data)
            
            return {
                "status": "success",
                "user_id": user_id,
                "twitter_user_id": twitter_user_id,
                "tweets": enhanced_tweets,
                "total_tweets": len(enhanced_tweets),
                "include_analytics": include_analytics
            }
            
        except Exception as e:
            logger.error(f"Failed to get user timeline: {e}")
            raise
    
    async def delete_content(
        self,
        user_id: int,
        content_item_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Delete Twitter content
        
        Args:
            user_id: User ID
            content_item_id: Content item ID
            db: Database session
            
        Returns:
            Deletion result
        """
        try:
            # Get content item
            content_item = db.query(ContentItem).filter(
                ContentItem.id == content_item_id,
                ContentItem.user_id == user_id,
                ContentItem.platform == self.platform
            ).first()
            
            if not content_item:
                raise Exception("Content item not found")
            
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid Twitter connection found")
            
            # Delete from Twitter
            success = await twitter_client.delete_tweet(access_token, content_item.platform_post_id)
            
            if success:
                # Update database
                content_item.status = "deleted"
                db.commit()
                
                logger.info(f"Deleted Twitter content {content_item_id}")
                
                return {
                    "status": "success",
                    "content_item_id": content_item_id,
                    "tweet_id": content_item.platform_post_id,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            else:
                raise Exception("Failed to delete tweet from Twitter")
            
        except Exception as e:
            if db:
                db.rollback()
            logger.error(f"Failed to delete Twitter content: {e}")
            raise

# Global Twitter service instance
twitter_service = TwitterService()