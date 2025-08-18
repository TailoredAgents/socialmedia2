"""
LinkedIn API Client with OAuth 2.0 Support
Handles authentication, posting, and metrics collection for LinkedIn platform
"""
import os
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import json
import time
from dataclasses import dataclass

import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from backend.core.token_encryption import get_token_manager
from backend.core.audit_logger import log_content_event, AuditEventType

logger = logging.getLogger(__name__)

class LinkedInAPIError(Exception):
    """Custom exception for LinkedIn API errors"""
    pass

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

class LinkedInClient:
    """
    LinkedIn API client with OAuth 2.0 authentication and comprehensive features
    
    Features:
    - OAuth 2.0 authentication flow
    - Professional post creation
    - Engagement metrics collection
    - Rate limit handling
    - Error recovery and retry logic
    """
    
    # LinkedIn API v2 endpoints
    BASE_URL = "https://api.linkedin.com/v2"
    OAUTH_URL = "https://www.linkedin.com/oauth/v2"
    
    # LinkedIn API limits
    MAX_POST_LENGTH = 3000
    MAX_IMAGES_PER_POST = 9
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize LinkedIn client
        
        Args:
            client_id: LinkedIn OAuth 2.0 Client ID
            client_secret: LinkedIn OAuth 2.0 Client Secret
        """
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            logger.warning("LinkedIn OAuth credentials not provided. Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
        
        self.token_manager = get_token_manager()
        self.session = requests.Session()
        
        # Rate limiting tracking
        self.rate_limits = {}
        self.last_rate_limit_check = {}
        
        logger.info("LinkedIn client initialized")
    
    def get_oauth_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> Tuple[str, str]:
        """
        Get OAuth 2.0 authorization URL for user consent
        
        Args:
            redirect_uri: OAuth redirect URI
            state: Optional state parameter for CSRF protection
            
        Returns:
            Tuple of (authorization_url, state)
        """
        try:
            oauth = OAuth2Session(
                client_id=self.client_id,
                redirect_uri=redirect_uri,
                scope=["r_liteprofile", "r_emailaddress", "w_member_social", "r_member_social"]
            )
            
            authorization_url, state = oauth.authorization_url(
                f"{self.OAUTH_URL}/authorization",
                state=state
            )
            
            logger.info(f"Generated LinkedIn OAuth authorization URL for redirect_uri: {redirect_uri}")
            return authorization_url, state
            
        except Exception as e:
            logger.error(f"Failed to generate LinkedIn OAuth authorization URL: {e}")
            raise LinkedInAPIError(f"OAuth authorization URL generation failed: {e}")
    
    def exchange_code_for_tokens(self, authorization_code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            authorization_code: OAuth authorization code from callback
            redirect_uri: OAuth redirect URI used in authorization
            
        Returns:
            Dictionary containing token data
        """
        try:
            token_data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post(
                f"{self.OAUTH_URL}/accessToken",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"LinkedIn token exchange failed: {response.status_code} - {response.text}")
                raise LinkedInAPIError(f"Token exchange failed: {response.text}")
            
            token_response = response.json()
            
            # Add expiration timestamp
            if "expires_in" in token_response:
                token_response["expires_at"] = time.time() + token_response["expires_in"]
            
            logger.info("Successfully exchanged authorization code for LinkedIn tokens")
            return token_response
            
        except Exception as e:
            logger.error(f"LinkedIn token exchange failed: {e}")
            raise LinkedInAPIError(f"Token exchange failed: {e}")
    
    def _get_authenticated_session(self, access_token: str) -> requests.Session:
        """Get authenticated requests session"""
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202401",
            "X-Restli-Protocol-Version": "2.0.0"
        })
        return session
    
    def _check_rate_limit(self, endpoint: str) -> bool:
        """
        Check if we're within rate limits for an endpoint
        
        Args:
            endpoint: API endpoint to check
            
        Returns:
            True if within limits, False if rate limited
        """
        now = time.time()
        rate_limit_info = self.rate_limits.get(endpoint, {})
        
        # Check if rate limit has reset
        reset_time = rate_limit_info.get("reset_time", 0)
        if now >= reset_time:
            return True
        
        # Check remaining requests
        remaining = rate_limit_info.get("remaining", 1)
        return remaining > 0
    
    def _update_rate_limit(self, endpoint: str, response: requests.Response):
        """Update rate limit tracking from API response headers"""
        headers = response.headers
        
        self.rate_limits[endpoint] = {
            "limit": int(headers.get("X-RateLimit-Limit", 0)),
            "remaining": int(headers.get("X-RateLimit-Remaining", 0)),
            "reset_time": int(headers.get("X-RateLimit-Reset", 0))
        }
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get authenticated user information
        
        Args:
            access_token: OAuth access token
            
        Returns:
            Dictionary containing user information
        """
        try:
            session = self._get_authenticated_session(access_token)
            
            # Check rate limits
            if not self._check_rate_limit("people"):
                raise LinkedInAPIError("Rate limit exceeded for user info endpoint")
            
            response = session.get(
                f"{self.BASE_URL}/people/~",
                params={
                    "projection": "(id,firstName,lastName,profilePicture(displayImage~:playableStreams),headline,numConnections,numFollowers,industry)"
                }
            )
            
            self._update_rate_limit("people", response)
            
            if response.status_code != 200:
                logger.error(f"Failed to get LinkedIn user info: {response.status_code} - {response.text}")
                raise LinkedInAPIError(f"Failed to get user info: {response.text}")
            
            user_data = response.json()
            
            # Extract user information
            profile = {
                "id": user_data.get("id"),
                "first_name": user_data.get("firstName", {}).get("localized", {}).get("en_US", ""),
                "last_name": user_data.get("lastName", {}).get("localized", {}).get("en_US", ""),
                "headline": user_data.get("headline", {}).get("localized", {}).get("en_US", ""),
                "connections": user_data.get("numConnections", 0),
                "followers": user_data.get("numFollowers", 0),
                "industry": user_data.get("industry", {}).get("localized", {}).get("en_US", ""),
                "profile_image": self._extract_profile_image(user_data.get("profilePicture", {}))
            }
            
            logger.info(f"Retrieved LinkedIn user info for {profile['first_name']} {profile['last_name']}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn user info: {e}")
            raise LinkedInAPIError(f"Failed to get user info: {e}")
    
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
    
    def post_update(self, access_token: str, content: str, user_id: int, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """
        Post an update to LinkedIn
        
        Args:
            access_token: OAuth access token
            content: Post content (max 3000 characters)
            user_id: User ID for audit logging
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)
            
        Returns:
            Dictionary containing post response data
        """
        try:
            # Validate content length
            if len(content) > self.MAX_POST_LENGTH:
                raise LinkedInAPIError(f"Post content too long: {len(content)} > {self.MAX_POST_LENGTH}")
            
            session = self._get_authenticated_session(access_token)
            
            # Check rate limits
            if not self._check_rate_limit("ugcPosts"):
                raise LinkedInAPIError("Rate limit exceeded for posts endpoint")
            
            # Get user profile to get author URN
            user_info = self.get_user_info(access_token)
            author_urn = f"urn:li:person:{user_info['id']}"
            
            # Prepare post payload
            post_payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            # Post update
            response = session.post(
                f"{self.BASE_URL}/ugcPosts",
                json=post_payload
            )
            
            self._update_rate_limit("ugcPosts", response)
            
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to post LinkedIn update: {response.status_code} - {response.text}")
                raise LinkedInAPIError(f"Failed to post update: {response.text}")
            
            post_data = response.json()
            post_id = post_data.get("id", "")
            
            # Log successful posting
            log_content_event(
                AuditEventType.CONTENT_PUBLISHED,
                user_id=user_id,
                resource=f"linkedin_post_{post_id}",
                action="post_update",
                additional_data={
                    "post_id": post_id,
                    "content_length": len(content),
                    "visibility": visibility
                }
            )
            
            logger.info(f"Successfully posted LinkedIn update: {post_id}")
            return {
                "id": post_id,
                "text": content,
                "author_id": user_info['id'],
                "visibility": visibility,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to post LinkedIn update: {e}")
            
            # Log failed posting
            log_content_event(
                AuditEventType.CONTENT_PUBLISHED,
                user_id=user_id,
                resource="linkedin_post_failed",
                action="post_update",
                additional_data={
                    "error": str(e),
                    "content_length": len(content) if content else 0
                }
            )
            
            raise LinkedInAPIError(f"Failed to post update: {e}")
    
    def get_post_metrics(self, access_token: str, post_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for a specific LinkedIn post
        
        Args:
            access_token: OAuth access token
            post_id: LinkedIn post ID
            
        Returns:
            Dictionary containing post metrics
        """
        try:
            session = self._get_authenticated_session(access_token)
            
            # Check rate limits
            if not self._check_rate_limit("socialActions"):
                raise LinkedInAPIError("Rate limit exceeded for post metrics endpoint")
            
            # Get social actions for the post
            response = session.get(
                f"{self.BASE_URL}/socialActions/{post_id}",
                params={
                    "projection": "(totalSocialActionCounts)"
                }
            )
            
            self._update_rate_limit("socialActions", response)
            
            if response.status_code != 200:
                logger.error(f"Failed to get LinkedIn post metrics: {response.status_code} - {response.text}")
                # Return empty metrics if API call fails
                return {
                    "post_id": post_id,
                    "likes_count": 0,
                    "comments_count": 0,
                    "shares_count": 0,
                    "impressions_count": 0,
                    "engagement_rate": 0.0,
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            
            metrics_data = response.json()
            social_counts = metrics_data.get("totalSocialActionCounts", {})
            
            # Extract metrics
            likes_count = social_counts.get("numLikes", 0)
            comments_count = social_counts.get("numComments", 0)
            shares_count = social_counts.get("numShares", 0)
            
            # Calculate engagement (LinkedIn doesn't provide impressions in basic API)
            engagement_count = likes_count + comments_count + shares_count
            
            processed_metrics = {
                "post_id": post_id,
                "likes_count": likes_count,
                "comments_count": comments_count,
                "shares_count": shares_count,
                "impressions_count": 0,  # Not available in basic API
                "engagement_rate": 0.0,  # Cannot calculate without impressions
                "total_engagement": engagement_count,
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Retrieved LinkedIn metrics for post {post_id}: {engagement_count} total engagements")
            return processed_metrics
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn post metrics: {e}")
            # Return empty metrics on error
            return {
                "post_id": post_id,
                "likes_count": 0,
                "comments_count": 0,
                "shares_count": 0,
                "impressions_count": 0,
                "engagement_rate": 0.0,
                "retrieved_at": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def validate_connection(self, access_token: str) -> Dict[str, Any]:
        """
        Validate LinkedIn connection by making a test API call
        
        Args:
            access_token: OAuth access token
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Test connection by getting user info
            user_info = self.get_user_info(access_token)
            
            return {
                "is_valid": True,
                "user_id": user_info["id"],
                "display_name": f"{user_info['first_name']} {user_info['last_name']}".strip(),
                "headline": user_info.get("headline", ""),
                "connections_count": user_info.get("connections", 0),
                "followers_count": user_info.get("followers", 0),
                "industry": user_info.get("industry", ""),
                "validated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LinkedIn connection validation failed: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "validated_at": datetime.utcnow().isoformat()
            }
    
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
        
        if len(text) > self.MAX_POST_LENGTH:
            return False, f"Post content too long ({len(text)}/{self.MAX_POST_LENGTH} characters)"
        
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


# Helper functions for common operations

def create_linkedin_client() -> LinkedInClient:
    """Create and return a LinkedInClient instance"""
    return LinkedInClient()

def format_content_for_linkedin(content: str) -> str:
    """
    Format content specifically for LinkedIn's professional audience
    
    Args:
        content: Original content to format
        
    Returns:
        LinkedIn-optimized content
    """
    # Add line breaks for better readability
    if len(content) > 300:
        # Add paragraph breaks for longer content
        sentences = content.split('. ')
        formatted_sentences = []
        current_paragraph = ""
        
        for sentence in sentences:
            if len(current_paragraph + sentence) > 200:
                if current_paragraph:
                    formatted_sentences.append(current_paragraph.strip() + '.')
                    current_paragraph = sentence
                else:
                    formatted_sentences.append(sentence + '.')
            else:
                current_paragraph += sentence + '. ' if not sentence.endswith('.') else sentence + ' '
        
        if current_paragraph:
            formatted_sentences.append(current_paragraph.strip())
        
        content = '\n\n'.join(formatted_sentences)
    
    return content

# Global LinkedIn client instance
linkedin_client = LinkedInClient()