"""
Minimal metrics API stub for production deployment
"""
from fastapi import APIRouter
from typing import List, Dict, Any
import logging

router = APIRouter(prefix="/api", tags=["metrics"])
logger = logging.getLogger(__name__)

@router.get("/metrics")
async def get_metrics():
    """Get system metrics - minimal stub"""
    return {
        "metrics": {
            "content_generated": 0,
            "posts_scheduled": 0,
            "engagement_rate": 0.0,
            "api_calls": 0
        },
        "message": "Metrics service temporarily unavailable - database not configured"
    }