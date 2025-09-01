"""
Enhanced image processing service for social media optimization
Implements Grok 4's recommendations for aspect ratio, quality, and platform optimization
"""
import logging
import base64
import io
from typing import Dict, Tuple, Optional, List
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import asyncio
from pathlib import Path

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ImageProcessingService:
    """
    Advanced image processing for social media content optimization
    Based on Grok 4's analysis and best practices research
    """
    
    # Platform-specific aspect ratios and dimensions
    PLATFORM_SPECS = {
        "instagram": {
            "square": (1080, 1080),
            "portrait": (1080, 1350),
            "story": (1080, 1920),
            "aspect_ratios": ["1:1", "4:5", "9:16"]
        },
        "twitter": {
            "default": (1200, 675),  # 16:9
            "square": (1200, 1200),
            "header": (1500, 500),
            "aspect_ratios": ["16:9", "1:1", "3:1"]
        },
        "facebook": {
            "default": (1200, 630),  # ~1.9:1
            "square": (1200, 1200),
            "cover": (1640, 859),
            "aspect_ratios": ["1.9:1", "1:1", "1.91:1"]
        },
        "linkedin": {
            "default": (1200, 627),  # 1.91:1
            "square": (1200, 1200),
            "cover": (1584, 396),
            "aspect_ratios": ["1.91:1", "1:1", "4:1"]
        },
        "tiktok": {
            "default": (1080, 1920),  # 9:16 vertical
            "square": (1080, 1080),
            "aspect_ratios": ["9:16", "1:1"]
        },
        "youtube": {
            "thumbnail": (1280, 720),  # 16:9
            "banner": (2560, 1440),
            "aspect_ratios": ["16:9", "16:10"]
        }
    }
    
    # Quality enhancement settings
    QUALITY_SETTINGS = {
        "draft": {
            "compression": 85,
            "sharpen": False,
            "enhance_color": False,
            "max_size": (1024, 1024)
        },
        "standard": {
            "compression": 90,
            "sharpen": True,
            "enhance_color": True,
            "max_size": (1200, 1200)
        },
        "premium": {
            "compression": 95,
            "sharpen": True,
            "enhance_color": True,
            "enhance_contrast": True,
            "max_size": (1920, 1920)
        },
        "story": {
            "compression": 90,
            "sharpen": True,
            "enhance_color": True,
            "max_size": (1080, 1920)
        },
        "banner": {
            "compression": 95,
            "sharpen": True,
            "enhance_color": True,
            "enhance_contrast": True,
            "max_size": (2048, 1024)
        }
    }

    def __init__(self):
        self.temp_dir = Path("uploads/temp/images")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def resize_for_platform(
        self, 
        image_data: bytes, 
        platform: str, 
        format_type: str = "default",
        quality_preset: str = "standard"
    ) -> Tuple[bytes, Dict[str, any]]:
        """
        Resize and optimize image for specific platform requirements
        
        Args:
            image_data: Raw image bytes
            platform: Target social media platform
            format_type: Platform format (default, square, story, etc.)
            quality_preset: Quality level for optimization
            
        Returns:
            Tuple of (processed_image_bytes, metadata)
        """
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            original_size = image.size
            
            # Convert to RGB if needed (handles RGBA, P modes)
            if image.mode != 'RGB':
                # Handle transparency by adding white background
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image, mask=image.split()[-1])
                    image = background
                else:
                    image = image.convert('RGB')
            
            # Get platform specifications
            platform_spec = self.PLATFORM_SPECS.get(platform, self.PLATFORM_SPECS["instagram"])
            target_size = platform_spec.get(format_type, platform_spec["default"])
            
            # Calculate optimal resize maintaining aspect ratio
            processed_image = self._smart_resize(image, target_size)
            
            # Apply quality enhancements
            processed_image = self._enhance_image_quality(processed_image, quality_preset)
            
            # Save to bytes with optimization
            output_buffer = io.BytesIO()
            quality_settings = self.QUALITY_SETTINGS[quality_preset]
            
            processed_image.save(
                output_buffer,
                format="JPEG",
                quality=quality_settings["compression"],
                optimize=True,
                progressive=True
            )
            
            processed_bytes = output_buffer.getvalue()
            
            metadata = {
                "original_size": original_size,
                "processed_size": processed_image.size,
                "platform": platform,
                "format_type": format_type,
                "quality_preset": quality_preset,
                "file_size_bytes": len(processed_bytes),
                "compression_ratio": len(image_data) / len(processed_bytes) if len(processed_bytes) > 0 else 1.0
            }
            
            logger.info(f"Image processed for {platform}: {original_size} → {processed_image.size}")
            
            return processed_bytes, metadata
            
        except Exception as e:
            logger.error(f"Failed to process image for {platform}: {e}")
            # Return original image as fallback
            return image_data, {"error": str(e), "fallback": True}

    def _smart_resize(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        Intelligently resize image maintaining aspect ratio with cropping if needed
        """
        original_width, original_height = image.size
        target_width, target_height = target_size
        
        # Calculate aspect ratios
        original_ratio = original_width / original_height
        target_ratio = target_width / target_height
        
        if abs(original_ratio - target_ratio) < 0.01:
            # Aspect ratios are very similar, just resize
            return image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Need to crop to match aspect ratio
        if original_ratio > target_ratio:
            # Original is wider, crop sides
            new_width = int(original_height * target_ratio)
            left = (original_width - new_width) // 2
            image = image.crop((left, 0, left + new_width, original_height))
        else:
            # Original is taller, crop top/bottom
            new_height = int(original_width / target_ratio)
            top = (original_height - new_height) // 2
            image = image.crop((0, top, original_width, top + new_height))
        
        # Now resize to target size
        return image.resize(target_size, Image.Resampling.LANCZOS)

    def _enhance_image_quality(self, image: Image.Image, quality_preset: str) -> Image.Image:
        """
        Apply quality enhancements based on preset
        """
        settings = self.QUALITY_SETTINGS.get(quality_preset, self.QUALITY_SETTINGS["standard"])
        
        enhanced_image = image
        
        # Sharpen if requested
        if settings.get("sharpen", False):
            enhanced_image = enhanced_image.filter(ImageFilter.UnsharpMask(
                radius=1.0, percent=150, threshold=3
            ))
        
        # Enhance color if requested
        if settings.get("enhance_color", False):
            color_enhancer = ImageEnhance.Color(enhanced_image)
            enhanced_image = color_enhancer.enhance(1.1)  # 10% more vibrant
        
        # Enhance contrast if requested
        if settings.get("enhance_contrast", False):
            contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = contrast_enhancer.enhance(1.05)  # 5% more contrast
        
        return enhanced_image

    def add_watermark(
        self, 
        image_data: bytes, 
        watermark_text: str, 
        position: str = "bottom_right",
        opacity: float = 0.7
    ) -> bytes:
        """
        Add text watermark to image
        
        Args:
            image_data: Original image bytes
            watermark_text: Text to add as watermark
            position: Position (bottom_right, bottom_left, top_right, top_left, center)
            opacity: Watermark opacity (0.0 to 1.0)
            
        Returns:
            Image bytes with watermark
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Create watermark overlay
            overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Try to load a nice font, fallback to default
            try:
                # Common system fonts
                font_paths = [
                    "/System/Library/Fonts/Arial.ttf",  # macOS
                    "/usr/share/fonts/truetype/arial.ttf",  # Linux
                    "C:/Windows/Fonts/arial.ttf"  # Windows
                ]
                font = None
                for font_path in font_paths:
                    if Path(font_path).exists():
                        font = ImageFont.truetype(font_path, 24)
                        break
                if font is None:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            text_width, text_height = draw.textbbox((0, 0), watermark_text, font=font)[2:]
            
            positions = {
                "bottom_right": (image.width - text_width - 20, image.height - text_height - 20),
                "bottom_left": (20, image.height - text_height - 20),
                "top_right": (image.width - text_width - 20, 20),
                "top_left": (20, 20),
                "center": ((image.width - text_width) // 2, (image.height - text_height) // 2)
            }
            
            text_position = positions.get(position, positions["bottom_right"])
            
            # Draw watermark with opacity
            alpha = int(255 * opacity)
            draw.text(text_position, watermark_text, font=font, fill=(255, 255, 255, alpha))
            
            # Combine with original image
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            watermarked = Image.alpha_composite(image, overlay)
            
            # Convert back to RGB for JPEG
            if watermarked.mode == 'RGBA':
                background = Image.new('RGB', watermarked.size, (255, 255, 255))
                background.paste(watermarked, mask=watermarked.split()[-1])
                watermarked = background
            
            # Save to bytes
            output_buffer = io.BytesIO()
            watermarked.save(output_buffer, format="JPEG", quality=90, optimize=True)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to add watermark: {e}")
            return image_data  # Return original on error

    def validate_image_quality(self, image_data: bytes) -> Dict[str, any]:
        """
        Validate image quality and provide recommendations
        
        Returns:
            Dict with quality metrics and recommendations
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            quality_metrics = {
                "size": image.size,
                "format": image.format,
                "mode": image.mode,
                "file_size_bytes": len(image_data),
                "aspect_ratio": width / height,
                "is_high_resolution": width >= 1080 and height >= 1080,
                "is_square": abs(width - height) < 50,  # Allow some tolerance
                "quality_score": 0,
                "issues": [],
                "recommendations": []
            }
            
            # Calculate quality score (0-100)
            score = 70  # Base score
            
            # Resolution scoring
            if width >= 1920 and height >= 1080:
                score += 20
            elif width >= 1080 and height >= 1080:
                score += 10
            else:
                quality_metrics["issues"].append("Low resolution")
                quality_metrics["recommendations"].append("Use higher resolution images (min 1080px)")
            
            # File size scoring
            file_size_mb = len(image_data) / (1024 * 1024)
            if 0.1 <= file_size_mb <= 5:  # Good range
                score += 10
            elif file_size_mb > 10:
                quality_metrics["issues"].append("Large file size")
                quality_metrics["recommendations"].append("Optimize image compression")
            
            # Format scoring
            if image.format in ['JPEG', 'PNG']:
                score += 0  # Standard formats
            else:
                quality_metrics["issues"].append(f"Unusual format: {image.format}")
                quality_metrics["recommendations"].append("Convert to JPEG or PNG")
            
            quality_metrics["quality_score"] = min(100, max(0, score))
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Failed to validate image quality: {e}")
            return {
                "error": str(e),
                "quality_score": 0,
                "issues": ["Failed to analyze image"],
                "recommendations": ["Check image file integrity"]
            }

    def get_platform_recommendations(self, platform: str) -> Dict[str, any]:
        """
        Get platform-specific recommendations for image optimization
        """
        if platform not in self.PLATFORM_SPECS:
            platform = "instagram"  # Default fallback
            
        spec = self.PLATFORM_SPECS[platform]
        
        return {
            "platform": platform,
            "recommended_sizes": spec,
            "best_practices": self._get_platform_best_practices(platform),
            "quality_presets": list(self.QUALITY_SETTINGS.keys())
        }

    def _get_platform_best_practices(self, platform: str) -> List[str]:
        """Get platform-specific best practices"""
        practices = {
            "instagram": [
                "Use square (1:1) or portrait (4:5) ratios for feed posts",
                "Vertical 9:16 for Stories and Reels",
                "High contrast and vibrant colors perform well",
                "Include faces when possible for higher engagement"
            ],
            "twitter": [
                "16:9 landscape works best for tweet images",
                "Keep text readable even in small previews",
                "Use high contrast for better visibility in timeline",
                "Avoid very tall images that get cropped in feed"
            ],
            "facebook": [
                "1.91:1 ratio optimal for link previews",
                "Square images work well for organic posts",
                "Bright, clear images with minimal text",
                "Consider Facebook's 20% text rule for ads"
            ],
            "linkedin": [
                "Professional, clean aesthetics work best",
                "1.91:1 for articles, square for posts",
                "High quality, business-appropriate content",
                "Clear, readable text and professional imagery"
            ],
            "tiktok": [
                "Vertical 9:16 is mandatory for full-screen",
                "Bright, attention-grabbing visuals",
                "Consider mobile viewing experience",
                "High contrast text if adding overlays"
            ]
        }
        
        return practices.get(platform, [
            "Use high resolution images (min 1080px)",
            "Maintain consistent brand colors",
            "Optimize for mobile viewing",
            "Test readability at small sizes"
        ])


# Global service instance
image_processing_service = ImageProcessingService()