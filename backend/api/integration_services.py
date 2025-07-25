"""
Integration Services API Endpoints
Exposes Instagram, Facebook, TikTok, research automation, and content generation services
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date

from backend.db.database import get_db
from backend.db.models import User, ContentItem, ResearchData
from backend.auth.dependencies import get_current_active_user
from backend.integrations.instagram_client import instagram_client, InstagramMediaType
from backend.integrations.facebook_client import facebook_client
from backend.integrations.tiktok_client import tiktok_client, TikTokVideoPrivacy
from backend.services.research_automation import research_service, ResearchQuery, ResearchSource
from backend.services.content_automation import content_automation_service
from backend.services.workflow_orchestration import workflow_orchestrator

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

# Pydantic Models for API Requests/Responses

class InstagramPostRequest(BaseModel):
    caption: str = Field(..., max_length=2200)
    media_urls: List[str] = Field(..., min_items=1, max_items=10)
    media_type: str = Field(..., regex="^(IMAGE|VIDEO|CAROUSEL_ALBUM|REELS)$")
    location_id: Optional[str] = None
    hashtags: Optional[List[str]] = Field(default_factory=list)
    schedule_for: Optional[datetime] = None

class FacebookPostRequest(BaseModel):
    message: str = Field(..., max_length=63206)
    media_urls: Optional[List[str]] = Field(default_factory=list)
    link: Optional[str] = None
    scheduled_publish_time: Optional[datetime] = None
    targeting: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TikTokVideoRequest(BaseModel):
    video_url: str = Field(..., description="URL of video to upload")
    description: str = Field(..., max_length=2200)
    privacy_level: str = Field("PUBLIC_TO_EVERYONE", regex="^(PUBLIC_TO_EVERYONE|MUTUAL_FOLLOW_FRIENDS|FOLLOWER_OF_CREATOR|SELF_ONLY)$")
    disable_duet: bool = False
    disable_stitch: bool = False
    disable_comment: bool = False
    brand_content_toggle: bool = False
    auto_add_music: bool = True

class ResearchQueryRequest(BaseModel):
    keywords: List[str] = Field(..., min_items=1, max_items=10)
    platforms: List[str] = Field(..., min_items=1)
    time_range: str = Field("24h", regex="^(1h|24h|7d|30d)$")
    location: Optional[str] = None
    max_results: int = Field(50, ge=10, le=500)
    include_sentiment: bool = True
    include_engagement: bool = True

class ContentGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=5, max_length=200)
    platform: str = Field(..., regex="^(twitter|instagram|facebook|linkedin|tiktok)$")
    content_type: str = Field(..., regex="^(post|story|reel|thread|article)$")
    tone: str = Field("professional", regex="^(professional|casual|humorous|inspirational|educational)$")
    target_audience: Optional[str] = None
    include_hashtags: bool = True
    include_cta: bool = True

class WorkflowTriggerRequest(BaseModel):
    workflow_type: str = Field(..., regex="^(daily_content|research_analysis|engagement_optimization|trend_monitoring)$")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    schedule_for: Optional[datetime] = None

# Instagram API Endpoints

@router.post("/instagram/post")
async def create_instagram_post(
    request: InstagramPostRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create Instagram post with media"""
    try:
        # Get user's Instagram access token
        instagram_token = await instagram_client.get_user_token(current_user.id)
        if not instagram_token:
            raise HTTPException(status_code=401, detail="Instagram account not connected")
        
        # Create Instagram post
        result = await instagram_client.create_post(
            access_token=instagram_token,
            caption=request.caption,
            media_urls=request.media_urls,
            media_type=InstagramMediaType(request.media_type),
            location_id=request.location_id,
            hashtags=request.hashtags
        )
        
        # Store in database
        content_item = ContentItem(
            user_id=current_user.id,
            content=request.caption,
            platform="instagram",
            content_type=request.media_type.lower(),
            platform_post_id=result["id"],
            platform_url=result.get("permalink"),
            status="published",
            published_at=datetime.utcnow()
        )
        db.add(content_item)
        db.commit()
        
        return {
            "success": True,
            "instagram_post_id": result["id"],
            "permalink": result.get("permalink"),
            "content_id": content_item.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Instagram post: {str(e)}")

@router.get("/instagram/insights/{post_id}")
async def get_instagram_insights(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get Instagram post insights"""
    try:
        instagram_token = await instagram_client.get_user_token(current_user.id)
        if not instagram_token:
            raise HTTPException(status_code=401, detail="Instagram account not connected")
        
        insights = await instagram_client.get_media_insights(instagram_token, post_id)
        return {"insights": insights}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Instagram insights: {str(e)}")

# Facebook API Endpoints

@router.post("/facebook/post")
async def create_facebook_post(
    request: FacebookPostRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create Facebook post"""
    try:
        facebook_token = await facebook_client.get_user_token(current_user.id)
        if not facebook_token:
            raise HTTPException(status_code=401, detail="Facebook account not connected")
        
        result = await facebook_client.create_post(
            access_token=facebook_token,
            message=request.message,
            media_urls=request.media_urls,
            link=request.link,
            scheduled_publish_time=request.scheduled_publish_time
        )
        
        # Store in database
        content_item = ContentItem(
            user_id=current_user.id,
            content=request.message,
            platform="facebook",
            content_type="post",
            platform_post_id=result["id"],
            status="published" if not request.scheduled_publish_time else "scheduled",
            published_at=datetime.utcnow() if not request.scheduled_publish_time else None,
            scheduled_for=request.scheduled_publish_time
        )
        db.add(content_item)
        db.commit()
        
        return {
            "success": True,
            "facebook_post_id": result["id"],
            "content_id": content_item.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Facebook post: {str(e)}")

@router.get("/facebook/insights/{post_id}")
async def get_facebook_insights(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get Facebook post insights"""
    try:
        facebook_token = await facebook_client.get_user_token(current_user.id)
        if not facebook_token:
            raise HTTPException(status_code=401, detail="Facebook account not connected")
        
        insights = await facebook_client.get_post_insights(facebook_token, post_id)
        return {"insights": insights}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Facebook insights: {str(e)}")

# Research Automation Endpoints

@router.post("/research/execute")
async def execute_research(
    request: ResearchQueryRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Execute automated research query"""
    try:
        # Convert request to ResearchQuery object
        research_query = ResearchQuery(
            keywords=request.keywords,
            platforms=[ResearchSource(platform) for platform in request.platforms],
            content_types=["text", "image", "video"],
            time_range=request.time_range,
            location=request.location,
            max_results=request.max_results,
            include_sentiment=request.include_sentiment,
            include_engagement=request.include_engagement
        )
        
        # Execute research in background
        background_tasks.add_task(
            research_service.execute_research_pipeline,
            query=research_query,
            user_id=current_user.id,
            db=db
        )
        
        return {
            "success": True,
            "message": "Research pipeline started",
            "query": {
                "keywords": request.keywords,
                "platforms": request.platforms,
                "time_range": request.time_range,
                "max_results": request.max_results
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute research: {str(e)}")

@router.get("/research/results")
async def get_research_results(
    keywords: List[str] = Query(...),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recent research results"""
    try:
        # Query research data
        results = db.query(ResearchData).filter(
            ResearchData.user_id == current_user.id,
            ResearchData.keywords.contains(keywords)
        ).order_by(ResearchData.created_at.desc()).limit(limit).all()
        
        return {
            "results": [
                {
                    "id": result.id,
                    "source": result.source,
                    "content": result.content,
                    "keywords": result.keywords,
                    "sentiment": result.sentiment_score,
                    "engagement": result.engagement_metrics,
                    "created_at": result.created_at
                }
                for result in results
            ],
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get research results: {str(e)}")

# Content Generation Endpoints

@router.post("/content/generate")
async def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered content"""
    try:
        # Generate content using automation service
        generated_content = await content_automation_service.generate_content(
            topic=request.topic,
            platform=request.platform,
            content_type=request.content_type,
            tone=request.tone,
            target_audience=request.target_audience,
            include_hashtags=request.include_hashtags,
            include_cta=request.include_cta,
            user_id=current_user.id
        )
        
        # Store generated content
        content_item = ContentItem(
            user_id=current_user.id,
            content=generated_content["content"],
            platform=request.platform,
            content_type=request.content_type,
            status="draft",
            ai_model=generated_content.get("model", "openai-gpt"),
            prompt_used=generated_content.get("prompt"),
            generation_params={
                "topic": request.topic,
                "tone": request.tone,
                "target_audience": request.target_audience
            }
        )
        db.add(content_item)
        db.commit()
        
        return {
            "success": True,
            "content": generated_content["content"],
            "hashtags": generated_content.get("hashtags", []),
            "engagement_prediction": generated_content.get("engagement_score"),
            "content_id": content_item.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate content: {str(e)}")

# Workflow Orchestration Endpoints

@router.post("/workflow/trigger")
async def trigger_workflow(
    request: WorkflowTriggerRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Trigger automated workflow"""
    try:
        # Trigger workflow in background
        background_tasks.add_task(
            workflow_orchestrator.execute_workflow,
            workflow_type=request.workflow_type,
            user_id=current_user.id,
            parameters=request.parameters,
            scheduled_time=request.schedule_for
        )
        
        return {
            "success": True,
            "message": f"Workflow '{request.workflow_type}' triggered",
            "workflow_type": request.workflow_type,
            "parameters": request.parameters,
            "scheduled_for": request.schedule_for
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger workflow: {str(e)}")

@router.get("/workflow/status/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get workflow execution status"""
    try:
        status = await workflow_orchestrator.get_workflow_status(workflow_id, current_user.id)
        return {"status": status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@router.get("/metrics/collection")
async def get_metrics_collection_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get metrics collection status across all platforms"""
    try:
        from backend.services.metrics_collection import metrics_collector
        
        status = await metrics_collector.get_collection_status(current_user.id)
        return {
            "collection_status": status,
            "last_collection": status.get("last_update"),
            "platforms": status.get("platforms", {}),
            "metrics_count": status.get("total_metrics", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics status: {str(e)}")

# TikTok API Endpoints

@router.post("/tiktok/video")
async def upload_tiktok_video(
    request: TikTokVideoRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload video to TikTok"""
    try:
        # Get user's TikTok access token
        tiktok_token = await tiktok_client.get_user_token(current_user.id)
        if not tiktok_token:
            raise HTTPException(status_code=401, detail="TikTok account not connected")
        
        # Upload video to TikTok
        publish_id = await tiktok_client.upload_video(
            access_token=tiktok_token,
            video_url=request.video_url,
            description=request.description,
            privacy_level=TikTokVideoPrivacy(request.privacy_level),
            disable_duet=request.disable_duet,
            disable_stitch=request.disable_stitch,
            disable_comment=request.disable_comment,
            brand_content_toggle=request.brand_content_toggle,
            auto_add_music=request.auto_add_music
        )
        
        # Store in database
        content_item = ContentItem(
            user_id=current_user.id,
            content=request.description,
            platform="tiktok",
            content_type="video",
            platform_post_id=publish_id,
            status="published",
            published_at=datetime.utcnow()
        )
        db.add(content_item)
        db.commit()
        
        return {
            "success": True,
            "publish_id": publish_id,
            "content_id": content_item.id,
            "platform": "tiktok"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload TikTok video: {str(e)}")

@router.get("/tiktok/user/info")
async def get_tiktok_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get TikTok user profile information"""
    try:
        tiktok_token = await tiktok_client.get_user_token(current_user.id)
        if not tiktok_token:
            raise HTTPException(status_code=401, detail="TikTok account not connected")
        
        user_info = await tiktok_client.get_user_info(access_token=tiktok_token)
        
        return {
            "user_info": {
                "open_id": user_info.open_id,
                "display_name": user_info.display_name,
                "avatar_url": user_info.avatar_url,
                "follower_count": user_info.follower_count,
                "following_count": user_info.following_count,
                "likes_count": user_info.likes_count,
                "video_count": user_info.video_count,
                "is_verified": user_info.is_verified
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok user info: {str(e)}")

@router.get("/tiktok/videos")
async def get_tiktok_user_videos(
    max_count: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's TikTok videos"""
    try:
        tiktok_token = await tiktok_client.get_user_token(current_user.id)
        if not tiktok_token:
            raise HTTPException(status_code=401, detail="TikTok account not connected")
        
        videos_data = await tiktok_client.get_user_videos(
            access_token=tiktok_token,
            max_count=max_count,
            cursor=cursor
        )
        
        return {
            "videos": [
                {
                    "id": video.id,
                    "title": video.title,
                    "description": video.video_description,
                    "duration": video.duration,
                    "cover_image_url": video.cover_image_url,
                    "share_url": video.share_url,
                    "create_time": video.create_time.isoformat(),
                    "likes_count": video.likes_count,
                    "view_count": video.video_view_count,
                    "share_count": video.share_count,
                    "comment_count": video.comment_count
                }
                for video in videos_data["videos"]
            ],
            "cursor": videos_data["cursor"],
            "has_more": videos_data["has_more"],
            "total": videos_data["total"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok videos: {str(e)}")

@router.get("/tiktok/analytics/{video_id}")
async def get_tiktok_video_analytics(
    video_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get analytics for a TikTok video"""
    try:
        tiktok_token = await tiktok_client.get_user_token(current_user.id)
        if not tiktok_token:
            raise HTTPException(status_code=401, detail="TikTok account not connected")
        
        analytics_list = await tiktok_client.get_video_analytics(
            access_token=tiktok_token,
            video_ids=[video_id]
        )
        
        if not analytics_list:
            raise HTTPException(status_code=404, detail="Video analytics not found")
        
        analytics = analytics_list[0]
        
        return {
            "analytics": {
                "video_id": analytics.video_id,
                "view_count": analytics.view_count,
                "like_count": analytics.like_count,
                "comment_count": analytics.comment_count,
                "share_count": analytics.share_count,
                "profile_view": analytics.profile_view,
                "reach": analytics.reach,
                "play_time_sum": analytics.play_time_sum,
                "average_watch_time": analytics.average_watch_time,
                "completion_rate": analytics.completion_rate,
                "engagement_rate": analytics.engagement_rate,
                "date_range_begin": analytics.date_range_begin.isoformat(),
                "date_range_end": analytics.date_range_end.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok analytics: {str(e)}")

@router.get("/tiktok/hashtags/trending")
async def get_trending_tiktok_hashtags(
    keywords: List[str] = Query(..., min_items=1, max_items=10),
    period: int = Query(7, ge=1, le=120),
    region_code: str = Query("US"),
    current_user: User = Depends(get_current_active_user)
):
    """Get trending TikTok hashtags"""
    try:
        tiktok_token = await tiktok_client.get_user_token(current_user.id)
        if not tiktok_token:
            raise HTTPException(status_code=401, detail="TikTok account not connected")
        
        hashtags = await tiktok_client.search_hashtags(
            access_token=tiktok_token,
            keywords=keywords,
            period=period,
            region_code=region_code
        )
        
        return {
            "hashtags": [
                {
                    "hashtag_id": hashtag.hashtag_id,
                    "hashtag_name": hashtag.hashtag_name,
                    "view_count": hashtag.view_count,
                    "publish_count": hashtag.publish_cnt,
                    "is_commerce": hashtag.is_commerce,
                    "description": hashtag.desc
                }
                for hashtag in hashtags
            ],
            "period_days": period,
            "region_code": region_code,
            "total": len(hashtags)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending hashtags: {str(e)}")

@router.get("/tiktok/trending/videos")
async def get_trending_tiktok_videos(
    region_code: str = Query("US"),
    period: int = Query(7, ge=1, le=120),
    max_count: int = Query(50, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Get trending TikTok videos"""
    try:
        tiktok_token = await tiktok_client.get_user_token(current_user.id)
        if not tiktok_token:
            raise HTTPException(status_code=401, detail="TikTok account not connected")
        
        trending_videos = await tiktok_client.get_trending_videos(
            access_token=tiktok_token,
            region_code=region_code,
            period=period,
            max_count=max_count
        )
        
        return {
            "trending_videos": trending_videos,
            "region_code": region_code,
            "period_days": period,
            "total": len(trending_videos)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending videos: {str(e)}")

@router.get("/tiktok/comments/{video_id}")
async def get_tiktok_video_comments(
    video_id: str,
    max_count: int = Query(20, ge=1, le=50),
    cursor: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """Get comments for a TikTok video"""
    try:
        tiktok_token = await tiktok_client.get_user_token(current_user.id)
        if not tiktok_token:
            raise HTTPException(status_code=401, detail="TikTok account not connected")
        
        comments_data = await tiktok_client.get_video_comments(
            access_token=tiktok_token,
            video_id=video_id,
            max_count=max_count,
            cursor=cursor
        )
        
        return {
            "comments": comments_data.get("comments", []),
            "cursor": comments_data.get("cursor", ""),
            "has_more": comments_data.get("has_more", False),
            "total": comments_data.get("total", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok comments: {str(e)}")