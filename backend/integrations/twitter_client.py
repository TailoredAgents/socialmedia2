"""
Twitter API v2 Integration Client
Integration Specialist Component - Complete Twitter API v2 integration with posting and analytics
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import json
import httpx
from dataclasses import dataclass

from backend.core.config import get_settings
from backend.auth.social_oauth import oauth_manager

settings = get_settings()
logger = logging.getLogger(__name__)

@dataclass
class TwitterPost:
    """Twitter post data structure"""
    id: str
    text: str
    author_id: str
    created_at: datetime
    public_metrics: Dict[str, int]
    context_annotations: List[Dict[str, Any]]
    attachments: Optional[Dict[str, Any]] = None
    referenced_tweets: Optional[List[Dict[str, Any]]] = None

@dataclass
class TwitterThread:
    """Twitter thread data structure"""
    thread_id: str
    tweets: List[TwitterPost]
    total_tweets: int
    created_at: datetime
    last_updated: datetime

@dataclass
class TwitterAnalytics:
    """Twitter analytics data structure"""
    tweet_id: str
    impressions: int
    retweets: int
    likes: int
    replies: int
    quotes: int
    bookmarks: int
    engagement_rate: float
    url_clicks: int
    profile_clicks: int
    fetched_at: datetime

class TwitterAPIClient:
    """
    Twitter API v2 Client with comprehensive posting and analytics capabilities
    
    Features:
    - Tweet posting with media support
    - Thread creation and management
    - Analytics data retrieval
    - User timeline management  
    - Rate limit handling and optimization
    - Real-time engagement tracking
    """
    
    def __init__(self):
        """Initialize Twitter API client"""
        self.api_base = "https://api.twitter.com/2"
        self.upload_base = "https://upload.twitter.com/1.1"
        
        # API endpoints
        self.endpoints = {
            "tweet": "/tweets",
            "user_tweets": "/users/{user_id}/tweets",
            "me": "/users/me",
            "tweet_lookup": "/tweets/{tweet_id}",
            "user_lookup": "/users/by/username/{username}",
            "media_upload": "/media/upload.json",
            "spaces": "/spaces/search",
            "lists": "/lists"
        }
        
        # Rate limiting configuration
        self.rate_limits = {
            "tweet_create": {"requests": 300, "window": 900},  # 300 per 15 min
            "tweet_lookup": {"requests": 300, "window": 900},
            "user_lookup": {"requests": 300, "window": 900},
            "user_tweets": {"requests": 900, "window": 900},
            "media_upload": {"requests": 300, "window": 900}
        }
        
        # Supported media types
        self.supported_media_types = {
            "image": ["jpg", "jpeg", "png", "gif", "webp"],
            "video": ["mp4", "mov"],
            "gif": ["gif"]
        }
        
        logger.info("TwitterAPIClient initialized with v2 API support")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        use_upload_base: bool = False
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Twitter API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            access_token: OAuth access token
            data: Request data
            params: Query parameters
            files: File uploads
            use_upload_base: Use upload API base URL
            
        Returns:
            API response data
        """
        base_url = self.upload_base if use_upload_base else self.api_base
        url = f"{base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "AI-Social-Media-Agent/1.0"
        }
        
        # Add Content-Type for JSON requests
        if data and not files:
            headers["Content-Type"] = "application/json"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    if files:
                        response = await client.post(url, headers=headers, data=data, files=files)
                    elif data:
                        response = await client.post(url, headers=headers, json=data)
                    else:
                        response = await client.post(url, headers=headers, params=params)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=headers, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle rate limiting
                if response.status_code == 429:
                    reset_time = response.headers.get("x-rate-limit-reset")
                    if reset_time:
                        wait_time = int(reset_time) - int(datetime.utcnow().timestamp())
                        logger.warning(f"Rate limited. Waiting {wait_time}s")
                        await asyncio.sleep(max(wait_time, 60))
                        # Retry once after rate limit
                        return await self._make_request(method, endpoint, access_token, data, params, files, use_upload_base)
                
                # Handle API errors
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    logger.error(f"Twitter API error {response.status_code}: {error_data}")
                    raise Exception(f"Twitter API error: {error_data.get('detail', response.text)}")
                
                return response.json()
                
            except httpx.RequestError as e:
                logger.error(f"HTTP request error: {e}")
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                logger.error(f"API request failed: {e}")
                raise
    
    async def get_user_profile(self, access_token: str, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user profile information
        
        Args:
            access_token: OAuth access token
            username: Username to lookup (if None, gets authenticated user)
            
        Returns:
            User profile data
        """
        if username:
            endpoint = self.endpoints["user_lookup"].format(username=username)
        else:
            endpoint = self.endpoints["me"]
        
        params = {
            "user.fields": "id,name,username,description,public_metrics,profile_image_url,verified,created_at"
        }
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        if username:
            return response.get("data", {})
        else:
            return response.get("data", {})
    
    async def post_tweet(
        self,
        access_token: str,
        text: str,
        media_ids: Optional[List[str]] = None,
        reply_to_tweet_id: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        poll_options: Optional[List[str]] = None,
        poll_duration_minutes: int = 1440
    ) -> TwitterPost:
        """
        Post a new tweet
        
        Args:
            access_token: OAuth access token
            text: Tweet text (max 280 characters)
            media_ids: List of uploaded media IDs
            reply_to_tweet_id: ID of tweet to reply to
            quote_tweet_id: ID of tweet to quote
            poll_options: Poll options (2-4 options)
            poll_duration_minutes: Poll duration in minutes
            
        Returns:
            Posted tweet data
        """
        if len(text) > 280:
            raise ValueError("Tweet text exceeds 280 characters")
        
        tweet_data = {"text": text}
        
        # Add media attachments
        if media_ids:
            tweet_data["media"] = {"media_ids": media_ids}
        
        # Add reply reference
        if reply_to_tweet_id:
            tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}
        
        # Add quote tweet reference
        if quote_tweet_id:
            tweet_data["quote_tweet_id"] = quote_tweet_id
        
        # Add poll
        if poll_options and len(poll_options) >= 2:
            tweet_data["poll"] = {
                "options": poll_options[:4],  # Max 4 options
                "duration_minutes": min(poll_duration_minutes, 10080)  # Max 7 days
            }
        
        response = await self._make_request("POST", self.endpoints["tweet"], access_token, data=tweet_data)
        
        tweet_info = response.get("data", {})
        
        # Create TwitterPost object
        return TwitterPost(
            id=tweet_info.get("id"),
            text=tweet_info.get("text"),
            author_id=tweet_info.get("author_id"),
            created_at=datetime.fromisoformat(tweet_info.get("created_at", "").replace("Z", "+00:00")),
            public_metrics=tweet_info.get("public_metrics", {}),
            context_annotations=tweet_info.get("context_annotations", []),
            attachments=tweet_info.get("attachments"),
            referenced_tweets=tweet_info.get("referenced_tweets")
        )
    
    async def post_thread(
        self,
        access_token: str,
        tweets: List[str],
        media_per_tweet: Optional[List[List[str]]] = None
    ) -> TwitterThread:
        """
        Post a Twitter thread
        
        Args:
            access_token: OAuth access token
            tweets: List of tweet texts
            media_per_tweet: List of media IDs for each tweet
            
        Returns:
            Thread information
        """
        if not tweets:
            raise ValueError("Thread must contain at least one tweet")
        
        posted_tweets = []
        previous_tweet_id = None
        
        # Ensure media_per_tweet matches tweets length
        if media_per_tweet and len(media_per_tweet) != len(tweets):
            raise ValueError("media_per_tweet must match tweets length")
        
        try:
            for i, tweet_text in enumerate(tweets):
                # Get media IDs for this tweet
                media_ids = media_per_tweet[i] if media_per_tweet else None
                
                # Post tweet (reply to previous if not first)
                tweet = await self.post_tweet(
                    access_token=access_token,
                    text=tweet_text,
                    media_ids=media_ids,
                    reply_to_tweet_id=previous_tweet_id
                )
                
                posted_tweets.append(tweet)
                previous_tweet_id = tweet.id
                
                # Add delay between tweets to avoid rate limiting
                if i < len(tweets) - 1:
                    await asyncio.sleep(1)
            
            # Create thread object
            thread = TwitterThread(
                thread_id=posted_tweets[0].id,  # First tweet ID as thread ID
                tweets=posted_tweets,
                total_tweets=len(posted_tweets),
                created_at=posted_tweets[0].created_at,
                last_updated=posted_tweets[-1].created_at
            )
            
            logger.info(f"Successfully posted Twitter thread with {len(posted_tweets)} tweets")
            
            return thread
            
        except Exception as e:
            logger.error(f"Failed to post Twitter thread: {e}")
            # If we've posted some tweets, try to delete them
            if posted_tweets:
                await self._cleanup_failed_thread(access_token, posted_tweets)
            raise
    
    async def _cleanup_failed_thread(self, access_token: str, posted_tweets: List[TwitterPost]):
        """Clean up partially posted thread"""
        logger.warning(f"Cleaning up {len(posted_tweets)} tweets from failed thread")
        
        for tweet in reversed(posted_tweets):  # Delete in reverse order
            try:
                await self.delete_tweet(access_token, tweet.id)
                await asyncio.sleep(0.5)  # Brief delay between deletions
            except Exception as e:
                logger.error(f"Failed to delete tweet {tweet.id} during cleanup: {e}")
    
    async def delete_tweet(self, access_token: str, tweet_id: str) -> bool:
        """
        Delete a tweet
        
        Args:
            access_token: OAuth access token
            tweet_id: ID of tweet to delete
            
        Returns:
            Success status
        """
        endpoint = f"/tweets/{tweet_id}"
        
        try:
            response = await self._make_request("DELETE", endpoint, access_token)
            deleted = response.get("data", {}).get("deleted", False)
            
            if deleted:
                logger.info(f"Successfully deleted tweet {tweet_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete tweet {tweet_id}: {e}")
            return False
    
    async def upload_media(
        self,
        access_token: str,
        media_data: bytes,
        media_type: str,
        alt_text: Optional[str] = None
    ) -> str:
        """
        Upload media to Twitter
        
        Args:
            access_token: OAuth access token
            media_data: Binary media data
            media_type: Media MIME type
            alt_text: Alternative text for accessibility
            
        Returns:
            Media ID string
        """
        # Determine media category
        if media_type.startswith("image/"):
            media_category = "tweet_image"
        elif media_type.startswith("video/"):
            media_category = "tweet_video"
        else:
            raise ValueError(f"Unsupported media type: {media_type}")
        
        # Upload media
        upload_data = {
            "command": "INIT",
            "media_type": media_type,
            "total_bytes": len(media_data),
            "media_category": media_category
        }
        
        # Initialize upload
        init_response = await self._make_request(
            "POST",
            self.endpoints["media_upload"],
            access_token,
            data=upload_data,
            use_upload_base=True
        )
        
        media_id = init_response.get("media_id_string")
        if not media_id:
            raise Exception("Failed to initialize media upload")
        
        # Upload media data in chunks
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        for i in range(0, len(media_data), chunk_size):
            chunk = media_data[i:i + chunk_size]
            
            chunk_data = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": i // chunk_size
            }
            
            files = {"media": ("media", chunk, media_type)}
            
            await self._make_request(
                "POST",
                self.endpoints["media_upload"],
                access_token,
                data=chunk_data,
                files=files,
                use_upload_base=True
            )
        
        # Finalize upload
        finalize_data = {
            "command": "FINALIZE",
            "media_id": media_id
        }
        
        finalize_response = await self._make_request(
            "POST",
            self.endpoints["media_upload"],
            access_token,
            data=finalize_data,
            use_upload_base=True
        )
        
        # Check processing status for videos
        processing_info = finalize_response.get("processing_info")
        if processing_info:
            await self._wait_for_media_processing(access_token, media_id)
        
        # Add alt text if provided
        if alt_text:
            await self._add_media_alt_text(access_token, media_id, alt_text)
        
        logger.info(f"Successfully uploaded media with ID: {media_id}")
        
        return media_id
    
    async def _wait_for_media_processing(self, access_token: str, media_id: str):
        """Wait for media processing to complete"""
        max_wait_time = 300  # 5 minutes max
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < max_wait_time:
            status_data = {
                "command": "STATUS",
                "media_id": media_id
            }
            
            status_response = await self._make_request(
                "GET",
                self.endpoints["media_upload"],
                access_token,
                params=status_data,
                use_upload_base=True
            )
            
            processing_info = status_response.get("processing_info", {})
            state = processing_info.get("state")
            
            if state == "succeeded":
                logger.info(f"Media processing completed for {media_id}")
                return
            elif state == "failed":
                error = processing_info.get("error", {})
                raise Exception(f"Media processing failed: {error}")
            
            # Wait before checking again
            check_after = processing_info.get("check_after_secs", 5)
            await asyncio.sleep(check_after)
        
        raise Exception("Media processing timeout")
    
    async def _add_media_alt_text(self, access_token: str, media_id: str, alt_text: str):
        """Add alternative text to uploaded media"""
        alt_data = {
            "media_id": media_id,
            "alt_text": {"text": alt_text[:1000]}  # Max 1000 characters
        }
        
        await self._make_request(
            "POST",
            "/media/metadata/create.json",
            access_token,
            data=alt_data,
            use_upload_base=True
        )
    
    async def get_tweet_analytics(
        self,
        access_token: str,
        tweet_id: str,
        include_organic_metrics: bool = True,
        include_promoted_metrics: bool = False
    ) -> TwitterAnalytics:
        """
        Get analytics for a specific tweet
        
        Args:
            access_token: OAuth access token
            tweet_id: Tweet ID
            include_organic_metrics: Include organic engagement metrics
            include_promoted_metrics: Include promoted metrics
            
        Returns:
            Tweet analytics data
        """
        endpoint = self.endpoints["tweet_lookup"].format(tweet_id=tweet_id)
        
        params = {
            "tweet.fields": "public_metrics,organic_metrics,promoted_metrics,created_at",
            "expansions": "author_id"
        }
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        tweet_data = response.get("data", {})
        public_metrics = tweet_data.get("public_metrics", {})
        organic_metrics = tweet_data.get("organic_metrics", {}) if include_organic_metrics else {}
        promoted_metrics = tweet_data.get("promoted_metrics", {}) if include_promoted_metrics else {}
        
        # Calculate engagement rate
        impressions = organic_metrics.get("impression_count") or public_metrics.get("impression_count", 1)
        engagements = (
            public_metrics.get("retweet_count", 0) +
            public_metrics.get("like_count", 0) +
            public_metrics.get("reply_count", 0) +
            public_metrics.get("quote_count", 0)
        )
        engagement_rate = (engagements / impressions * 100) if impressions > 0 else 0
        
        return TwitterAnalytics(
            tweet_id=tweet_id,
            impressions=impressions,
            retweets=public_metrics.get("retweet_count", 0),
            likes=public_metrics.get("like_count", 0),
            replies=public_metrics.get("reply_count", 0),
            quotes=public_metrics.get("quote_count", 0),
            bookmarks=public_metrics.get("bookmark_count", 0),
            engagement_rate=engagement_rate,
            url_clicks=organic_metrics.get("url_link_clicks", 0),
            profile_clicks=organic_metrics.get("user_profile_clicks", 0),
            fetched_at=datetime.utcnow()
        )
    
    async def get_user_tweets(
        self,
        access_token: str,
        user_id: str,
        max_results: int = 10,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
        include_retweets: bool = False
    ) -> List[TwitterPost]:
        """
        Get tweets from a user's timeline
        
        Args:
            access_token: OAuth access token
            user_id: User ID
            max_results: Maximum tweets to return (5-100)
            since_date: Only tweets after this date
            until_date: Only tweets before this date
            include_retweets: Include retweets
            
        Returns:
            List of tweets
        """
        endpoint = self.endpoints["user_tweets"].format(user_id=user_id)
        
        params = {
            "max_results": min(max(max_results, 5), 100),
            "tweet.fields": "id,text,author_id,created_at,public_metrics,context_annotations,attachments,referenced_tweets",
            "exclude": [] if include_retweets else ["retweets"]
        }
        
        if since_date:
            params["start_time"] = since_date.isoformat()
        if until_date:
            params["end_time"] = until_date.isoformat()
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        tweets_data = response.get("data", [])
        tweets = []
        
        for tweet_data in tweets_data:
            tweet = TwitterPost(
                id=tweet_data.get("id"),
                text=tweet_data.get("text"),
                author_id=tweet_data.get("author_id"),
                created_at=datetime.fromisoformat(tweet_data.get("created_at", "").replace("Z", "+00:00")),
                public_metrics=tweet_data.get("public_metrics", {}),
                context_annotations=tweet_data.get("context_annotations", []),
                attachments=tweet_data.get("attachments"),
                referenced_tweets=tweet_data.get("referenced_tweets")
            )
            tweets.append(tweet)
        
        return tweets
    
    async def search_tweets(
        self,
        access_token: str,
        query: str,
        max_results: int = 10,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None
    ) -> List[TwitterPost]:
        """
        Search for tweets
        
        Args:
            access_token: OAuth access token
            query: Search query
            max_results: Maximum tweets to return
            since_date: Only tweets after this date
            until_date: Only tweets before this date
            
        Returns:
            List of matching tweets
        """
        endpoint = "/tweets/search/recent"
        
        params = {
            "query": query,
            "max_results": min(max(max_results, 10), 100),
            "tweet.fields": "id,text,author_id,created_at,public_metrics,context_annotations"
        }
        
        if since_date:
            params["start_time"] = since_date.isoformat()
        if until_date:
            params["end_time"] = until_date.isoformat()
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        tweets_data = response.get("data", [])
        tweets = []
        
        for tweet_data in tweets_data:
            tweet = TwitterPost(
                id=tweet_data.get("id"),
                text=tweet_data.get("text"),
                author_id=tweet_data.get("author_id"),
                created_at=datetime.fromisoformat(tweet_data.get("created_at", "").replace("Z", "+00:00")),
                public_metrics=tweet_data.get("public_metrics", {}),
                context_annotations=tweet_data.get("context_annotations", [])
            )
            tweets.append(tweet)
        
        return tweets
    
    def is_valid_tweet_text(self, text: str) -> Tuple[bool, str]:
        """
        Validate tweet text
        
        Args:
            text: Tweet text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Tweet text cannot be empty"
        
        if len(text) > 280:
            return False, f"Tweet text too long ({len(text)}/280 characters)"
        
        return True, ""
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from tweet text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from tweet text"""
        import re
        mentions = re.findall(r'@\w+', text)
        return [mention.lower() for mention in mentions]

# Global Twitter client instance
twitter_client = TwitterAPIClient()