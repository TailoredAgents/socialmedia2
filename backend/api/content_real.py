"""
Real Content API with AI-powered functionality
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from backend.services.image_generation_service import ImageGenerationService
from backend.services.ai_insights_service import ai_insights_service
from backend.services.twitter_service import twitter_service

router = APIRouter(prefix="/api/content", tags=["content"])
logger = logging.getLogger(__name__)

# Initialize services
image_service = ImageGenerationService()

class ImageGenerationRequest(BaseModel):
    prompt: str
    platform: str = "instagram"
    quality_preset: str = "standard"
    content_context: Optional[str] = None
    industry_context: Optional[str] = None
    tone: str = "professional"

class ContentGenerationRequest(BaseModel):
    topic: str
    platform: str = "twitter"
    tone: str = "professional"
    include_hashtags: bool = True

@router.get("/")
async def get_content():
    """Get recent generated content"""
    # For now, return empty as we don't have database storage yet
    return {
        "content": [],
        "total": 0,
        "message": "No stored content - content is generated on-demand"
    }

@router.get("/scheduled/upcoming")
async def get_upcoming_scheduled():
    """Get upcoming scheduled content"""
    return {
        "scheduled_content": [],
        "total": 0,
        "message": "Scheduling feature coming soon - post directly for now"
    }

@router.post("/generate")
async def generate_content(request: ContentGenerationRequest):
    """Generate AI-powered social media content"""
    try:
        # Get AI insights for context
        insights = await ai_insights_service.generate_weekly_insights()
        
        # Generate content based on insights and topic
        from openai import AsyncOpenAI
        from backend.core.config import get_settings
        
        settings = get_settings()
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        context = ""
        if insights.get("status") == "success":
            context = f"Recent AI industry insights: {insights['insights']['full_analysis'][:500]}..."
        
        prompt = f"""
        Create engaging {request.platform} content about: {request.topic}
        
        Context: {context}
        
        Requirements:
        - Tone: {request.tone}
        - Platform: {request.platform}
        - Include hashtags: {request.include_hashtags}
        - Make it engaging and authentic
        - Keep within platform character limits
        
        Return only the content text, ready to post.
        """
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        generated_content = response.choices[0].message.content.strip()
        
        return {
            "success": True,
            "content": generated_content,
            "platform": request.platform,
            "topic": request.topic,
            "tone": request.tone,
            "character_count": len(generated_content),
            "generated_at": "now"
        }
        
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/generate-image")
async def generate_image(request: ImageGenerationRequest):
    """Generate AI-powered images using real OpenAI DALL-E"""
    try:
        result = await image_service.generate_image(
            prompt=request.prompt,
            platform=request.platform,
            quality_preset=request.quality_preset,
            content_context=request.content_context,
            industry_context=request.industry_context,
            tone=request.tone
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.get("/ai-insights")
async def get_ai_insights():
    """Get real AI industry insights"""
    try:
        insights = await ai_insights_service.generate_weekly_insights()
        return insights
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.get("/social-connections")
async def get_social_connections():
    """Get status of social media API connections"""
    connections = {
        "twitter": twitter_service.get_connection_status(),
        "linkedin": {
            "connected": False,
            "error": "LinkedIn API credentials not configured",
            "credentials_needed": ["client_id", "client_secret", "access_token"]
        },
        "instagram": {
            "connected": False,
            "error": "Instagram API credentials not configured", 
            "credentials_needed": ["app_id", "app_secret", "access_token", "business_id"]
        },
        "facebook": {
            "connected": False,
            "error": "Facebook API credentials not configured",
            "credentials_needed": ["app_id", "app_secret", "access_token", "page_id"]
        }
    }
    
    return {
        "status": "success",
        "connections": connections,
        "connected_count": sum(1 for conn in connections.values() if conn.get("connected", False)),
        "total_platforms": len(connections)
    }