"""
TikTok API Integration Client
Integration Specialist Component - Complete TikTok API integration for short-form video content
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import json
import httpx
from dataclasses import dataclass
from enum import Enum
import base64

from backend.core.config import get_settings
from backend.auth.social_oauth import oauth_manager
from backend.integrations.integration_error_handler import handle_integration_errors

settings = get_settings()
logger = logging.getLogger(__name__)

class TikTokVideoPrivacy(Enum):
    """TikTok video privacy settings"""
    PUBLIC_TO_EVERYONE = "PUBLIC_TO_EVERYONE"
    MUTUAL_FOLLOW_FRIENDS = "MUTUAL_FOLLOW_FRIENDS"
    FOLLOWER_OF_CREATOR = "FOLLOWER_OF_CREATOR"
    SELF_ONLY = "SELF_ONLY"

class TikTokVideoFeature(Enum):
    """TikTok video features"""
    DUET = "duet"
    STITCH = "stitch"
    COMMENT = "comment"

@dataclass
class TikTokVideo:
    """TikTok video data structure"""
    id: str
    title: str
    video_description: str
    duration: int
    height: int
    width: int
    cover_image_url: str
    share_url: str
    embed_html: str
    embed_link: str
    create_time: datetime
    username: str
    display_name: str
    avatar_url: str
    follower_count: int
    following_count: int
    likes_count: int
    video_view_count: int
    share_count: int
    comment_count: int
    is_verified: bool
    privacy_level: str
    hashtags: List[str]
    effects: List[str]
    music_info: Dict[str, Any]

@dataclass
class TikTokUserInfo:
    """TikTok user information"""
    open_id: str
    union_id: str
    avatar_url: str
    avatar_url_100: str
    avatar_large_url: str
    display_name: str
    bio_description: str
    profile_deep_link: str
    is_verified: bool
    follower_count: int
    following_count: int
    likes_count: int
    video_count: int

@dataclass
class TikTokVideoAnalytics:
    """TikTok video analytics data structure"""
    video_id: str
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    profile_view: int
    reach: int
    play_time_sum: int
    average_watch_time: float
    completion_rate: float
    engagement_rate: float
    date_range_begin: datetime
    date_range_end: datetime
    fetched_at: datetime

@dataclass
class TikTokHashtagChallenge:
    """TikTok hashtag challenge data structure"""
    hashtag_id: str
    hashtag_name: str
    is_commerce: bool
    view_count: int
    publish_cnt: int
    cover_image: List[str]
    desc: str

class TikTokAPIClient:
    """
    TikTok for Developers API Client with comprehensive video management and analytics
    
    Features:
    - Video uploading and publishing
    - User profile management
    - Video analytics and insights
    - Hashtag research and trending content
    - Comment management
    - Live stream integration
    - Creator marketplace features
    - Advanced targeting and optimization
    """
    
    def __init__(self):
        """Initialize TikTok API client"""
        self.api_base = "https://open.tiktokapis.com/v2"
        self.upload_base = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        
        # API endpoints
        self.endpoints = {
            "user_info": "/user/info/",
            "video_list": "/video/list/",
            "video_query": "/video/query/",
            "video_upload_init": "/post/publish/video/init/",
            "video_upload": "/post/publish/video/upload/",
            "video_publish": "/post/publish/status/fetch/",
            "video_analytics": "/research/video/query/",
            "user_analytics": "/research/user/info/",
            "hashtag_suggest": "/research/hashtag/suggest/",
            "trending_videos": "/research/video/query/",
            "comment_list": "/video/comment/list/",
            "comment_reply": "/video/comment/reply/"
        }
        
        # Rate limiting configuration (TikTok has strict limits)
        self.rate_limits = {
            "video_upload": {"requests": 10, "window": 86400},    # 10 per day
            "video_query": {"requests": 1000, "window": 86400},   # 1000 per day
            "user_info": {"requests": 1000, "window": 86400},
            "analytics": {"requests": 1000, "window": 86400},
            "comment_management": {"requests": 100, "window": 3600}  # 100 per hour
        }
        
        # Content limits and requirements
        self.content_limits = {
            "video_description": 2200,  # Characters
            "video_duration_min": 3,    # Seconds
            "video_duration_max": 600,  # 10 minutes
            "video_size_max": 287 * 1024 * 1024,  # 287MB
            "aspect_ratio": [(9, 16), (1, 1)],  # Vertical or square
            "resolution_min": (540, 960),
            "resolution_max": (2160, 3840),
            "hashtags_max": 100,  # Per video
            "mentions_max": 20
        }
        
        # Supported formats
        self.supported_formats = {
            "video": ["mp4", "mov", "avi", "flv", "webm", "mkv"],
            "audio": ["aac", "mp3", "wav", "m4a"],
            "codecs": {
                "video": ["H.264", "H.265"],
                "audio": ["AAC", "MP3"]
            },
            "frame_rates": [23.976, 24, 25, 29.97, 30, 50, 59.94, 60]
        }
        
        logger.info("TikTokAPIClient initialized with TikTok for Developers API v2")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Make authenticated request to TikTok API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            access_token: TikTok access token
            data: Request data
            params: Query parameters
            headers: Additional headers
            files: File uploads
            timeout: Request timeout in seconds
            
        Returns:
            API response data
        """
        url = f"{self.api_base}{endpoint}"
        
        request_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Social-Media-Agent/1.0"
        }
        
        if headers:
            request_headers.update(headers)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=request_headers, params=params)
                elif method.upper() == "POST":
                    if files:
                        # Remove Content-Type for multipart uploads
                        request_headers.pop("Content-Type", None)
                        response = await client.post(url, headers=request_headers, data=data, files=files)
                    elif data:
                        response = await client.post(url, headers=request_headers, json=data)
                    else:
                        response = await client.post(url, headers=request_headers, params=params)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=request_headers, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=request_headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 3600))
                    logger.warning(f"TikTok API rate limited. Waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, access_token, data, params, headers, files, timeout)
                
                # Handle API errors
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    error_info = error_data.get("error", {})
                    error_message = error_info.get("message", response.text)
                    error_code = error_info.get("code", response.status_code)
                    
                    logger.error(f"TikTok API error {error_code}: {error_message}")
                    raise Exception(f"TikTok API error ({error_code}): {error_message}")
                
                response_data = response.json() if response.content else {}
                
                # Check TikTok-specific error format
                if "error" in response_data:
                    error_info = response_data["error"]
                    raise Exception(f"TikTok API error: {error_info.get('message', 'Unknown error')}")
                
                return response_data
                
            except httpx.RequestError as e:
                logger.error(f"HTTP request error: {e}")
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                logger.error(f"TikTok API request failed: {e}")
                raise
    
    @handle_integration_errors("tiktok", "get_user_info")
    async def get_user_info(self, access_token: str, fields: Optional[List[str]] = None) -> TikTokUserInfo:
        """
        Get authenticated user's TikTok profile information
        
        Args:
            access_token: TikTok access token
            fields: Specific fields to retrieve
            
        Returns:
            User profile information
        """
        if not fields:
            fields = [
                "open_id", "union_id", "avatar_url", "avatar_url_100", "avatar_large_url",
                "display_name", "bio_description", "profile_deep_link", "is_verified",
                "follower_count", "following_count", "likes_count", "video_count"
            ]
        
        params = {
            "fields": ",".join(fields)
        }
        
        response = await self._make_request("GET", self.endpoints["user_info"], access_token, params=params)
        
        user_data = response.get("data", {}).get("user", {})
        
        return TikTokUserInfo(
            open_id=user_data.get("open_id", ""),
            union_id=user_data.get("union_id", ""),
            avatar_url=user_data.get("avatar_url", ""),
            avatar_url_100=user_data.get("avatar_url_100", ""),
            avatar_large_url=user_data.get("avatar_large_url", ""),
            display_name=user_data.get("display_name", ""),
            bio_description=user_data.get("bio_description", ""),
            profile_deep_link=user_data.get("profile_deep_link", ""),
            is_verified=user_data.get("is_verified", False),
            follower_count=user_data.get("follower_count", 0),
            following_count=user_data.get("following_count", 0),
            likes_count=user_data.get("likes_count", 0),
            video_count=user_data.get("video_count", 0)
        )
    
    @handle_integration_errors("tiktok", "upload_video")
    async def upload_video(
        self,
        access_token: str,
        video_url: str,
        description: str,
        privacy_level: TikTokVideoPrivacy = TikTokVideoPrivacy.PUBLIC_TO_EVERYONE,
        disable_duet: bool = False,
        disable_stitch: bool = False,
        disable_comment: bool = False,
        brand_content_toggle: bool = False,
        brand_organic_toggle: bool = False,
        auto_add_music: bool = True
    ) -> str:
        """
        Upload and publish video to TikTok
        
        Args:
            access_token: TikTok access token
            video_url: URL of video to upload
            description: Video description/caption
            privacy_level: Video privacy setting
            disable_duet: Disable duet feature
            disable_stitch: Disable stitch feature
            disable_comment: Disable comments
            brand_content_toggle: Mark as brand content
            brand_organic_toggle: Mark as brand organic content
            auto_add_music: Auto add music recommendation
            
        Returns:
            Publish ID for status checking
        """
        if len(description) > self.content_limits["video_description"]:
            raise ValueError(f"Description exceeds {self.content_limits['video_description']} characters")
        
        # Step 1: Initialize video upload
        init_data = {
            "post_info": {
                "title": description,
                "privacy_level": privacy_level.value,
                "disable_duet": disable_duet,
                "disable_stitch": disable_stitch,
                "disable_comment": disable_comment,
                "brand_content_toggle": brand_content_toggle,
                "brand_organic_toggle": brand_organic_toggle
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_url": video_url
            }
        }
        
        if auto_add_music:
            init_data["post_info"]["auto_add_music"] = True
        
        init_response = await self._make_request("POST", self.endpoints["video_upload_init"], access_token, data=init_data)
        
        publish_id = init_response.get("data", {}).get("publish_id")
        if not publish_id:
            raise Exception("Failed to initialize video upload")
        
        logger.info(f"TikTok video upload initialized with publish_id: {publish_id}")
        
        # Step 2: Check upload status
        await self._wait_for_upload_completion(access_token, publish_id)
        
        return publish_id
    
    async def _wait_for_upload_completion(self, access_token: str, publish_id: str, max_wait: int = 300):
        """
        Wait for video upload and processing to complete
        
        Args:
            access_token: TikTok access token
            publish_id: Publish ID from upload initialization
            max_wait: Maximum wait time in seconds
        """
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < max_wait:
            params = {"publish_id": publish_id}
            
            try:
                response = await self._make_request("POST", self.endpoints["video_publish"], access_token, data=params)
                
                status_data = response.get("data", {})
                status = status_data.get("status")
                
                if status == "PUBLISHED":
                    logger.info(f"TikTok video {publish_id} published successfully")
                    return
                elif status == "FAILED":
                    fail_reason = status_data.get("fail_reason", "Unknown error")
                    raise Exception(f"Video upload failed: {fail_reason}")
                elif status == "PROCESSING":
                    logger.info(f"Video {publish_id} still processing...")
                    await asyncio.sleep(10)
                else:
                    # Status could be "UPLOADING" or other intermediate states
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"Error checking upload status: {e}")
                await asyncio.sleep(10)
        
        raise Exception(f"Video upload timeout after {max_wait} seconds")
    
    @handle_integration_errors("tiktok", "get_user_videos")
    async def get_user_videos(
        self,
        access_token: str,
        max_count: int = 20,
        cursor: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get user's TikTok videos
        
        Args:
            access_token: TikTok access token
            max_count: Maximum number of videos to retrieve
            cursor: Pagination cursor
            fields: Specific fields to retrieve
            
        Returns:
            Video list with pagination info
        """
        if not fields:
            fields = [
                "id", "title", "video_description", "duration", "height", "width",
                "cover_image_url", "share_url", "embed_html", "embed_link", "create_time"
            ]
        
        params = {
            "max_count": min(max_count, 100),  # TikTok API limit
            "fields": ",".join(fields)
        }
        
        if cursor:
            params["cursor"] = cursor
        
        response = await self._make_request("POST", self.endpoints["video_list"], access_token, data=params)
        
        videos_data = response.get("data", {})
        videos = []
        
        for video_info in videos_data.get("videos", []):
            video = TikTokVideo(
                id=video_info.get("id", ""),
                title=video_info.get("title", ""),
                video_description=video_info.get("video_description", ""),
                duration=video_info.get("duration", 0),
                height=video_info.get("height", 0),
                width=video_info.get("width", 0),
                cover_image_url=video_info.get("cover_image_url", ""),
                share_url=video_info.get("share_url", ""),
                embed_html=video_info.get("embed_html", ""),
                embed_link=video_info.get("embed_link", ""),
                create_time=datetime.fromtimestamp(video_info.get("create_time", 0)),
                username="",  # Not available in this endpoint
                display_name="",
                avatar_url="",
                follower_count=0,
                following_count=0,
                likes_count=video_info.get("like_count", 0),
                video_view_count=video_info.get("view_count", 0),
                share_count=video_info.get("share_count", 0),
                comment_count=video_info.get("comment_count", 0),
                is_verified=False,
                privacy_level=video_info.get("privacy_level", ""),
                hashtags=self._extract_hashtags(video_info.get("video_description", "")),
                effects=video_info.get("effects", []),
                music_info=video_info.get("music_info", {})
            )
            videos.append(video)
        
        return {
            "videos": videos,
            "cursor": videos_data.get("cursor", ""),
            "has_more": videos_data.get("has_more", False),
            "total": len(videos)
        }
    
    @handle_integration_errors("tiktok", "get_video_analytics")
    async def get_video_analytics(
        self,
        access_token: str,
        video_ids: List[str],
        fields: Optional[List[str]] = None,
        date_range_begin: Optional[datetime] = None,
        date_range_end: Optional[datetime] = None
    ) -> List[TikTokVideoAnalytics]:
        """
        Get analytics for TikTok videos
        
        Args:
            access_token: TikTok access token
            video_ids: List of video IDs to analyze
            fields: Specific analytics fields to retrieve
            date_range_begin: Start date for analytics
            date_range_end: End date for analytics
            
        Returns:
            List of video analytics
        """
        if not fields:
            fields = [
                "video_id", "video_view", "profile_view", "like", "comment", "share",
                "reach", "play_time", "average_watch_time", "full_video_watched_rate"
            ]
        
        if not date_range_begin:
            date_range_begin = datetime.utcnow() - timedelta(days=30)
        if not date_range_end:
            date_range_end = datetime.utcnow()
        
        # TikTok API limits to 100 video IDs per request
        video_chunks = [video_ids[i:i+100] for i in range(0, len(video_ids), 100)]
        all_analytics = []
        
        for chunk in video_chunks:
            query_data = {
                "filters": {
                    "video_ids": chunk
                },
                "max_count": len(chunk),
                "metrics": fields,
                "date_range": {
                    "date_range_begin": date_range_begin.strftime("%Y%m%d"),
                    "date_range_end": date_range_end.strftime("%Y%m%d")
                }
            }
            
            response = await self._make_request("POST", self.endpoints["video_analytics"], access_token, data=query_data)
            
            analytics_data = response.get("data", {}).get("list", [])
            
            for item in analytics_data:
                metrics = item.get("metrics", {})
                dimensions = item.get("dimensions", {})
                
                # Calculate engagement rate
                views = metrics.get("video_view", 1)
                likes = metrics.get("like", 0)
                comments = metrics.get("comment", 0)
                shares = metrics.get("share", 0)
                engagement = likes + comments + shares
                engagement_rate = (engagement / views * 100) if views > 0 else 0
                
                # Calculate completion rate
                play_time = metrics.get("play_time", 0)
                avg_watch_time = metrics.get("average_watch_time", 0)
                completion_rate = (avg_watch_time / play_time * 100) if play_time > 0 else 0
                
                analytics = TikTokVideoAnalytics(
                    video_id=dimensions.get("video_id", ""),
                    view_count=metrics.get("video_view", 0),
                    like_count=likes,
                    comment_count=comments,
                    share_count=shares,
                    profile_view=metrics.get("profile_view", 0),
                    reach=metrics.get("reach", 0),
                    play_time_sum=play_time,
                    average_watch_time=avg_watch_time,
                    completion_rate=completion_rate,
                    engagement_rate=engagement_rate,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    fetched_at=datetime.utcnow()
                )
                
                all_analytics.append(analytics)
            
            # Brief delay between chunks to respect rate limits
            if len(video_chunks) > 1:
                await asyncio.sleep(1)
        
        return all_analytics
    
    @handle_integration_errors("tiktok", "search_hashtags")
    async def search_hashtags(
        self,
        access_token: str,
        keywords: List[str],
        period: int = 7,
        region_code: str = "US"
    ) -> List[TikTokHashtagChallenge]:
        """
        Search for trending hashtags and challenges
        
        Args:
            access_token: TikTok access token
            keywords: Keywords to search for
            period: Time period in days (1, 7, 30, 120)
            region_code: Region code for localized results
            
        Returns:
            List of hashtag challenges
        """
        query_data = {
            "keywords": keywords,
            "period": period,
            "region_code": region_code,
            "max_count": 100
        }
        
        response = await self._make_request("POST", self.endpoints["hashtag_suggest"], access_token, data=query_data)
        
        hashtags_data = response.get("data", {}).get("list", [])
        hashtags = []
        
        for hashtag_info in hashtags_data:
            hashtag = TikTokHashtagChallenge(
                hashtag_id=hashtag_info.get("hashtag_id", ""),
                hashtag_name=hashtag_info.get("hashtag_name", ""),
                is_commerce=hashtag_info.get("is_commerce", False),
                view_count=hashtag_info.get("view_count", 0),
                publish_cnt=hashtag_info.get("publish_cnt", 0),
                cover_image=hashtag_info.get("cover_image", []),
                desc=hashtag_info.get("desc", "")
            )
            hashtags.append(hashtag)
        
        return hashtags
    
    @handle_integration_errors("tiktok", "get_trending_videos")
    async def get_trending_videos(
        self,
        access_token: str,
        region_code: str = "US",
        period: int = 7,
        max_count: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get trending videos in specified region
        
        Args:
            access_token: TikTok access token
            region_code: Region code for localized results
            period: Time period in days
            max_count: Maximum number of videos to retrieve
            
        Returns:
            List of trending video information
        """
        query_data = {
            "region_code": region_code,
            "period": period,
            "max_count": min(max_count, 1000),
            "sort_by": "trending_score"
        }
        
        response = await self._make_request("POST", self.endpoints["trending_videos"], access_token, data=query_data)
        
        return response.get("data", {}).get("list", [])
    
    def validate_video_content(self, description: str, video_duration: int = 0) -> Tuple[bool, str]:
        """
        Validate TikTok video content
        
        Args:
            description: Video description to validate
            video_duration: Video duration in seconds
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not description or not description.strip():
            return False, "Video description cannot be empty"
        
        if len(description) > self.content_limits["video_description"]:
            return False, f"Description too long ({len(description)}/{self.content_limits['video_description']} characters)"
        
        if video_duration > 0:
            if video_duration < self.content_limits["video_duration_min"]:
                return False, f"Video too short (minimum {self.content_limits['video_duration_min']} seconds)"
            
            if video_duration > self.content_limits["video_duration_max"]:
                return False, f"Video too long (maximum {self.content_limits['video_duration_max']} seconds)"
        
        # Check hashtag count
        hashtags = self._extract_hashtags(description)
        if len(hashtags) > self.content_limits["hashtags_max"]:
            return False, f"Too many hashtags ({len(hashtags)}/{self.content_limits['hashtags_max']})"
        
        return True, ""
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re
        mentions = re.findall(r'@\w+', text)
        return [mention.lower() for mention in mentions]
    
    def optimize_for_tiktok(self, description: str, trending_hashtags: Optional[List[str]] = None) -> str:
        """
        Optimize content for TikTok's algorithm and audience
        
        Args:
            description: Original description
            trending_hashtags: List of trending hashtags to include
            
        Returns:
            Optimized description
        """
        # TikTok favors engaging, authentic content
        engagement_hooks = [
            "Wait for it...",
            "You won't believe this!",
            "POV:",
            "Day in my life:",
            "Things I wish I knew:",
            "Plot twist:"
        ]
        
        # Check if description already has a hook
        has_hook = any(hook.lower() in description.lower() for hook in engagement_hooks)
        
        # Add trending hashtags if provided and space allows
        current_hashtags = self._extract_hashtags(description)
        
        if trending_hashtags and len(description) < self.content_limits["video_description"] - 100:
            # Add top 3 trending hashtags that aren't already included
            new_hashtags = []
            for hashtag in trending_hashtags[:3]:
                if hashtag.lower() not in [h.lower() for h in current_hashtags]:
                    new_hashtags.append(hashtag if hashtag.startswith('#') else f'#{hashtag}')
            
            if new_hashtags:
                description += f"\n\n{' '.join(new_hashtags)}"
        
        # Add popular TikTok hashtags if room allows
        popular_hashtags = ["#fyp", "#foryou", "#viral", "#trending"]
        remaining_space = self.content_limits["video_description"] - len(description)
        
        if remaining_space > 50:
            for hashtag in popular_hashtags:
                if hashtag.lower() not in description.lower() and len(description + f" {hashtag}") <= self.content_limits["video_description"]:
                    description += f" {hashtag}"
        
        return description.strip()
    
    async def get_video_comments(
        self,
        access_token: str,
        video_id: str,
        max_count: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comments for a specific video
        
        Args:
            access_token: TikTok access token
            video_id: Video ID
            max_count: Maximum number of comments to retrieve
            cursor: Pagination cursor
            
        Returns:
            Comments data with pagination info
        """
        params = {
            "video_id": video_id,
            "max_count": min(max_count, 50),  # TikTok API limit
            "fields": ["id", "text", "create_time", "like_count", "reply_count", "parent_comment_id"]
        }
        
        if cursor:
            params["cursor"] = cursor
        
        response = await self._make_request("GET", self.endpoints["comment_list"], access_token, params=params)
        
        return response.get("data", {})
    
    async def reply_to_comment(
        self,
        access_token: str,
        video_id: str,
        comment_id: str,
        reply_text: str
    ) -> Dict[str, Any]:
        """
        Reply to a comment on a video
        
        Args:
            access_token: TikTok access token
            video_id: Video ID
            comment_id: Comment ID to reply to
            reply_text: Reply text content
            
        Returns:
            Reply information
        """
        if len(reply_text) > 150:  # TikTok comment limit
            raise ValueError("Reply text exceeds 150 characters")
        
        reply_data = {
            "video_id": video_id,
            "comment_id": comment_id,
            "text": reply_text
        }
        
        response = await self._make_request("POST", self.endpoints["comment_reply"], access_token, data=reply_data)
        
        return response.get("data", {})
    
    def get_video_insights_summary(self, analytics_list: List[TikTokVideoAnalytics]) -> Dict[str, Any]:
        """
        Generate summary insights from video analytics
        
        Args:
            analytics_list: List of video analytics
            
        Returns:
            Summary insights
        """
        if not analytics_list:
            return {}
        
        total_views = sum(a.view_count for a in analytics_list)
        total_likes = sum(a.like_count for a in analytics_list)
        total_comments = sum(a.comment_count for a in analytics_list)
        total_shares = sum(a.share_count for a in analytics_list)
        
        avg_engagement_rate = sum(a.engagement_rate for a in analytics_list) / len(analytics_list)
        avg_completion_rate = sum(a.completion_rate for a in analytics_list) / len(analytics_list)
        avg_watch_time = sum(a.average_watch_time for a in analytics_list) / len(analytics_list)
        
        # Find best performing video
        best_video = max(analytics_list, key=lambda x: x.engagement_rate)
        
        return {
            "total_videos": len(analytics_list),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_engagement": total_likes + total_comments + total_shares,
            "average_engagement_rate": round(avg_engagement_rate, 2),
            "average_completion_rate": round(avg_completion_rate, 2),
            "average_watch_time": round(avg_watch_time, 2),
            "best_performing_video": {
                "video_id": best_video.video_id,
                "engagement_rate": best_video.engagement_rate,
                "view_count": best_video.view_count
            },
            "performance_trends": {
                "high_engagement_videos": len([a for a in analytics_list if a.engagement_rate > avg_engagement_rate * 1.5]),
                "viral_potential_videos": len([a for a in analytics_list if a.view_count > total_views / len(analytics_list) * 3])
            }
        }
    
    async def get_user_token(self, user_id: int) -> Optional[str]:
        """
        Get stored TikTok access token for user
        
        Args:
            user_id: User ID
            
        Returns:
            TikTok access token or None if not found
        """
        try:
            return await oauth_manager.get_user_access_token(user_id, "tiktok")
        except Exception as e:
            logger.error(f"Failed to get TikTok token for user {user_id}: {e}")
            return None


# Global TikTok client instance
tiktok_client = TikTokAPIClient()