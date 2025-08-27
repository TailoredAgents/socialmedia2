"""
AI Contextual Suggestions API
Provides personalized, real-time AI suggestions based on user context
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from backend.db.database import get_db
from backend.db.models import User, UserSetting, Content, Goal, Memory
from backend.auth.dependencies import get_current_active_user
from backend.agents.tools import OpenAITool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai-suggestions"])

# Request/Response Models
class SuggestionRequest(BaseModel):
    type: str = Field(..., pattern="^(content|goals|inbox|memory|scheduler)$")
    context: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=4, ge=1, le=10)

class AISuggestion(BaseModel):
    id: str
    title: str
    description: str
    action: str
    color: str = "blue"
    ai_prompt: str
    estimated_time: str
    priority: int = Field(default=5, ge=1, le=10)  # 1 = highest priority
    personalization_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
class SuggestionsResponse(BaseModel):
    suggestions: List[AISuggestion]
    context_summary: str
    personalization_level: str  # "basic", "medium", "high"

async def analyze_user_context(user: User, db: Session, suggestion_type: str) -> Dict[str, Any]:
    """Analyze user's current context to personalize suggestions"""
    context = {
        "user_id": user.id,
        "type": suggestion_type,
        "account_age_days": (datetime.utcnow() - user.created_at).days if user.created_at else 0,
        "has_content": False,
        "content_count": 0,
        "has_goals": False,
        "goal_count": 0,
        "has_memories": False,
        "memory_count": 0,
        "recent_activity": False,
        "preferred_platforms": [],
        "brand_voice": "professional",
        "creativity_level": 0.7
    }
    
    try:
        # Get user settings for personalization
        user_settings = db.query(UserSetting).filter(UserSetting.user_id == user.id).first()
        if user_settings:
            context["preferred_platforms"] = user_settings.preferred_platforms or ["twitter", "instagram"]
            context["brand_voice"] = user_settings.brand_voice or "professional"
            context["creativity_level"] = user_settings.creativity_level or 0.7
        
        # Analyze content history
        content_count = db.query(Content).filter(Content.user_id == user.id).count()
        context["content_count"] = content_count
        context["has_content"] = content_count > 0
        
        # Check for recent content (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_content = db.query(Content).filter(
            Content.user_id == user.id,
            Content.created_at >= week_ago
        ).count()
        context["recent_activity"] = recent_content > 0
        
        # Analyze goals
        goal_count = db.query(Goal).filter(Goal.user_id == user.id).count()
        context["goal_count"] = goal_count
        context["has_goals"] = goal_count > 0
        
        # Analyze memories/brand brain
        memory_count = db.query(Memory).filter(Memory.user_id == user.id).count()
        context["memory_count"] = memory_count
        context["has_memories"] = memory_count > 0
        
    except Exception as e:
        logger.warning(f"Error analyzing user context: {e}")
    
    return context

async def generate_contextual_suggestions(user_context: Dict[str, Any], suggestion_type: str) -> List[Dict[str, Any]]:
    """Generate AI-powered contextual suggestions based on user context"""
    
    # Build AI prompt based on context
    context_info = f"""
    User Context:
    - Account age: {user_context['account_age_days']} days
    - Content created: {user_context['content_count']} posts
    - Goals set: {user_context['goal_count']} goals
    - Brand brain entries: {user_context['memory_count']} memories
    - Recent activity: {user_context['recent_activity']}
    - Preferred platforms: {', '.join(user_context['preferred_platforms'])}
    - Brand voice: {user_context['brand_voice']}
    - Creativity level: {user_context['creativity_level']}
    
    Generate 4 personalized AI suggestions for {suggestion_type} that would be most valuable for this user.
    Consider their experience level, activity patterns, and preferences.
    """
    
    try:
        # Generate contextual suggestions using AI
        openai_tool = OpenAITool()
        ai_response = openai_tool.generate_text(
            prompt=f"""You are an AI social media assistant. Based on the user context below, generate 4 specific, actionable suggestions for {suggestion_type}.

{context_info}

Return suggestions as JSON array with this format:
[
  {{
    "id": "unique-id",
    "title": "Action title",
    "description": "Specific description based on user context",
    "action": "Button text",
    "color": "blue|purple|green|orange",
    "ai_prompt": "Specific AI prompt for this action",
    "estimated_time": "X minutes/seconds",
    "priority": 1-10,
    "personalization_score": 0.0-1.0
  }}
]

Make suggestions specific to their experience level and current situation. For new users, focus on getting started. For experienced users, focus on optimization and growth.""",
            model="gpt-5-mini",  # Use GPT-5 mini for better contextual understanding
            max_tokens=2000
        )
        
        # Parse AI response
        import json
        suggestions_data = json.loads(ai_response.strip())
        
        return suggestions_data
        
    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}")
        return []

def get_fallback_suggestions(suggestion_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Provide fallback suggestions if AI generation fails"""
    fallbacks = {
        "content": [
            {
                "id": "trending-content",
                "title": "Generate trending content ideas",
                "description": "AI will research current trends and create personalized post ideas",
                "action": "Generate Ideas",
                "color": "blue",
                "ai_prompt": "Generate trending social media post ideas based on current industry trends",
                "estimated_time": "30 seconds",
                "priority": 3,
                "personalization_score": 0.6
            },
            {
                "id": "content-calendar",
                "title": "Create content calendar",
                "description": "Plan and schedule your posts for optimal engagement",
                "action": "Plan Calendar",
                "color": "purple",
                "ai_prompt": "Create a weekly content calendar with strategic posting times",
                "estimated_time": "1 minute",
                "priority": 2,
                "personalization_score": 0.7
            }
        ],
        "goals": [
            {
                "id": "growth-goals",
                "title": "Set growth targets",
                "description": "AI-recommended goals based on your current performance",
                "action": "Create Goals",
                "color": "green",
                "ai_prompt": "Suggest realistic growth goals based on current metrics",
                "estimated_time": "30 seconds",
                "priority": 1,
                "personalization_score": 0.8
            }
        ]
    }
    
    return fallbacks.get(suggestion_type, fallbacks["content"])

@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_contextual_suggestions(
    request: SuggestionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized AI suggestions based on user context"""
    try:
        # Analyze user context
        user_context = await analyze_user_context(current_user, db, request.type)
        user_context.update(request.context)  # Merge with request context
        
        # Generate AI suggestions
        ai_suggestions = await generate_contextual_suggestions(user_context, request.type)
        
        # Fallback to static suggestions if AI fails
        if not ai_suggestions:
            ai_suggestions = get_fallback_suggestions(request.type, user_context)
            logger.warning(f"Using fallback suggestions for user {current_user.id}")
        
        # Limit results
        ai_suggestions = ai_suggestions[:request.limit]
        
        # Convert to response models
        suggestions = [AISuggestion(**suggestion) for suggestion in ai_suggestions]
        
        # Determine personalization level
        avg_score = sum(s.personalization_score for s in suggestions) / len(suggestions) if suggestions else 0
        if avg_score >= 0.8:
            personalization_level = "high"
        elif avg_score >= 0.6:
            personalization_level = "medium"  
        else:
            personalization_level = "basic"
        
        # Create context summary
        context_summary = f"Based on your {user_context['account_age_days']}-day journey with {user_context['content_count']} posts created"
        
        return SuggestionsResponse(
            suggestions=suggestions,
            context_summary=context_summary,
            personalization_level=personalization_level
        )
        
    except Exception as e:
        logger.error(f"Error getting contextual suggestions for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate suggestions"
        )

@router.get("/suggestion-types")
async def get_available_suggestion_types():
    """Get list of available suggestion types"""
    return {
        "types": ["content", "goals", "inbox", "memory", "scheduler"],
        "descriptions": {
            "content": "Content creation and posting suggestions",
            "goals": "Goal setting and achievement suggestions", 
            "inbox": "Social inbox management suggestions",
            "memory": "Brand brain and knowledge suggestions",
            "scheduler": "Content scheduling and timing suggestions"
        }
    }