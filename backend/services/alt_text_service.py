"""
Alt-text generation service using OpenAI Vision for accessibility
Implements Grok 4's recommendations for automatic alt-text generation
"""
import logging
import base64
from typing import Optional, Dict, Any
from openai import AsyncOpenAI

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AltTextService:
    """
    Service for generating descriptive alt-text for images using OpenAI Vision
    Ensures accessibility compliance and better social media engagement
    """
    
    def __init__(self):
        # Initialize OpenAI client for alt-text generation
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured. Alt-text generation will be unavailable.")
            self.client = None
        else:
            try:
                self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("Alt-text service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize alt-text service: {e}")
                self.client = None
    
    async def generate_alt_text(
        self, 
        image_data: bytes, 
        context: Optional[str] = None,
        platform: str = "instagram",
        max_length: int = 125  # Twitter's alt-text limit
    ) -> Dict[str, Any]:
        """
        Generate descriptive alt-text for an image using OpenAI Vision
        
        Args:
            image_data: Raw image bytes
            context: Optional context about the image content
            platform: Target platform (affects style and length)
            max_length: Maximum alt-text length
            
        Returns:
            Dict containing alt-text and metadata
        """
        if not self.client:
            return {
                "alt_text": "Image description unavailable",
                "status": "error",
                "error": "Alt-text service not available"
            }
        
        try:
            # Convert image to base64 for OpenAI Vision API
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create platform-specific prompt
            prompt = self._create_alt_text_prompt(context, platform, max_length)
            
            # Call OpenAI Vision API
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4 with vision capabilities
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "low"  # Reduce cost while maintaining quality
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150,
                temperature=0.3  # Lower temperature for more consistent descriptions
            )
            
            if not response.choices:
                raise Exception("No response from OpenAI Vision API")
            
            alt_text = response.choices[0].message.content.strip()
            
            # Ensure it fits within length constraints
            if len(alt_text) > max_length:
                alt_text = alt_text[:max_length-3] + "..."
            
            # Clean up common issues
            alt_text = self._clean_alt_text(alt_text)
            
            return {
                "alt_text": alt_text,
                "status": "success",
                "platform": platform,
                "length": len(alt_text),
                "max_length": max_length,
                "model_used": "gpt-4o-vision"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate alt-text: {e}")
            
            # Provide fallback alt-text
            fallback_text = self._generate_fallback_alt_text(context, platform)
            
            return {
                "alt_text": fallback_text,
                "status": "fallback",
                "error": str(e),
                "platform": platform,
                "length": len(fallback_text)
            }
    
    def _create_alt_text_prompt(self, context: Optional[str], platform: str, max_length: int) -> str:
        """Create platform-specific prompt for alt-text generation"""
        
        base_prompt = f"""Please provide a concise, descriptive alt-text for this image that would be suitable for {platform}. 

The alt-text should:
1. Be descriptive but concise (max {max_length} characters)
2. Focus on the main visual elements and their purpose
3. Be helpful for screen readers and accessibility
4. Avoid starting with "Image of" or "Picture of"
5. Include relevant details that convey the image's meaning and context

"""
        
        if context:
            base_prompt += f"Additional context: {context[:200]}\n\n"
        
        # Platform-specific guidelines
        platform_guidelines = {
            "instagram": "Focus on aesthetic elements, mood, and visual appeal.",
            "twitter": "Be very concise and focus on key information.",
            "facebook": "Include context that would help understand the post's purpose.",
            "linkedin": "Focus on professional context and business relevance.",
            "tiktok": "Describe dynamic elements and visual appeal."
        }
        
        if platform in platform_guidelines:
            base_prompt += platform_guidelines[platform] + "\n\n"
        
        base_prompt += "Please provide only the alt-text description, no additional formatting or explanation:"
        
        return base_prompt
    
    def _clean_alt_text(self, alt_text: str) -> str:
        """Clean and optimize alt-text"""
        # Remove common prefixes that screen readers don't need
        prefixes_to_remove = [
            "Image of ", "Picture of ", "Photo of ", "A picture of ", "An image of ",
            "This image shows ", "The image depicts ", "Image shows ", "Photo shows "
        ]
        
        cleaned = alt_text
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):]
                break
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        # Remove excessive punctuation
        cleaned = cleaned.replace("...", ".")
        
        # Ensure it ends with a period if it doesn't already
        if cleaned and not cleaned.endswith(('.', '!', '?')):
            cleaned += "."
        
        return cleaned.strip()
    
    def _generate_fallback_alt_text(self, context: Optional[str], platform: str) -> str:
        """Generate simple fallback alt-text when API fails"""
        if context:
            # Use context to create basic alt-text
            context_cleaned = context[:100].strip()
            return f"Image related to: {context_cleaned}"
        
        # Generic fallback based on platform
        platform_fallbacks = {
            "instagram": "Social media image",
            "twitter": "Tweet image",
            "facebook": "Social media post image",
            "linkedin": "Professional content image",
            "tiktok": "Video thumbnail image"
        }
        
        return platform_fallbacks.get(platform, "Social media image")
    
    def validate_alt_text(self, alt_text: str, platform: str = "instagram") -> Dict[str, Any]:
        """
        Validate alt-text quality and provide recommendations
        
        Args:
            alt_text: Alt-text to validate
            platform: Target platform
            
        Returns:
            Dict with validation results and recommendations
        """
        # Platform-specific length limits
        length_limits = {
            "twitter": 1000,  # Twitter's actual limit
            "instagram": 125,  # Practical limit for readability
            "facebook": 125,
            "linkedin": 120,
            "tiktok": 100
        }
        
        max_length = length_limits.get(platform, 125)
        
        validation = {
            "is_valid": True,
            "issues": [],
            "recommendations": [],
            "length": len(alt_text),
            "max_length": max_length,
            "platform": platform
        }
        
        # Length validation
        if len(alt_text) > max_length:
            validation["is_valid"] = False
            validation["issues"].append(f"Too long ({len(alt_text)}/{max_length} characters)")
            validation["recommendations"].append("Shorten the description while keeping key details")
        
        if len(alt_text) < 10:
            validation["is_valid"] = False
            validation["issues"].append("Too short to be descriptive")
            validation["recommendations"].append("Add more descriptive details")
        
        # Content validation
        if not alt_text.strip():
            validation["is_valid"] = False
            validation["issues"].append("Empty alt-text")
            validation["recommendations"].append("Provide a meaningful description")
        
        # Check for poor practices
        poor_starts = ["image of", "picture of", "photo of", "a image", "an image"]
        if any(alt_text.lower().startswith(start) for start in poor_starts):
            validation["recommendations"].append("Avoid starting with 'Image of' or similar phrases")
        
        if "image" in alt_text.lower() or "picture" in alt_text.lower() or "photo" in alt_text.lower():
            validation["recommendations"].append("Focus on describing content rather than mentioning it's an image")
        
        return validation


# Global service instance
alt_text_service = AltTextService()