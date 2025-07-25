"""
Content management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
import uuid
import json

from backend.db.database import get_db
from backend.db.models import ContentLog, User
from backend.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/content", tags=["content"])

# Pydantic models
class CreateContentRequest(BaseModel):
    platform: str = Field(..., regex="^(twitter|linkedin|instagram|facebook|tiktok)$")
    content: str = Field(..., min_length=1, max_length=10000)
    content_type: str = Field(..., regex="^(text|image|video|carousel)$")
    scheduled_for: Optional[datetime] = None
    engagement_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('scheduled_for')
    def scheduled_for_must_be_future(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v

class UpdateContentRequest(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    scheduled_for: Optional[datetime] = None
    engagement_data: Optional[Dict[str, Any]] = None
    
    @validator('scheduled_for')
    def scheduled_for_must_be_future(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v

class PublishContentRequest(BaseModel):
    platform_post_id: Optional[str] = None
    engagement_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ContentResponse(BaseModel):
    id: int
    platform: str
    content: str
    content_type: str
    status: str
    engagement_data: Dict[str, Any]
    scheduled_for: Optional[datetime]
    published_at: Optional[datetime]
    platform_post_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ContentAnalytics(BaseModel):
    total_posts: int
    posts_by_platform: Dict[str, int]
    posts_by_status: Dict[str, int]
    avg_engagement: float
    top_performing_posts: List[Dict[str, Any]]

@router.post("/", response_model=ContentResponse)
async def create_content(
    request: CreateContentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new content"""
    
    content = ContentLog(
        user_id=current_user.id,
        platform=request.platform,
        content=request.content,
        content_type=request.content_type,
        status="draft",
        engagement_data=request.engagement_data or {},
        scheduled_for=request.scheduled_for
    )
    
    # Auto-schedule if scheduled_for is provided
    if request.scheduled_for:
        content.status = "scheduled"
    
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content

@router.get("/", response_model=List[ContentResponse])
async def get_user_content(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    platform: Optional[str] = Query(None, regex="^(twitter|linkedin|instagram|facebook|tiktok)$"),
    status: Optional[str] = Query(None, regex="^(draft|scheduled|published|failed)$"),
    content_type: Optional[str] = Query(None, regex="^(text|image|video|carousel)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's content with filtering and pagination"""
    
    query = db.query(ContentLog).filter(ContentLog.user_id == current_user.id)
    
    if platform:
        query = query.filter(ContentLog.platform == platform)
    if status:
        query = query.filter(ContentLog.status == status)
    if content_type:
        query = query.filter(ContentLog.content_type == content_type)
    
    content_items = query.order_by(ContentLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return content_items

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific content by ID"""
    
    content = db.query(ContentLog).filter(
        ContentLog.id == content_id,
        ContentLog.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content

@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    request: UpdateContentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update content"""
    
    content = db.query(ContentLog).filter(
        ContentLog.id == content_id,
        ContentLog.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status == "published":
        raise HTTPException(status_code=400, detail="Cannot update published content")
    
    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    # Update status if scheduling
    if request.scheduled_for and content.status == "draft":
        content.status = "scheduled"
    elif not request.scheduled_for and content.status == "scheduled":
        content.status = "draft"
    
    content.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(content)
    
    return content

@router.post("/{content_id}/publish", response_model=ContentResponse)
async def publish_content(
    content_id: int,
    request: PublishContentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark content as published"""
    
    content = db.query(ContentLog).filter(
        ContentLog.id == content_id,
        ContentLog.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status == "published":
        raise HTTPException(status_code=400, detail="Content already published")
    
    # Update content status
    content.status = "published"
    content.published_at = datetime.utcnow()
    content.platform_post_id = request.platform_post_id
    
    # Update engagement data
    if request.engagement_data:
        content.engagement_data.update(request.engagement_data)
    
    content.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(content)
    
    return content

@router.post("/{content_id}/schedule")
async def schedule_content(
    content_id: int,
    scheduled_for: datetime,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Schedule content for publishing"""
    
    if scheduled_for <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
    
    content = db.query(ContentLog).filter(
        ContentLog.id == content_id,
        ContentLog.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status == "published":
        raise HTTPException(status_code=400, detail="Cannot schedule published content")
    
    content.scheduled_for = scheduled_for
    content.status = "scheduled"
    content.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Content scheduled successfully", "scheduled_for": scheduled_for}

@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete content"""
    
    content = db.query(ContentLog).filter(
        ContentLog.id == content_id,
        ContentLog.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status == "published":
        raise HTTPException(status_code=400, detail="Cannot delete published content")
    
    db.delete(content)
    db.commit()
    
    return {"message": "Content deleted successfully"}

@router.get("/scheduled/upcoming")
async def get_upcoming_content(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=30)
):
    """Get upcoming scheduled content"""
    
    from datetime import timedelta
    
    end_date = datetime.utcnow() + timedelta(days=days)
    
    content_items = db.query(ContentLog).filter(
        ContentLog.user_id == current_user.id,
        ContentLog.status == "scheduled",
        ContentLog.scheduled_for.between(datetime.utcnow(), end_date)
    ).order_by(ContentLog.scheduled_for).all()
    
    return [
        {
            "id": content.id,
            "platform": content.platform,
            "content": content.content[:100] + "..." if len(content.content) > 100 else content.content,
            "content_type": content.content_type,
            "scheduled_for": content.scheduled_for,
            "days_until": (content.scheduled_for - datetime.utcnow()).days
        }
        for content in content_items
    ]

@router.get("/analytics/summary", response_model=ContentAnalytics)
async def get_content_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get content analytics summary"""
    
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    content_items = db.query(ContentLog).filter(
        ContentLog.user_id == current_user.id,
        ContentLog.created_at >= start_date
    ).all()
    
    # Calculate statistics
    total_posts = len(content_items)
    
    posts_by_platform = {}
    posts_by_status = {}
    engagement_scores = []
    
    for content in content_items:
        # Platform stats
        platform = content.platform
        posts_by_platform[platform] = posts_by_platform.get(platform, 0) + 1
        
        # Status stats
        status = content.status
        posts_by_status[status] = posts_by_status.get(status, 0) + 1
        
        # Engagement stats
        engagement_data = content.engagement_data or {}
        likes = engagement_data.get('likes', 0)
        comments = engagement_data.get('comments', 0)
        shares = engagement_data.get('shares', 0)
        engagement_score = likes + comments * 2 + shares * 3  # Weighted engagement
        engagement_scores.append(engagement_score)
    
    avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
    
    # Top performing posts
    content_with_engagement = [
        (content, content.engagement_data.get('likes', 0) + 
         content.engagement_data.get('comments', 0) * 2 + 
         content.engagement_data.get('shares', 0) * 3)
        for content in content_items if content.status == "published"
    ]
    
    top_performing = sorted(content_with_engagement, key=lambda x: x[1], reverse=True)[:5]
    
    top_performing_posts = [
        {
            "id": content.id,
            "platform": content.platform,
            "content": content.content[:100] + "..." if len(content.content) > 100 else content.content,
            "engagement_score": score,
            "published_at": content.published_at
        }
        for content, score in top_performing
    ]
    
    return ContentAnalytics(
        total_posts=total_posts,
        posts_by_platform=posts_by_platform,
        posts_by_status=posts_by_status,
        avg_engagement=round(avg_engagement, 2),
        top_performing_posts=top_performing_posts
    )

@router.post("/generate")
async def generate_content_ideas(
    platform: str = Query(..., regex="^(twitter|linkedin|instagram|facebook|tiktok)$"),
    topic: Optional[str] = Query(None),
    tone: str = Query("professional", regex="^(professional|casual|humorous|inspiring|educational)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate content ideas (placeholder for AI integration)"""
    
    # This would integrate with OpenAI or other AI services
    # For now, return mock suggestions
    
    platform_suggestions = {
        "twitter": [
            "Share a quick tip about your industry",
            "Ask an engaging question to your audience",
            "Share behind-the-scenes content",
            "Comment on industry news or trends",
            "Celebrate a team or personal achievement"
        ],
        "linkedin": [
            "Write about lessons learned from recent projects",
            "Share industry insights or market analysis",
            "Highlight team member achievements",
            "Discuss professional development topics",
            "Share case studies or success stories"
        ],
        "instagram": [
            "Post behind-the-scenes photos/videos",
            "Share customer testimonials with visuals",
            "Create educational carousel posts",
            "Show your workspace or team",
            "Share user-generated content"
        ]
    }
    
    suggestions = platform_suggestions.get(platform, platform_suggestions["twitter"])
    
    return {
        "platform": platform,
        "topic": topic,
        "tone": tone,
        "suggestions": suggestions[:3],  # Return top 3
        "generated_at": datetime.utcnow()
    }