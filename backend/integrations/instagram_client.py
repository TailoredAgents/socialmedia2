"""
Instagram Graph API Integration Client
Integration Specialist Component - Complete Instagram API integration for visual content
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import json
import httpx
from dataclasses import dataclass
from enum import Enum

from backend.core.config import get_settings
from backend.auth.social_oauth import oauth_manager

settings = get_settings()
logger = logging.getLogger(__name__)

class InstagramMediaType(Enum):
    """Instagram media types"""
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"
    REELS = "REELS"
    STORIES = "STORIES"

@dataclass
class InstagramMedia:
    """Instagram media data structure"""
    id: str
    media_type: str
    media_url: str
    caption: str
    permalink: str
    timestamp: datetime
    like_count: int
    comments_count: int
    impressions: int
    reach: int
    saved: int
    engagement: int
    is_comment_enabled: bool
    is_shared_to_feed: bool
    owner_id: str
    thumbnail_url: Optional[str] = None
    video_views: Optional[int] = None

@dataclass
class InstagramStory:
    """Instagram story data structure"""
    id: str
    media_type: str
    media_url: str
    permalink: str
    timestamp: datetime
    impressions: int
    reach: int
    replies: int
    exits: int
    taps_forward: int
    taps_back: int
    owner_id: str

@dataclass
class InstagramInsight:
    """Instagram insights data structure"""
    media_id: str
    impressions: int
    reach: int
    engagement: int
    saved: int
    shares: int
    likes: int
    comments: int
    profile_visits: int
    website_clicks: int
    fetched_at: datetime
    video_views: Optional[int] = None

@dataclass
class InstagramProfile:
    """Instagram profile data structure"""
    id: str
    username: str
    name: str
    biography: str
    followers_count: int
    follows_count: int
    media_count: int
    profile_picture_url: str
    website: str
    is_verified: bool
    is_business_account: bool

class InstagramAPIClient:
    """
    Instagram Graph API Client with comprehensive content and analytics capabilities
    
    Features:
    - Image and video posting
    - Carousel (multi-image) posts
    - Reels creation
    - Stories posting
    - Hashtag and mention tracking
    - Insights and analytics
    - Comment management
    - Business account features
    """
    
    def __init__(self):
        """Initialize Instagram API client"""
        self.api_base = "https://graph.facebook.com/v18.0"
        
        # API endpoints
        self.endpoints = {
            "me": "/me",
            "accounts": "/me/accounts",
            "ig_accounts": "/{page_id}?fields=instagram_business_account",
            "media": "/{ig_user_id}/media",
            "media_publish": "/{ig_user_id}/media_publish",
            "media_info": "/{media_id}",
            "insights": "/{object_id}/insights",
            "stories": "/{ig_user_id}/stories",
            "content_publishing_limit": "/{ig_user_id}/content_publishing_limit",
            "hashtag_search": "/ig_hashtag_search",
            "hashtag_info": "/{hashtag_id}",
            "mentioned_media": "/{ig_user_id}/mentioned_media",
            "user_info": "/{ig_user_id}"
        }
        
        # Rate limiting configuration
        self.rate_limits = {
            "content_publishing": {"requests": 25, "window": 3600},  # 25 per hour
            "api_calls": {"requests": 200, "window": 3600},  # 200 per hour
            "insights": {"requests": 200, "window": 3600}
        }
        
        # Content limits
        self.content_limits = {
            "caption": 2200,  # Characters
            "hashtags": 30,  # Maximum hashtags
            "mentions": 20,  # Maximum mentions
            "carousel_items": 10,  # Maximum carousel items
            "video_duration": 60,  # Seconds for feed videos
            "reels_duration": 90,  # Seconds for reels
            "story_duration": 15,  # Seconds for stories
            "video_size": 100 * 1024 * 1024,  # 100MB
            "image_size": 8 * 1024 * 1024  # 8MB
        }
        
        # Supported media types
        self.supported_formats = {
            "image": ["jpg", "jpeg", "png"],
            "video": ["mp4", "mov"],
            "aspect_ratios": {
                "square": (1, 1),
                "portrait": (4, 5),
                "landscape": (1.91, 1)
            }
        }
        
        logger.info("InstagramAPIClient initialized with Graph API v18.0")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Instagram Graph API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            access_token: Facebook access token with Instagram permissions
            data: Request data
            params: Query parameters
            files: File uploads
            
        Returns:
            API response data
        """
        url = f"{self.api_base}{endpoint}"
        
        # Add access token to params
        if not params:
            params = {}
        params["access_token"] = access_token
        
        headers = {
            "User-Agent": "AI-Social-Media-Agent/1.0"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    if files:
                        response = await client.post(url, headers=headers, data=data, files=files, params=params)
                    elif data:
                        response = await client.post(url, headers=headers, data=data, params=params)
                    else:
                        response = await client.post(url, headers=headers, params=params)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("X-Business-Use-Case-Usage", {}).get("call_count", 3600))
                    logger.warning(f"Instagram API rate limited. Waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, access_token, data, params, files)
                
                # Handle API errors
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get("error", {}).get("message", response.text)
                    logger.error(f"Instagram API error {response.status_code}: {error_message}")
                    raise Exception(f"Instagram API error: {error_message}")
                
                return response.json() if response.content else {}
                
            except httpx.RequestError as e:
                logger.error(f"HTTP request error: {e}")
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                logger.error(f"Instagram API request failed: {e}")
                raise
    
    async def get_instagram_account_id(self, access_token: str, facebook_page_id: str) -> str:
        """
        Get Instagram Business Account ID from Facebook Page
        
        Args:
            access_token: Facebook access token
            facebook_page_id: Facebook Page ID connected to Instagram
            
        Returns:
            Instagram Business Account ID
        """
        endpoint = self.endpoints["ig_accounts"].format(page_id=facebook_page_id)
        response = await self._make_request("GET", endpoint, access_token)
        
        ig_account = response.get("instagram_business_account", {})
        ig_account_id = ig_account.get("id")
        
        if not ig_account_id:
            raise Exception("No Instagram Business Account found for this Facebook Page")
        
        return ig_account_id
    
    async def get_facebook_pages(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get Facebook Pages that user manages (required for Instagram)
        
        Args:
            access_token: Facebook access token
            
        Returns:
            List of Facebook Pages
        """
        params = {
            "fields": "id,name,access_token,instagram_business_account"
        }
        
        response = await self._make_request("GET", self.endpoints["accounts"], access_token, params=params)
        return response.get("data", [])
    
    async def get_profile(self, access_token: str, ig_user_id: str) -> InstagramProfile:
        """
        Get Instagram profile information
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            
        Returns:
            Instagram profile data
        """
        endpoint = self.endpoints["user_info"].format(ig_user_id=ig_user_id)
        params = {
            "fields": "id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url,website,is_verified"
        }
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        return InstagramProfile(
            id=response.get("id"),
            username=response.get("username"),
            name=response.get("name", ""),
            biography=response.get("biography", ""),
            followers_count=response.get("followers_count", 0),
            follows_count=response.get("follows_count", 0),
            media_count=response.get("media_count", 0),
            profile_picture_url=response.get("profile_picture_url", ""),
            website=response.get("website", ""),
            is_verified=response.get("is_verified", False),
            is_business_account=True  # Always true for Graph API access
        )
    
    async def create_media_container(
        self,
        access_token: str,
        ig_user_id: str,
        media_type: InstagramMediaType,
        caption: str,
        media_url: Optional[str] = None,
        video_url: Optional[str] = None,
        children: Optional[List[str]] = None,
        location_id: Optional[str] = None,
        user_tags: Optional[List[Dict[str, Any]]] = None,
        product_tags: Optional[List[Dict[str, Any]]] = None,
        cover_url: Optional[str] = None
    ) -> str:
        """
        Create a media container for publishing
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            media_type: Type of media to create
            caption: Post caption
            media_url: URL for image (required for IMAGE)
            video_url: URL for video (required for VIDEO/REELS)
            children: List of child media IDs (required for CAROUSEL_ALBUM)
            location_id: Location ID
            user_tags: User tags with coordinates
            product_tags: Product tags
            cover_url: Cover image URL for reels
            
        Returns:
            Container ID
        """
        endpoint = self.endpoints["media"].format(ig_user_id=ig_user_id)
        
        # Validate caption
        if len(caption) > self.content_limits["caption"]:
            raise ValueError(f"Caption exceeds {self.content_limits['caption']} characters")
        
        # Build media data based on type
        media_data = {
            "caption": caption
        }
        
        if media_type == InstagramMediaType.IMAGE:
            if not media_url:
                raise ValueError("Image URL required for IMAGE type")
            media_data["image_url"] = media_url
            
        elif media_type == InstagramMediaType.VIDEO:
            if not video_url:
                raise ValueError("Video URL required for VIDEO type")
            media_data["video_url"] = video_url
            media_data["media_type"] = "VIDEO"
            
        elif media_type == InstagramMediaType.REELS:
            if not video_url:
                raise ValueError("Video URL required for REELS type")
            media_data["video_url"] = video_url
            media_data["media_type"] = "REELS"
            if cover_url:
                media_data["cover_url"] = cover_url
                
        elif media_type == InstagramMediaType.CAROUSEL_ALBUM:
            if not children or len(children) < 2:
                raise ValueError("At least 2 children required for CAROUSEL_ALBUM")
            if len(children) > self.content_limits["carousel_items"]:
                raise ValueError(f"Maximum {self.content_limits['carousel_items']} items allowed in carousel")
            media_data["media_type"] = "CAROUSEL"
            media_data["children"] = children
        
        # Add optional parameters
        if location_id:
            media_data["location_id"] = location_id
        if user_tags:
            media_data["user_tags"] = user_tags
        if product_tags:
            media_data["product_tags"] = product_tags
        
        response = await self._make_request("POST", endpoint, access_token, data=media_data)
        
        container_id = response.get("id")
        if not container_id:
            raise Exception("Failed to create media container")
        
        logger.info(f"Created Instagram media container: {container_id}")
        return container_id
    
    async def publish_media(
        self,
        access_token: str,
        ig_user_id: str,
        creation_id: str
    ) -> InstagramMedia:
        """
        Publish a media container
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            creation_id: Container ID from create_media_container
            
        Returns:
            Published media data
        """
        endpoint = self.endpoints["media_publish"].format(ig_user_id=ig_user_id)
        
        publish_data = {
            "creation_id": creation_id
        }
        
        response = await self._make_request("POST", endpoint, access_token, data=publish_data)
        
        media_id = response.get("id")
        if not media_id:
            raise Exception("Failed to publish media")
        
        # Get full media details
        return await self.get_media_info(access_token, media_id)
    
    async def post_image(
        self,
        access_token: str,
        ig_user_id: str,
        image_url: str,
        caption: str,
        location_id: Optional[str] = None,
        user_tags: Optional[List[Dict[str, Any]]] = None
    ) -> InstagramMedia:
        """
        Post a single image to Instagram
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            image_url: Public URL of the image
            caption: Post caption
            location_id: Location ID
            user_tags: User tags with coordinates
            
        Returns:
            Posted media data
        """
        # Create container
        container_id = await self.create_media_container(
            access_token=access_token,
            ig_user_id=ig_user_id,
            media_type=InstagramMediaType.IMAGE,
            caption=caption,
            media_url=image_url,
            location_id=location_id,
            user_tags=user_tags
        )
        
        # Wait a moment for container processing
        await asyncio.sleep(2)
        
        # Publish
        return await self.publish_media(access_token, ig_user_id, container_id)
    
    async def post_video(
        self,
        access_token: str,
        ig_user_id: str,
        video_url: str,
        caption: str,
        location_id: Optional[str] = None
    ) -> InstagramMedia:
        """
        Post a video to Instagram
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            video_url: Public URL of the video
            caption: Post caption
            location_id: Location ID
            
        Returns:
            Posted media data
        """
        # Create container
        container_id = await self.create_media_container(
            access_token=access_token,
            ig_user_id=ig_user_id,
            media_type=InstagramMediaType.VIDEO,
            caption=caption,
            video_url=video_url,
            location_id=location_id
        )
        
        # Videos need more processing time
        await asyncio.sleep(10)
        
        # Check status before publishing
        await self._wait_for_container_ready(access_token, container_id)
        
        # Publish
        return await self.publish_media(access_token, ig_user_id, container_id)
    
    async def post_carousel(
        self,
        access_token: str,
        ig_user_id: str,
        media_items: List[Dict[str, str]],
        caption: str,
        location_id: Optional[str] = None
    ) -> InstagramMedia:
        """
        Post a carousel (multiple images/videos) to Instagram
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            media_items: List of dicts with 'type' and 'url' keys
            caption: Post caption
            location_id: Location ID
            
        Returns:
            Posted media data
        """
        if len(media_items) < 2 or len(media_items) > self.content_limits["carousel_items"]:
            raise ValueError(f"Carousel must have 2-{self.content_limits['carousel_items']} items")
        
        # Create child containers
        children_ids = []
        for item in media_items:
            if item["type"] == "image":
                child_data = {"image_url": item["url"]}
            elif item["type"] == "video":
                child_data = {"video_url": item["url"], "media_type": "VIDEO"}
            else:
                raise ValueError(f"Unsupported media type: {item['type']}")
            
            endpoint = self.endpoints["media"].format(ig_user_id=ig_user_id)
            response = await self._make_request("POST", endpoint, access_token, data=child_data)
            
            child_id = response.get("id")
            if child_id:
                children_ids.append(child_id)
            
            # Brief delay between creating children
            await asyncio.sleep(1)
        
        # Create parent container
        container_id = await self.create_media_container(
            access_token=access_token,
            ig_user_id=ig_user_id,
            media_type=InstagramMediaType.CAROUSEL_ALBUM,
            caption=caption,
            children=children_ids,
            location_id=location_id
        )
        
        # Wait for processing
        await asyncio.sleep(5)
        
        # Publish
        return await self.publish_media(access_token, ig_user_id, container_id)
    
    async def post_reel(
        self,
        access_token: str,
        ig_user_id: str,
        video_url: str,
        caption: str,
        cover_url: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> InstagramMedia:
        """
        Post a Reel to Instagram
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            video_url: Public URL of the video (9:16 aspect ratio recommended)
            caption: Post caption
            cover_url: Cover image URL
            location_id: Location ID
            
        Returns:
            Posted media data
        """
        # Create container
        container_id = await self.create_media_container(
            access_token=access_token,
            ig_user_id=ig_user_id,
            media_type=InstagramMediaType.REELS,
            caption=caption,
            video_url=video_url,
            cover_url=cover_url,
            location_id=location_id
        )
        
        # Reels need more processing time
        await asyncio.sleep(15)
        
        # Check status before publishing
        await self._wait_for_container_ready(access_token, container_id)
        
        # Publish
        return await self.publish_media(access_token, ig_user_id, container_id)
    
    async def _wait_for_container_ready(self, access_token: str, container_id: str, max_wait: int = 60):
        """Wait for media container to be ready for publishing"""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < max_wait:
            endpoint = f"/{container_id}"
            params = {"fields": "status_code"}
            
            try:
                response = await self._make_request("GET", endpoint, access_token, params=params)
                status = response.get("status_code")
                
                if status == "FINISHED":
                    return
                elif status == "ERROR":
                    raise Exception("Media container processing failed")
                
                # Status is still IN_PROGRESS
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error checking container status: {e}")
                await asyncio.sleep(5)
        
        raise Exception("Media container processing timeout")
    
    async def get_media_info(self, access_token: str, media_id: str) -> InstagramMedia:
        """
        Get detailed information about a media item
        
        Args:
            access_token: Facebook access token
            media_id: Instagram media ID
            
        Returns:
            Media information
        """
        endpoint = self.endpoints["media_info"].format(media_id=media_id)
        params = {
            "fields": "id,media_type,media_url,caption,permalink,timestamp,like_count,comments_count,is_comment_enabled,owner,thumbnail_url"
        }
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        # Get insights for engagement metrics
        insights = await self.get_media_insights(access_token, media_id)
        
        return InstagramMedia(
            id=response.get("id"),
            media_type=response.get("media_type"),
            media_url=response.get("media_url", ""),
            caption=response.get("caption", ""),
            permalink=response.get("permalink", ""),
            timestamp=datetime.fromisoformat(response.get("timestamp", "").replace("+0000", "+00:00")),
            like_count=response.get("like_count", 0),
            comments_count=response.get("comments_count", 0),
            impressions=insights.impressions,
            reach=insights.reach,
            saved=insights.saved,
            engagement=insights.engagement,
            is_comment_enabled=response.get("is_comment_enabled", True),
            is_shared_to_feed=True,  # Default for business accounts
            owner_id=response.get("owner", {}).get("id", ""),
            thumbnail_url=response.get("thumbnail_url"),
            video_views=insights.video_views
        )
    
    async def get_media_insights(
        self,
        access_token: str,
        media_id: str,
        metrics: Optional[List[str]] = None
    ) -> InstagramInsight:
        """
        Get insights for a media item
        
        Args:
            access_token: Facebook access token
            media_id: Instagram media ID
            metrics: Specific metrics to retrieve
            
        Returns:
            Media insights
        """
        endpoint = self.endpoints["insights"].format(object_id=media_id)
        
        # Default metrics based on media type
        if not metrics:
            metrics = [
                "impressions",
                "reach",
                "engagement",
                "saved",
                "shares",
                "likes",
                "comments",
                "profile_visits"
            ]
        
        params = {
            "metric": ",".join(metrics),
            "period": "lifetime"
        }
        
        try:
            response = await self._make_request("GET", endpoint, access_token, params=params)
            
            # Parse insights data
            insights_data = {}
            for insight in response.get("data", []):
                metric_name = insight.get("name")
                values = insight.get("values", [])
                if values:
                    insights_data[metric_name] = values[0].get("value", 0)
            
            return InstagramInsight(
                media_id=media_id,
                impressions=insights_data.get("impressions", 0),
                reach=insights_data.get("reach", 0),
                engagement=insights_data.get("engagement", 0),
                saved=insights_data.get("saved", 0),
                shares=insights_data.get("shares", 0),
                likes=insights_data.get("likes", 0),
                comments=insights_data.get("comments", 0),
                video_views=insights_data.get("video_views"),
                profile_visits=insights_data.get("profile_visits", 0),
                website_clicks=insights_data.get("website_clicks", 0),
                fetched_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.warning(f"Failed to get Instagram insights: {e}")
            # Return empty insights
            return InstagramInsight(
                media_id=media_id,
                impressions=0,
                reach=0,
                engagement=0,
                saved=0,
                shares=0,
                likes=0,
                comments=0,
                video_views=None,
                profile_visits=0,
                website_clicks=0,
                fetched_at=datetime.utcnow()
            )
    
    async def get_user_media(
        self,
        access_token: str,
        ig_user_id: str,
        limit: int = 25,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None
    ) -> List[InstagramMedia]:
        """
        Get user's media posts
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            limit: Number of posts to retrieve
            since_date: Start date filter
            until_date: End date filter
            
        Returns:
            List of media posts
        """
        endpoint = f"/{ig_user_id}/media"
        params = {
            "fields": "id,media_type,media_url,caption,permalink,timestamp,like_count,comments_count",
            "limit": min(limit, 100)
        }
        
        if since_date:
            params["since"] = int(since_date.timestamp())
        if until_date:
            params["until"] = int(until_date.timestamp())
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        media_list = []
        for item in response.get("data", []):
            try:
                # Get full media details with insights
                media = await self.get_media_info(access_token, item["id"])
                media_list.append(media)
            except Exception as e:
                logger.error(f"Failed to get media info for {item['id']}: {e}")
        
        return media_list
    
    async def delete_media(self, access_token: str, media_id: str) -> bool:
        """
        Delete an Instagram media post
        
        Args:
            access_token: Facebook access token
            media_id: Instagram media ID
            
        Returns:
            Success status
        """
        try:
            endpoint = f"/{media_id}"
            await self._make_request("DELETE", endpoint, access_token)
            
            logger.info(f"Successfully deleted Instagram media {media_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Instagram media {media_id}: {e}")
            return False
    
    async def get_hashtag_id(self, access_token: str, ig_user_id: str, hashtag: str) -> str:
        """
        Get Instagram hashtag ID
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            hashtag: Hashtag name (without #)
            
        Returns:
            Hashtag ID
        """
        params = {
            "user_id": ig_user_id,
            "q": hashtag.replace("#", "")
        }
        
        response = await self._make_request("GET", self.endpoints["hashtag_search"], access_token, params=params)
        
        data = response.get("data", [])
        if data:
            return data[0].get("id")
        
        raise Exception(f"Hashtag '{hashtag}' not found")
    
    async def get_hashtag_media(
        self,
        access_token: str,
        ig_user_id: str,
        hashtag: str,
        media_type: str = "top_media"
    ) -> List[Dict[str, Any]]:
        """
        Get media posts for a hashtag
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            hashtag: Hashtag to search
            media_type: "top_media" or "recent_media"
            
        Returns:
            List of media posts
        """
        # Get hashtag ID
        hashtag_id = await self.get_hashtag_id(access_token, ig_user_id, hashtag)
        
        # Get media for hashtag
        endpoint = self.endpoints["hashtag_info"].format(hashtag_id=hashtag_id)
        params = {
            "fields": f"id,name,{media_type}",
            "user_id": ig_user_id
        }
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        return response.get(media_type, {}).get("data", [])
    
    def validate_caption(self, caption: str) -> Tuple[bool, str]:
        """
        Validate Instagram caption
        
        Args:
            caption: Caption text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(caption) > self.content_limits["caption"]:
            return False, f"Caption too long ({len(caption)}/{self.content_limits['caption']} characters)"
        
        hashtags = self.extract_hashtags(caption)
        if len(hashtags) > self.content_limits["hashtags"]:
            return False, f"Too many hashtags ({len(hashtags)}/{self.content_limits['hashtags']})"
        
        mentions = self.extract_mentions(caption)
        if len(mentions) > self.content_limits["mentions"]:
            return False, f"Too many mentions ({len(mentions)}/{self.content_limits['mentions']})"
        
        return True, ""
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from caption"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from caption"""
        import re
        mentions = re.findall(r'@\w+', text)
        return [mention.lower() for mention in mentions]
    
    def optimize_caption(self, caption: str, add_hashtags: Optional[List[str]] = None) -> str:
        """
        Optimize caption for Instagram
        
        Args:
            caption: Original caption
            add_hashtags: Additional hashtags to include
            
        Returns:
            Optimized caption
        """
        # Ensure hashtags are at the end
        existing_hashtags = self.extract_hashtags(caption)
        
        # Remove hashtags from middle of text
        for hashtag in existing_hashtags:
            caption = caption.replace(hashtag, "")
        
        # Clean up extra spaces
        caption = " ".join(caption.split())
        
        # Add line breaks before hashtags
        if existing_hashtags or add_hashtags:
            caption += "\n\n"
        
        # Add existing hashtags back
        if existing_hashtags:
            caption += " ".join(existing_hashtags[:self.content_limits["hashtags"]])
        
        # Add new hashtags if room
        if add_hashtags:
            remaining_slots = self.content_limits["hashtags"] - len(existing_hashtags)
            if remaining_slots > 0:
                if existing_hashtags:
                    caption += " "
                caption += " ".join(f"#{tag}" for tag in add_hashtags[:remaining_slots])
        
        return caption.strip()
    
    async def check_publishing_limit(self, access_token: str, ig_user_id: str) -> Dict[str, Any]:
        """
        Check content publishing rate limit status
        
        Args:
            access_token: Facebook access token
            ig_user_id: Instagram Business Account ID
            
        Returns:
            Publishing limit status
        """
        endpoint = self.endpoints["content_publishing_limit"].format(ig_user_id=ig_user_id)
        params = {
            "fields": "quota_usage,rate_limit_settings"
        }
        
        response = await self._make_request("GET", endpoint, access_token, params=params)
        
        return {
            "quota_usage": response.get("quota_usage", 0),
            "quota_total": response.get("rate_limit_settings", {}).get("quota_total", 25),
            "quota_duration": response.get("rate_limit_settings", {}).get("quota_duration", 3600)
        }
    
    async def get_user_token(self, user_id: int) -> Optional[str]:
        """
        Get stored Instagram access token for user
        
        Args:
            user_id: User ID
            
        Returns:
            Instagram access token or None if not found
        """
        try:
            return await oauth_manager.get_user_access_token(user_id, "instagram")
        except Exception as e:
            logger.error(f"Failed to get Instagram token for user {user_id}: {e}")
            return None
    
    async def create_post(
        self,
        access_token: str,
        caption: str,
        media_urls: List[str],
        media_type: InstagramMediaType,
        location_id: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create Instagram post (wrapper method for integration API compatibility)
        
        Args:
            access_token: Facebook access token
            caption: Post caption
            media_urls: List of media URLs
            media_type: Type of media
            location_id: Location ID
            hashtags: List of hashtags
            
        Returns:
            Post creation result
        """
        # Get Instagram Business Account ID for this user
        pages = await self.get_facebook_pages(access_token)
        ig_account_id = None
        
        for page in pages:
            if "instagram_business_account" in page:
                ig_account_id = page["instagram_business_account"]["id"]
                break
        
        if not ig_account_id:
            raise Exception("No Instagram Business Account found")
        
        # Optimize caption with hashtags
        optimized_caption = self.optimize_caption(caption, hashtags)
        
        if media_type == InstagramMediaType.IMAGE and len(media_urls) == 1:
            # Single image post
            result = await self.post_image(
                access_token=access_token,
                ig_user_id=ig_account_id,
                image_url=media_urls[0],
                caption=optimized_caption,
                location_id=location_id
            )
        elif media_type == InstagramMediaType.VIDEO and len(media_urls) == 1:
            # Single video post
            result = await self.post_video(
                access_token=access_token,
                ig_user_id=ig_account_id,
                video_url=media_urls[0],
                caption=optimized_caption,
                location_id=location_id
            )
        elif media_type == InstagramMediaType.CAROUSEL_ALBUM and len(media_urls) > 1:
            # Carousel post
            media_items = [{"type": "image", "url": url} for url in media_urls]
            result = await self.post_carousel(
                access_token=access_token,
                ig_user_id=ig_account_id,
                media_items=media_items,
                caption=optimized_caption,
                location_id=location_id
            )
        elif media_type == InstagramMediaType.REELS and len(media_urls) == 1:
            # Reels post
            result = await self.post_reel(
                access_token=access_token,
                ig_user_id=ig_account_id,
                video_url=media_urls[0],
                caption=optimized_caption,
                location_id=location_id
            )
        else:
            raise ValueError(f"Unsupported media configuration: {media_type} with {len(media_urls)} URLs")
        
        return {
            "id": result.id,
            "permalink": result.permalink,
            "media_type": result.media_type
        }

# Global Instagram client instance
instagram_client = InstagramAPIClient()