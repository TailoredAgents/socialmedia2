"""
X (Twitter) publishing adapter for Phase 8
Handles X API v2 publishing with proper error mapping
"""
import logging
from typing import Tuple, Optional, List
import httpx
import base64
from datetime import datetime

from backend.db.models import SocialConnection
from backend.core.encryption import decrypt_token
from backend.services.rate_limit import RetryableError, FatalError
from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class XAdapter:
    """Adapter for publishing to X (Twitter)"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.twitter.com/2"
    
    async def publish(
        self, 
        connection: SocialConnection, 
        content: str, 
        media_urls: List[str]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Publish content to X platform
        
        Args:
            connection: SocialConnection with X tokens
            content: Content text to publish (tweet)
            media_urls: List of media URLs
            
        Returns:
            Tuple of (success, platform_post_id, error_message)
            
        Raises:
            RetryableError: For 429, 5xx, network errors
            FatalError: For auth failures, policy violations
        """
        try:
            # Validate connection
            if connection.platform != "x":
                raise FatalError(f"Invalid platform: {connection.platform}")
            
            # Get access token
            access_token = connection.access_tokens.get("access_token")
            if not access_token:
                raise FatalError("No access token found")
            
            # Decrypt token (don't log the actual token)
            try:
                decrypted_token = decrypt_token(access_token)
            except Exception as e:
                raise FatalError(f"Failed to decrypt access token: {str(e)}")
            
            logger.info(
                f"Publishing to X for connection {connection.id}, "
                f"content length: {len(content)}, media count: {len(media_urls)}"
            )
            
            # Prepare tweet data
            tweet_data = {
                "text": content
            }
            
            # Upload media if provided
            media_ids = []
            if media_urls:
                logger.info(f"Processing {len(media_urls)} media items for X")
                for media_url in media_urls:
                    try:
                        # Download media from URL
                        async with httpx.AsyncClient(timeout=30.0) as media_client:
                            media_response = await media_client.get(media_url)
                            if media_response.status_code == 200:
                                media_data = media_response.content
                                media_type = media_response.headers.get("content-type", "image/jpeg")
                                
                                # Upload to X
                                success, media_id, upload_error = await self.upload_media(
                                    connection, media_data, media_type
                                )
                                
                                if success and media_id:
                                    media_ids.append(media_id)
                                    logger.info(f"Successfully uploaded media: {media_id}")
                                else:
                                    logger.warning(f"Failed to upload media from {media_url}: {upload_error}")
                            else:
                                logger.warning(f"Failed to download media from {media_url}: {media_response.status_code}")
                    except Exception as e:
                        logger.error(f"Error processing media {media_url}: {e}")
                        # Continue with other media items
                        continue
            
            # Add media IDs to tweet data
            if media_ids:
                tweet_data["media"] = {"media_ids": media_ids}
                logger.info(f"Added {len(media_ids)} media items to tweet")
            
            # Prepare request
            url = f"{self.base_url}/tweets"
            
            headers = {
                "Authorization": f"Bearer {decrypted_token}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(url, json=tweet_data, headers=headers)
                    
                    # Log request without sensitive data
                    logger.debug(
                        f"X API request: POST {url} (token omitted), "
                        f"status: {response.status_code}"
                    )
                    
                    # Handle different response status codes
                    if response.status_code == 201:
                        # Success for tweet creation
                        result = response.json()
                        tweet_id = result.get("data", {}).get("id")
                        
                        if not tweet_id:
                            raise FatalError("No tweet ID returned from X API")
                        
                        logger.info(f"Successfully published to X: {tweet_id}")
                        return True, tweet_id, None
                    
                    elif response.status_code == 429:
                        # Rate limiting - should retry
                        reset_time = response.headers.get("x-rate-limit-reset")
                        error_msg = f"Rate limited by X API (reset: {reset_time})"
                        logger.warning(f"X API rate limit: {error_msg}")
                        raise RetryableError(error_msg)
                    
                    elif response.status_code in [500, 502, 503, 504]:
                        # Server errors - should retry
                        error_msg = f"X API server error: {response.status_code}"
                        logger.warning(f"X API server error: {error_msg}")
                        raise RetryableError(error_msg)
                    
                    elif response.status_code == 401:
                        # Authentication error - fatal
                        error_msg = "Authentication failed - token may be expired or invalid"
                        logger.error(f"X API auth error: {error_msg}")
                        raise FatalError(error_msg)
                    
                    elif response.status_code == 403:
                        # Forbidden - could be permissions or policy violation
                        try:
                            error_data = response.json()
                            error_detail = error_data.get("detail", "Permission denied")
                            
                            # Check for specific error types
                            if "suspended" in error_detail.lower():
                                error_msg = "Account suspended"
                                raise FatalError(error_msg)
                            elif "duplicate" in error_detail.lower():
                                error_msg = "Duplicate tweet detected"
                                raise FatalError(error_msg)
                            else:
                                error_msg = f"Permission denied: {error_detail}"
                                raise FatalError(error_msg)
                                
                        except (ValueError, KeyError):
                            error_msg = "Permission denied by X API"
                            logger.error(f"X API permission error: {error_msg}")
                            raise FatalError(error_msg)
                    
                    elif response.status_code == 400:
                        # Bad request - check if retryable
                        try:
                            error_data = response.json()
                            errors = error_data.get("errors", [])
                            
                            # Check for specific error types
                            for error in errors:
                                error_type = error.get("type", "")
                                
                                # Some errors are retryable (temporary issues)
                                if error_type in ["temporarily_unavailable", "rate_limit_exceeded"]:
                                    error_msg = f"Temporary X API error: {error.get('message', 'Unknown')}"
                                    logger.warning(f"Retryable X API error: {error_msg}")
                                    raise RetryableError(error_msg)
                                else:
                                    # Assume fatal for other errors
                                    error_msg = f"X API error: {error.get('message', 'Bad request')}"
                                    logger.error(f"Fatal X API error: {error_msg}")
                                    raise FatalError(error_msg)
                            
                            # No specific errors found
                            error_msg = "Bad request to X API"
                            raise FatalError(error_msg)
                                
                        except (ValueError, KeyError):
                            # Can't parse error - assume fatal
                            error_msg = f"Bad request to X API: {response.status_code}"
                            logger.error(f"X API bad request: {error_msg}")
                            raise FatalError(error_msg)
                    
                    elif response.status_code == 422:
                        # Unprocessable entity - content issues, usually fatal
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("detail", "Content validation failed")
                            logger.error(f"X API content validation error: {error_msg}")
                            raise FatalError(f"Content validation failed: {error_msg}")
                        except (ValueError, KeyError):
                            error_msg = "Content validation failed"
                            raise FatalError(error_msg)
                    
                    else:
                        # Other HTTP errors - assume retryable
                        error_msg = f"Unexpected X API response: {response.status_code}"
                        logger.warning(f"X API unexpected response: {error_msg}")
                        raise RetryableError(error_msg)
                        
                except httpx.TimeoutException:
                    error_msg = "X API request timeout"
                    logger.warning(f"X API timeout: {error_msg}")
                    raise RetryableError(error_msg)
                
                except httpx.NetworkError as e:
                    error_msg = f"X API network error: {str(e)}"
                    logger.warning(f"X API network error: {error_msg}")
                    raise RetryableError(error_msg)
                
                except httpx.HTTPError as e:
                    error_msg = f"X API HTTP error: {str(e)}"
                    logger.warning(f"X API HTTP error: {error_msg}")
                    raise RetryableError(error_msg)
            
        except RetryableError:
            # Re-raise retryable errors
            raise
            
        except FatalError:
            # Re-raise fatal errors
            raise
            
        except Exception as e:
            # Unexpected errors - log and treat as retryable
            error_msg = f"Unexpected error in X adapter: {str(e)}"
            logger.error(f"X adapter unexpected error: {error_msg}")
            raise RetryableError(error_msg)
    
    def validate_connection(self, connection: SocialConnection) -> Tuple[bool, Optional[str]]:
        """
        Validate that connection has required data for publishing
        
        Args:
            connection: SocialConnection to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if connection.platform != "x":
            return False, f"Invalid platform: {connection.platform}"
        
        if not connection.access_tokens.get("access_token"):
            return False, "No access token found"
        
        if not connection.is_active:
            return False, "Connection is not active"
        
        if connection.revoked_at:
            return False, "Connection has been revoked"
        
        return True, None
    
    def get_platform_limits(self) -> dict:
        """
        Get platform-specific limits
        
        Returns:
            Dictionary with platform limits
        """
        return {
            "max_content_length": 280,  # Twitter character limit
            "max_media_count": 4,
            "supported_media_types": ["image/jpeg", "image/png", "image/gif", "video/mp4"],
            "rate_limits": {
                "posts_per_15min": 300,  # X API v2 limit
                "posts_per_day": 2400
            }
        }
    
    async def upload_media(
        self, 
        connection: SocialConnection, 
        media_data: bytes,
        media_type: str = "image/jpeg"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload media to X platform using v1.1 media upload API
        
        Args:
            connection: SocialConnection with X tokens
            media_data: Raw media bytes
            media_type: MIME type of the media
            
        Returns:
            Tuple of (success, media_id, error_message)
        """
        try:
            # Validate connection
            if connection.platform != "x":
                raise FatalError(f"Invalid platform: {connection.platform}")
            
            # Get access token
            access_token = connection.access_tokens.get("access_token")
            if not access_token:
                raise FatalError("No access token found")
            
            # Decrypt token
            try:
                decrypted_token = decrypt_token(access_token)
            except Exception as e:
                raise FatalError(f"Failed to decrypt access token: {str(e)}")
            
            logger.info(f"Uploading media to X, size: {len(media_data)} bytes, type: {media_type}")
            
            # X API v1.1 media upload endpoint
            upload_url = "https://upload.twitter.com/1.1/media/upload.json"
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {decrypted_token}"
            }
            
            # Determine media category
            media_category = "tweet_image" if media_type.startswith("image") else "tweet_video"
            
            # Prepare form data
            files = {
                "media": ("image.jpg", media_data, media_type)
            }
            
            data = {
                "media_category": media_category
            }
            
            # Upload media
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    response = await client.post(
                        upload_url, 
                        headers=headers,
                        files=files,
                        data=data
                    )
                    
                    logger.debug(f"X media upload response: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        media_id = str(result.get("media_id"))
                        
                        if not media_id:
                            raise Exception("No media_id returned from X API")
                        
                        logger.info(f"Successfully uploaded media to X: {media_id}")
                        return True, media_id, None
                    
                    elif response.status_code == 429:
                        # Rate limiting
                        error_msg = "Rate limited by X media upload API"
                        logger.warning(error_msg)
                        raise RetryableError(error_msg)
                    
                    elif response.status_code in [500, 502, 503, 504]:
                        # Server errors
                        error_msg = f"X media upload server error: {response.status_code}"
                        logger.warning(error_msg)
                        raise RetryableError(error_msg)
                    
                    elif response.status_code == 401:
                        # Authentication error
                        error_msg = "Authentication failed for media upload"
                        logger.error(error_msg)
                        raise FatalError(error_msg)
                    
                    elif response.status_code == 403:
                        # Forbidden - check specific error
                        try:
                            error_data = response.json()
                            error_detail = error_data.get("errors", [{}])[0].get("message", "Permission denied")
                            error_msg = f"Media upload forbidden: {error_detail}"
                        except:
                            error_msg = "Media upload permission denied"
                        
                        logger.error(error_msg)
                        raise FatalError(error_msg)
                    
                    elif response.status_code == 400:
                        # Bad request - usually media format issues
                        try:
                            error_data = response.json()
                            error_detail = error_data.get("errors", [{}])[0].get("message", "Bad request")
                            error_msg = f"Media upload failed: {error_detail}"
                        except:
                            error_msg = "Invalid media format or size"
                        
                        logger.error(error_msg)
                        raise FatalError(error_msg)
                    
                    else:
                        # Other errors
                        error_msg = f"Unexpected media upload response: {response.status_code}"
                        logger.warning(error_msg)
                        raise RetryableError(error_msg)
                        
                except httpx.TimeoutException:
                    error_msg = "Media upload timeout"
                    logger.warning(error_msg)
                    raise RetryableError(error_msg)
                
                except httpx.NetworkError as e:
                    error_msg = f"Media upload network error: {str(e)}"
                    logger.warning(error_msg)
                    raise RetryableError(error_msg)
                
        except RetryableError:
            raise
        except FatalError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error in X media upload: {str(e)}"
            logger.error(error_msg)
            raise RetryableError(error_msg)