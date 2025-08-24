"""
Enhanced OpenAI Image Generation Service

This service uses the new OpenAI Responses API with image_generation tool
for superior social media content creation and multi-turn editing capabilities.
"""
import asyncio
import base64
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator, Union
from datetime import datetime
from pathlib import Path
import uuid

from openai import OpenAI, AsyncOpenAI
from backend.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class ImageGenerationService:
    """
    Enhanced image generation service using OpenAI's latest Responses API
    with image_generation tool for social media content creation.
    """
    
    def __init__(self):
        # Use xAI Grok for image generation
        self.client = OpenAI(
            api_key=settings.xai_api_key,
            base_url="https://api.x.ai/v1"
        )
        self.async_client = AsyncOpenAI(
            api_key=settings.xai_api_key,
            base_url="https://api.x.ai/v1"
        )
        
        # Platform-specific optimization prompts
        self.platform_styles = {
            "twitter": "modern, clean, minimalist design suitable for Twitter posts, 16:9 or square aspect ratio",
            "instagram": "vibrant, visually stunning, Instagram-optimized design with excellent composition",
            "facebook": "engaging, social media friendly, Facebook-style design that captures attention",
            "tiktok": "trendy, youthful, dynamic design perfect for TikTok content with bold visuals",
            "youtube": "professional thumbnail design with bold text and engaging visuals"
        }
        
        # Quality presets
        self.quality_presets = {
            "draft": {"quality": "low", "size": "1024x1024"},
            "standard": {"quality": "medium", "size": "1024x1024"},
            "premium": {"quality": "high", "size": "1024x1536"},
            "story": {"quality": "high", "size": "1024x1792"},
            "banner": {"quality": "high", "size": "1536x1024"}
        }

    def _enhance_prompt_for_platform(self, prompt: str, platform: str, 
                                   content_context: Optional[str] = None,
                                   industry_context: Optional[str] = None,
                                   tone: str = "professional") -> str:
        """Enhance the prompt with platform-specific optimizations."""
        
        # Base enhancement
        enhanced_prompt = f"Create a high-quality image: {prompt}"
        
        # Add platform styling
        if platform in self.platform_styles:
            enhanced_prompt += f" Style: {self.platform_styles[platform]}"
        
        # Add content context
        if content_context:
            enhanced_prompt += f" Content context: {content_context[:200]}"
        
        # Add industry context
        if industry_context:
            enhanced_prompt += f" Industry: {industry_context[:100]}"
        
        # Add tone guidance
        tone_styles = {
            "professional": "polished, sophisticated, business-appropriate",
            "casual": "relaxed, approachable, friendly",
            "humorous": "fun, playful, engaging with subtle humor",
            "inspiring": "motivational, uplifting, empowering",
            "educational": "clear, informative, easy to understand"
        }
        
        if tone in tone_styles:
            enhanced_prompt += f" Tone: {tone_styles[tone]}"
        
        return enhanced_prompt

    async def generate_image(self, 
                           prompt: str,
                           platform: str = "instagram",
                           quality_preset: str = "standard",
                           content_context: Optional[str] = None,
                           industry_context: Optional[str] = None,
                           tone: str = "professional",
                           custom_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a single image using the OpenAI Image Generation API.
        
        NOTE: This implementation uses the currently available OpenAI API (images.generate).
        TODO: Update to use client.responses.create with image_generation tool when available,
        as specified in /Users/jeffreyhacker/AI social media content agent/docs/api-references/openai-image-generation.md
        
        Args:
            prompt: Base image description
            platform: Target social media platform
            quality_preset: Quality/size preset (draft, standard, premium, story, banner)
            content_context: Additional context about the content
            industry_context: Industry-specific context
            tone: Desired tone for the image
            custom_options: Custom tool options (size, quality, format, etc.)
        
        Returns:
            Dict containing image data, metadata, and generation info
        """
        try:
            # Enhance prompt for the platform
            enhanced_prompt = self._enhance_prompt_for_platform(
                prompt, platform, content_context, industry_context, tone
            )
            
            # Get quality preset settings
            preset_config = self.quality_presets.get(quality_preset, self.quality_presets["standard"])
            
            # Prepare GPT Image 1 parameters
            tool_options = {
                "type": "image_generation",
                "size": preset_config.get("size", "1024x1024"),
                "quality": preset_config.get("quality", "standard")
            }
            
            # Override with custom options if provided
            if custom_options:
                tool_options.update(custom_options)
            
            # Use Grok 2 Image Generation via xAI API
            response = await asyncio.to_thread(
                self.client.images.generate,
                model="grok-2-image",
                prompt=enhanced_prompt,
                n=1,
                response_format="b64_json"  # Get base64 directly from Grok 2
            )
            
            # Extract base64 image data from response  
            if not response.data or len(response.data) == 0:
                raise Exception("No image data returned from Grok 2")
            
            image_base64 = response.data[0].b64_json
            if not image_base64:
                raise Exception("No base64 image data in Grok 2 response")
            
            # Generate unique filename and ID
            image_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_{timestamp}_{image_id[:8]}.png"
            
            return {
                "status": "success",
                "image_id": image_id,
                "response_id": image_id,  # Use our generated ID since DALL-E doesn't provide one
                "image_base64": image_base64,
                "image_data_url": f"data:image/png;base64,{image_base64}",
                "filename": filename,
                "prompt": {
                    "original": prompt,
                    "enhanced": enhanced_prompt,
                    "revised": enhanced_prompt  # Grok 2 doesn't revise prompts
                },
                "metadata": {
                    "platform": platform,
                    "quality_preset": quality_preset,
                    "tool_options": tool_options,
                    "model": "grok-2-image",
                    "generated_at": datetime.utcnow().isoformat(),
                    "content_context": content_context,
                    "industry_context": industry_context,
                    "tone": tone
                }
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "prompt": prompt,
                "platform": platform
            }

    async def edit_image(self,
                        edit_prompt: str,
                        previous_response_id: Optional[str] = None,
                        previous_image_id: Optional[str] = None,
                        platform: str = "instagram",
                        quality_preset: str = "standard") -> Dict[str, Any]:
        """
        Edit an existing image using multi-turn capabilities.
        
        Args:
            edit_prompt: Description of how to edit the image
            previous_response_id: ID of previous response to continue from
            previous_image_id: ID of specific image to edit
            platform: Target platform
            quality_preset: Quality preset
        
        Returns:
            Dict containing edited image data and metadata
        """
        try:
            # Prepare tool options
            tool_options = self.quality_presets.get(quality_preset, self.quality_presets["standard"])
            
            if previous_response_id:
                # Continue from previous response
                response = await asyncio.to_thread(
                    self.client.responses.create,
                    model="gpt-image-1",
                    previous_response_id=previous_response_id,
                    input=f"Edit the image: {edit_prompt}",
                    tools=[{
                        "type": "image_generation",
                        **tool_options
                    }]
                )
            elif previous_image_id:
                # Edit specific image by ID
                response = await asyncio.to_thread(
                    self.client.responses.create,
                    model="gpt-image-1",
                    input=[
                        {
                            "role": "user",
                            "content": [{"type": "input_text", "text": f"Edit the image: {edit_prompt}"}]
                        },
                        {
                            "type": "image_generation_call",
                            "id": previous_image_id
                        }
                    ],
                    tools=[{
                        "type": "image_generation",
                        **tool_options
                    }]
                )
            else:
                raise ValueError("Either previous_response_id or previous_image_id must be provided")
            
            # Extract edited image
            image_calls = [
                output for output in response.output
                if output.type == "image_generation_call"
            ]
            
            if not image_calls:
                raise Exception("No edited image was generated")
            
            image_call = image_calls[0]
            
            # Generate unique filename for edited image
            image_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_edited_{timestamp}_{image_id[:8]}.png"
            
            return {
                "status": "success",
                "image_id": image_call.id,
                "response_id": response.id,
                "image_base64": image_call.result,
                "image_data_url": f"data:image/png;base64,{image_call.result}",
                "filename": filename,
                "edit_prompt": edit_prompt,
                "revised_prompt": getattr(image_call, 'revised_prompt', edit_prompt),
                "metadata": {
                    "platform": platform,
                    "quality_preset": quality_preset,
                    "tool_options": tool_options,
                    "model": "grok-2-image",
                    "edited_at": datetime.utcnow().isoformat(),
                    "previous_response_id": previous_response_id,
                    "previous_image_id": previous_image_id
                }
            }
            
        except Exception as e:
            logger.error(f"Image editing failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "edit_prompt": edit_prompt
            }

    async def generate_streaming_image(self,
                                     prompt: str,
                                     platform: str = "instagram",
                                     partial_images: int = 2,
                                     quality_preset: str = "standard") -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate image with streaming partial results for better UX.
        
        Args:
            prompt: Image description
            platform: Target platform
            partial_images: Number of partial images to stream (1-3)
            quality_preset: Quality preset
        
        Yields:
            Dict containing partial image data and progress info
        """
        try:
            enhanced_prompt = self._enhance_prompt_for_platform(prompt, platform)
            tool_options = self.quality_presets.get(quality_preset, self.quality_presets["standard"])
            
            # Use Responses API with streaming as per OpenAI documentation
            stream = await asyncio.to_thread(
                self.client.responses.create,
                model="gpt-image-1",
                input=enhanced_prompt,
                tools=[{
                    "type": "image_generation",
                    "partial_images": partial_images,
                    **tool_options
                }],
                stream=True
            )
            
            for event in stream:
                if event.type == "image_generation.partial_image":
                    yield {
                        "status": "partial",
                        "partial_index": event.partial_image_index,
                        "total_partials": partial_images,
                        "image_base64": event.b64_json,
                        "image_data_url": f"data:image/png;base64,{event.b64_json}",
                        "progress": (event.partial_image_index + 1) / partial_images,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                elif event.type == "image_generation.done":
                    yield {
                        "status": "completed",
                        "final_image_base64": event.b64_json,
                        "final_image_data_url": f"data:image/png;base64,{event.b64_json}",
                        "prompt": enhanced_prompt,
                        "platform": platform,
                        "completed_at": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Streaming image generation failed: {str(e)}")
            yield {
                "status": "error",
                "error": str(e),
                "prompt": prompt,
                "platform": platform
            }

    async def generate_content_images(self,
                                    content_text: str,
                                    platforms: List[str],
                                    image_count: int = 1,
                                    industry_context: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate multiple images optimized for different platforms based on content.
        
        Args:
            content_text: The social media content text
            platforms: List of target platforms
            image_count: Number of images per platform
            industry_context: Industry context for styling
        
        Returns:
            Dict with platform keys and lists of generated images
        """
        results = {}
        
        # Generate base prompt from content
        base_prompt = f"Create a visual representation for this social media content: {content_text[:200]}"
        
        for platform in platforms:
            platform_images = []
            
            for i in range(image_count):
                # Add variation to each image
                variation_prompt = base_prompt
                if i > 0:
                    variations = [
                        "with a different composition",
                        "from an alternative perspective", 
                        "with different color scheme",
                        "in a complementary style"
                    ]
                    variation_prompt += f" {variations[i % len(variations)]}"
                
                result = await self.generate_image(
                    prompt=variation_prompt,
                    platform=platform,
                    content_context=content_text,
                    industry_context=industry_context
                )
                
                platform_images.append(result)
                
                # Brief delay to avoid rate limits
                await asyncio.sleep(0.5)
            
            results[platform] = platform_images
        
        return results

    def save_image_to_file(self, image_base64: str, filepath: str) -> bool:
        """Save base64 image data to file."""
        try:
            image_data = base64.b64decode(image_base64)
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save image to {filepath}: {str(e)}")
            return False

# Global service instance
image_generation_service = ImageGenerationService()