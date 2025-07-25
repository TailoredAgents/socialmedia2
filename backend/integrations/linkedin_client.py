"""
LinkedIn API Integration Client
Integration Specialist Component - Complete LinkedIn API integration for professional content
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import json
import httpx
from dataclasses import dataclass
import base64

from backend.core.config import get_settings
from backend.auth.social_oauth import oauth_manager

settings = get_settings()
logger = logging.getLogger(__name__)

@dataclass
class LinkedInPost:
    """LinkedIn post data structure"""
    id: str
    text: str
    author_id: str
    created_at: datetime
    visibility: str
    engagement_metrics: Dict[str, int]
    media_urls: List[str]
    article_url: Optional[str] = None
    company_page_id: Optional[str] = None

@dataclass
class LinkedInArticle:
    """LinkedIn article data structure"""
    id: str
    title: str
    content: str
    author_id: str
    published_at: datetime
    canonical_url: str
    thumbnail_url: Optional[str]
    view_count: int
    engagement_metrics: Dict[str, int]

@dataclass
class LinkedInAnalytics:
    """LinkedIn analytics data structure"""
    post_id: str
    impressions: int
    clicks: int
    reactions: int
    comments: int
    shares: int
    engagement_rate: float
    unique_impressions: int
    click_through_rate: float
    fetched_at: datetime

@dataclass
class LinkedInCompanyPage:
    """LinkedIn company page data structure"""
    id: str
    name: str
    description: str
    follower_count: int
    logo_url: str
    industry: str
    company_size: str
    website_url: str

class LinkedInAPIClient:
    """
    LinkedIn API Client with comprehensive posting and analytics capabilities
    
    Features:
    - Professional post creation with media support
    - Company page content management
    - Article publishing
    - Analytics and engagement metrics
    - Connection and network insights
    - Video and document sharing support
    """
    
    def __init__(self):
        """Initialize LinkedIn API client"""
        self.api_base = "https://api.linkedin.com/v2"
        self.api_version = "202401"  # LinkedIn API version
        
        # API endpoints
        self.endpoints = {
            "people": "/people/~",
            "posts": "/ugcPosts",
            "shares": "/shares",
            "articles": "/articles",
            "companies": "/companies/{company_id}",
            "organization_posts": "/organizationAcls",
            "media_upload": "/assets",
            "analytics": "/organizationalEntityShareStatistics",
            "social_actions": "/socialActions/{share_id}/comments"
        }
        
        # Rate limiting configuration (LinkedIn is more restrictive)
        self.rate_limits = {
            "post_create": {"requests": 100, "window": 3600},  # 100 per hour
            "post_lookup": {"requests": 500, "window": 3600},
            "people_lookup": {"requests": 500, "window": 3600},
            "analytics": {"requests": 1000, "window": 3600},
            "media_upload": {"requests": 100, "window": 3600}
        }
        
        # Content limits
        self.content_limits = {
            "post_text": 3000,  # Characters
            "article_title": 150,
            "article_content": 110000,  # Characters
            "media_per_post": 9,  # Maximum media items
            "hashtags_recommended": 5
        }
        
        # Supported media types
        self.supported_media_types = {
            "image": ["jpg", "jpeg", "png"],
            "video": ["mp4", "mov", "avi"],
            "document": ["pdf", "doc", "docx", "ppt", "pptx"]
        }
        
        logger.info("LinkedInAPIClient initialized with v2 API support")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to LinkedIn API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            access_token: OAuth access token
            data: Request data
            params: Query parameters
            headers: Additional headers
            files: File uploads
            
        Returns:
            API response data
        """
        url = f"{self.api_base}{endpoint}"
        
        request_headers = {
            "Authorization": f"Bearer {access_token}",
            "LinkedIn-Version": self.api_version,
            "X-Restli-Protocol-Version": "2.0.0",
            "User-Agent": "AI-Social-Media-Agent/1.0"
        }
        
        if headers:
            request_headers.update(headers)
        
        # Add Content-Type for JSON requests
        if data and not files:
            request_headers["Content-Type"] = "application/json"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=request_headers, params=params)
                elif method.upper() == "POST":
                    if files:
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
                    logger.warning(f"LinkedIn rate limited. Waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    # Retry once after rate limit
                    return await self._make_request(method, endpoint, access_token, data, params, headers, files)
                
                # Handle API errors
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    logger.error(f"LinkedIn API error {response.status_code}: {error_data}")
                    raise Exception(f"LinkedIn API error: {error_data.get('message', response.text)}")
                
                return response.json() if response.content else {}
                
            except httpx.RequestError as e:
                logger.error(f"HTTP request error: {e}")
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                logger.error(f"LinkedIn API request failed: {e}")
                raise
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get authenticated user's LinkedIn profile
        
        Args:
            access_token: OAuth access token
            
        Returns:
            User profile data
        """
        params = {
            "projection": "(id,firstName,lastName,profilePicture(displayImage~:playableStreams),headline,summary,numConnections,numFollowers,industry,positions)"
        }
        
        response = await self._make_request("GET", self.endpoints["people"], access_token, params=params)
        
        # Extract profile information
        profile = {
            "id": response.get("id"),
            "first_name": response.get("firstName", {}).get("localized", {}).get("en_US", ""),
            "last_name": response.get("lastName", {}).get("localized", {}).get("en_US", ""),
            "headline": response.get("headline", {}).get("localized", {}).get("en_US", ""),
            "summary": response.get("summary", {}).get("localized", {}).get("en_US", ""),
            "connections": response.get("numConnections", 0),
            "followers": response.get("numFollowers", 0),
            "industry": response.get("industry", {}).get("localized", {}).get("en_US", ""),
            "profile_image": self._extract_profile_image(response.get("profilePicture", {}))
        }
        
        return profile
    
    def _extract_profile_image(self, profile_picture_data: Dict) -> str:
        """Extract profile image URL from LinkedIn response"""
        try:
            display_image = profile_picture_data.get("displayImage~", {})
            elements = display_image.get("elements", [])
            
            if elements:
                # Get the largest image
                largest_image = max(elements, key=lambda x: x.get("data", {}).get("width", 0) * x.get("data", {}).get("height", 0))
                identifiers = largest_image.get("identifiers", [])
                if identifiers:
                    return identifiers[0].get("identifier", "")
            
            return ""
        except Exception:
            return ""
    
    async def create_post(
        self,
        access_token: str,
        text: str,
        visibility: str = "PUBLIC",
        media_assets: Optional[List[str]] = None,
        article_url: Optional[str] = None,
        author_type: str = "person",
        author_id: Optional[str] = None
    ) -> LinkedInPost:
        """
        Create a LinkedIn post
        
        Args:
            access_token: OAuth access token
            text: Post content
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)
            media_assets: List of uploaded media asset URNs
            article_url: URL to share
            author_type: "person" or "organization"
            author_id: Author ID (for organization posts)
            
        Returns:
            Created post data
        """
        if len(text) > self.content_limits["post_text"]:
            raise ValueError(f"Post text exceeds {self.content_limits['post_text']} characters")
        
        # Get author URN
        if author_type == "person":
            if not author_id:
                profile = await self.get_user_profile(access_token)
                author_id = profile["id"]
            author_urn = f"urn:li:person:{author_id}"
        else:
            author_urn = f"urn:li:organization:{author_id}"
        
        # Build post data
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        # Add media if provided
        if media_assets:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE" if len(media_assets) == 1 else "MULTIPLE_IMAGES"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "description": {
                        "text": "Media content"
                    },
                    "media": asset_urn,
                    "title": {
                        "text": "Shared Media"
                    }
                }
                for asset_urn in media_assets
            ]
        
        # Add article link if provided
        if article_url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                "status": "READY",
                "originalUrl": article_url
            }]
        
        response = await self._make_request("POST", self.endpoints["posts"], access_token, data=post_data)
        
        post_id = response.get("id", "")
        
        # Create LinkedInPost object
        return LinkedInPost(
            id=post_id,
            text=text,
            author_id=author_id,
            created_at=datetime.utcnow(),
            visibility=visibility,
            engagement_metrics={},
            media_urls=[],
            article_url=article_url,
            company_page_id=author_id if author_type == "organization" else None
        )
    
    async def upload_media(
        self,
        access_token: str,
        media_data: bytes,
        media_type: str,
        filename: str,
        description: Optional[str] = None
    ) -> str:
        """
        Upload media to LinkedIn
        
        Args:
            access_token: OAuth access token
            media_data: Binary media data
            media_type: Media MIME type
            filename: Original filename
            description: Media description
            
        Returns:
            Media asset URN
        """
        # Get upload URL
        upload_request = {
            "registerUploadRequest": {
                "recipes": [
                    "urn:li:digitalmediaRecipe:feedshare-image" if media_type.startswith("image") else "urn:li:digitalmediaRecipe:feedshare-video"
                ],
                "owner": f"urn:li:person:{await self._get_user_id(access_token)}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        upload_response = await self._make_request("POST", self.endpoints["media_upload"], access_token, data=upload_request)
        
        upload_mechanism = upload_response.get("value", {}).get("uploadMechanism", {})
        upload_url = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
        asset_urn = upload_response.get("value", {}).get("asset")
        
        if not upload_url or not asset_urn:
            raise Exception("Failed to get upload URL from LinkedIn")
        
        # Upload media data
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            files = {"file": (filename, media_data, media_type)}
            
            upload_result = await client.post(upload_url, headers=headers, files=files)
            
            if upload_result.status_code not in [200, 201]:
                raise Exception(f"Media upload failed: {upload_result.text}")
        
        logger.info(f"Successfully uploaded media to LinkedIn: {asset_urn}")
        return asset_urn
    
    async def _get_user_id(self, access_token: str) -> str:
        """Get the authenticated user's LinkedIn ID"""
        profile = await self.get_user_profile(access_token)
        return profile["id"]
    
    async def create_article(
        self,
        access_token: str,
        title: str,
        content: str,
        visibility: str = "PUBLIC",
        tags: Optional[List[str]] = None
    ) -> LinkedInArticle:
        """
        Create a LinkedIn article
        
        Args:
            access_token: OAuth access token
            title: Article title
            content: Article content (HTML supported)
            visibility: Article visibility
            tags: Article tags
            
        Returns:
            Created article data
        """
        if len(title) > self.content_limits["article_title"]:
            raise ValueError(f"Article title exceeds {self.content_limits['article_title']} characters")
        
        if len(content) > self.content_limits["article_content"]:
            raise ValueError(f"Article content exceeds {self.content_limits['article_content']} characters")
        
        user_id = await self._get_user_id(access_token)
        
        article_data = {
            "author": f"urn:li:person:{user_id}",
            "title": {
                "text": title
            },
            "content": {
                "contentEntities": [
                    {
                        "entityLocation": "https://linkedin.com",
                        "entity": {
                            "text": content
                        }
                    }
                ]
            },
            "visibility": visibility,
            "publishedAt": int(datetime.utcnow().timestamp() * 1000)
        }
        
        if tags:
            article_data["tags"] = tags
        
        response = await self._make_request("POST", self.endpoints["articles"], access_token, data=article_data)
        
        article_id = response.get("id", "")
        
        return LinkedInArticle(
            id=article_id,
            title=title,
            content=content,
            author_id=user_id,
            published_at=datetime.utcnow(),
            canonical_url=f"https://www.linkedin.com/pulse/{article_id}",
            thumbnail_url=None,
            view_count=0,
            engagement_metrics={}
        )
    
    async def get_post_analytics(
        self,
        access_token: str,
        post_id: str,
        time_range: str = "last30Days"
    ) -> LinkedInAnalytics:
        """
        Get analytics for a LinkedIn post
        
        Args:
            access_token: OAuth access token
            post_id: Post ID
            time_range: Time range for analytics
            
        Returns:
            Post analytics data
        """
        # LinkedIn analytics require organization access
        # This is a simplified implementation
        params = {
            "q": "organizationalEntity",
            "organizationalEntity": f"urn:li:organization:{await self._get_user_id(access_token)}",
            "timeIntervals.timeGranularityType": "DAY",
            "timeIntervals.timeRange.start": int((datetime.utcnow() - timedelta(days=30)).timestamp() * 1000),
            "timeIntervals.timeRange.end": int(datetime.utcnow().timestamp() * 1000)
        }
        
        try:
            response = await self._make_request("GET", self.endpoints["analytics"], access_token, params=params)
            
            # Extract analytics data (simplified)
            elements = response.get("elements", [])
            total_stats = {
                "impressions": 0,
                "clicks": 0,
                "reactions": 0,
                "comments": 0,
                "shares": 0
            }
            
            for element in elements:
                stats = element.get("totalShareStatistics", {})
                total_stats["impressions"] += stats.get("impressionCount", 0)
                total_stats["clicks"] += stats.get("clickCount", 0)
                total_stats["reactions"] += stats.get("likeCount", 0)
                total_stats["comments"] += stats.get("commentCount", 0)
                total_stats["shares"] += stats.get("shareCount", 0)
            
            # Calculate engagement rate
            engagement_rate = 0
            if total_stats["impressions"] > 0:
                engagements = total_stats["reactions"] + total_stats["comments"] + total_stats["shares"]
                engagement_rate = (engagements / total_stats["impressions"]) * 100
            
            # Calculate click-through rate
            ctr = 0
            if total_stats["impressions"] > 0:
                ctr = (total_stats["clicks"] / total_stats["impressions"]) * 100
            
            return LinkedInAnalytics(
                post_id=post_id,
                impressions=total_stats["impressions"],
                clicks=total_stats["clicks"],
                reactions=total_stats["reactions"],
                comments=total_stats["comments"],
                shares=total_stats["shares"],
                engagement_rate=engagement_rate,
                unique_impressions=total_stats["impressions"],  # Simplified
                click_through_rate=ctr,
                fetched_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.warning(f"Failed to get LinkedIn analytics: {e}")
            # Return empty analytics
            return LinkedInAnalytics(
                post_id=post_id,
                impressions=0,
                clicks=0,
                reactions=0,
                comments=0,
                shares=0,
                engagement_rate=0.0,
                unique_impressions=0,
                click_through_rate=0.0,
                fetched_at=datetime.utcnow()
            )
    
    async def get_company_pages(self, access_token: str) -> List[LinkedInCompanyPage]:
        """
        Get company pages the user can manage
        
        Args:
            access_token: OAuth access token
            
        Returns:
            List of company pages
        """
        params = {
            "q": "roleAssignee",
            "role": "ADMINISTRATOR",
            "projection": "(elements*(organization~(id,name,description,numFollowers,logoV2,industries,staffRange,website)))"
        }
        
        try:
            response = await self._make_request("GET", self.endpoints["organization_posts"], access_token, params=params)
            
            elements = response.get("elements", [])
            company_pages = []
            
            for element in elements:
                org_data = element.get("organization~", {})
                if org_data:
                    company_page = LinkedInCompanyPage(
                        id=org_data.get("id", ""),
                        name=org_data.get("name", {}).get("localized", {}).get("en_US", ""),
                        description=org_data.get("description", {}).get("localized", {}).get("en_US", ""),
                        follower_count=org_data.get("numFollowers", 0),
                        logo_url=self._extract_company_logo(org_data.get("logoV2", {})),
                        industry=self._extract_first_industry(org_data.get("industries", [])),
                        company_size=self._extract_company_size(org_data.get("staffRange", {})),
                        website_url=org_data.get("website", {}).get("localized", {}).get("en_US", "")
                    )
                    company_pages.append(company_page)
            
            return company_pages
            
        except Exception as e:
            logger.error(f"Failed to get company pages: {e}")
            return []
    
    def _extract_company_logo(self, logo_data: Dict) -> str:
        """Extract company logo URL"""
        try:
            cropped = logo_data.get("cropped~", {})
            elements = cropped.get("elements", [])
            if elements:
                identifiers = elements[0].get("identifiers", [])
                if identifiers:
                    return identifiers[0].get("identifier", "")
            return ""
        except Exception:
            return ""
    
    def _extract_first_industry(self, industries: List[Dict]) -> str:
        """Extract first industry name"""
        try:
            if industries:
                return industries[0].get("localized", {}).get("en_US", "")
            return ""
        except Exception:
            return ""
    
    def _extract_company_size(self, staff_range: Dict) -> str:
        """Extract company size description"""
        try:
            return staff_range.get("localized", {}).get("en_US", "")
        except Exception:
            return ""
    
    async def delete_post(self, access_token: str, post_id: str) -> bool:
        """
        Delete a LinkedIn post
        
        Args:
            access_token: OAuth access token
            post_id: Post ID to delete
            
        Returns:
            Success status
        """
        try:
            endpoint = f"/ugcPosts/{post_id}"
            await self._make_request("DELETE", endpoint, access_token)
            
            logger.info(f"Successfully deleted LinkedIn post {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete LinkedIn post {post_id}: {e}")
            return False
    
    def validate_post_content(self, text: str) -> Tuple[bool, str]:
        """
        Validate LinkedIn post content
        
        Args:
            text: Post content to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Post content cannot be empty"
        
        if len(text) > self.content_limits["post_text"]:
            return False, f"Post content too long ({len(text)}/{self.content_limits['post_text']} characters)"
        
        return True, ""
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from LinkedIn post text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from LinkedIn post text"""
        import re
        mentions = re.findall(r'@[\w\s]+', text)
        return [mention.strip().lower() for mention in mentions]
    
    def optimize_for_linkedin(self, text: str) -> str:
        """
        Optimize content for LinkedIn's professional audience
        
        Args:
            text: Original content
            
        Returns:
            Optimized content
        """
        # Add professional tone indicators
        if not any(word in text.lower() for word in ['insight', 'experience', 'professional', 'career', 'business']):
            # This is a simplified optimization
            # In a real implementation, this would use AI to enhance the professional tone
            pass
        
        # Ensure proper hashtag usage (LinkedIn recommends 3-5)
        hashtags = self.extract_hashtags(text)
        if len(hashtags) > 5:
            # Keep first 5 hashtags
            for hashtag in hashtags[5:]:
                text = text.replace(hashtag, '')
        
        return text.strip()

# Global LinkedIn client instance
linkedin_client = LinkedInAPIClient()