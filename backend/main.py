from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI(
    title="AI Social Media Content Agent",
    description="Enterprise AI Social Media Content Agent API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AI Social Media Content Agent API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/metrics")
async def get_metrics():
    return {
        "total_posts": 156,
        "engagement_rate": 4.2,
        "followers_gained": 342,
        "content_pieces": 89,
        "platforms": ["twitter", "linkedin", "instagram"],
        "last_updated": datetime.utcnow().isoformat(),
        "performance_data": {
            "twitter": {"posts": 45, "engagement": 3.8, "reach": 12500},
            "linkedin": {"posts": 32, "engagement": 5.1, "reach": 8900},
            "instagram": {"posts": 12, "engagement": 6.2, "reach": 5400}
        },
        "weekly_growth": [
            {"week": "2025-07-14", "followers": 1250, "engagement": 3.9},
            {"week": "2025-07-07", "followers": 1180, "engagement": 4.1},
            {"week": "2025-06-30", "followers": 1120, "engagement": 3.7},
            {"week": "2025-06-23", "followers": 1050, "engagement": 4.0}
        ]
    }

@app.get("/api/content")
async def get_content():
    return {
        "recent_posts": [
            {
                "id": "post_1",
                "platform": "twitter",
                "content": "AI is revolutionizing content creation with autonomous agents that can research, generate, and optimize posts across multiple platforms...",
                "status": "published",
                "engagement": {"likes": 45, "shares": 12, "comments": 8},
                "created_at": "2025-07-22T08:00:00Z"
            },
            {
                "id": "post_2",
                "platform": "linkedin",
                "content": "The future of social media marketing lies in AI-driven content factories that operate autonomously while maintaining brand voice and achieving specific business goals...",
                "status": "scheduled",
                "scheduled_for": "2025-07-23T10:00:00Z",
                "created_at": "2025-07-22T07:30:00Z"
            },
            {
                "id": "post_3",
                "platform": "instagram",
                "content": "Behind the scenes: Our AI content agent analyzed 50+ trending topics today and generated personalized content for maximum engagement 🚀 #AIMarketing",
                "status": "draft",
                "engagement": {"likes": 0, "shares": 0, "comments": 0},
                "created_at": "2025-07-22T12:15:00Z"
            }
        ],
        "drafts": 8,
        "scheduled": 15,
        "total_content": 156
    }

# Enhanced API endpoints
@app.get("/api/memory/stats")
async def get_memory_stats():
    return {
        "status": "success",
        "stats": {
            "total_content_items": 245,
            "index_size": 245,
            "content_types": {
                "research": 45,
                "generated_content": 156,
                "trend_analysis": 23,
                "optimization_insights": 21
            },
            "memory_system_version": "1.0",
            "last_updated": datetime.utcnow().isoformat()
        }
    }

@app.get("/api/goals/summary")
async def get_goals_summary():
    return {
        "status": "success",
        "summary": {
            "total_goals": 4,
            "active_goals": 3,
            "completed_goals": 1,
            "on_track_goals": 2,
            "avg_progress": 78.5,
            "goals": [
                {
                    "id": "goal_1",
                    "title": "Grow LinkedIn Following",
                    "progress": 91.7,
                    "target": "3,000 followers",
                    "current": "2,750 followers",
                    "status": "active",
                    "on_track": True
                },
                {
                    "id": "goal_2",
                    "title": "Improve Engagement Rate",
                    "progress": 85.0,
                    "target": "6.0% engagement",
                    "current": "5.1% engagement",
                    "status": "active",
                    "on_track": True
                },
                {
                    "id": "goal_3",
                    "title": "Monthly Content Volume",
                    "progress": 75.0,
                    "target": "60 posts/month",
                    "current": "45 posts",
                    "status": "active",
                    "on_track": False
                }
            ]
        }
    }

@app.get("/api/workflow/status")
async def get_workflow_status():
    return {
        "status": "success",
        "workflow": {
            "current_stage": "content_generation",
            "last_full_cycle": "2025-07-22T06:00:00Z",
            "cycle_count": 142,
            "next_cycle": "2025-07-23T06:00:00Z",
            "metrics": {
                "avg_cycle_time": 85.5,
                "success_rate": 96.2,
                "content_generated_today": 12,
                "research_items_today": 8
            },
            "stages": [
                {
                    "name": "Daily Research",
                    "status": "completed",
                    "scheduled_time": "06:00",
                    "completion_time": "06:25",
                    "duration_minutes": 25
                },
                {
                    "name": "Trend Analysis",
                    "status": "completed", 
                    "scheduled_time": "06:30",
                    "completion_time": "06:45",
                    "duration_minutes": 15
                },
                {
                    "name": "Content Generation",
                    "status": "running",
                    "scheduled_time": "09:15",
                    "progress": 60,
                    "duration_minutes": 45
                },
                {
                    "name": "Automated Posting",
                    "status": "pending",
                    "scheduled_time": "15:00",
                    "duration_minutes": 30
                }
            ]
        }
    }

@app.post("/api/workflow/trigger")
async def trigger_workflow():
    return {
        "status": "success",
        "message": "Daily workflow cycle triggered",
        "cycle_number": 143,
        "estimated_completion": "2025-07-22T22:30:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )