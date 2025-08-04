"""
Minimal content API stub for production deployment
"""
from fastapi import APIRouter
from typing import List, Dict, Any
import logging

router = APIRouter(prefix="/api/content", tags=["content"])
logger = logging.getLogger(__name__)

@router.get("/")
async def get_content():
    """Get content - minimal stub"""
    return {
        "content": [],
        "total": 0,
        "message": "Content service temporarily unavailable - database not configured"
    }

@router.get("/scheduled/upcoming")
async def get_upcoming_scheduled():
    """Get upcoming scheduled content"""
    return {
        "scheduled_content": [],
        "total": 0,
        "message": "Content scheduling temporarily unavailable"
    }

@router.post("/generate")
async def generate_content():
    """Generate content stub"""
    return {
        "success": False,
        "message": "Content generation temporarily unavailable - AI services not configured"
    }

@router.get("/generate-image")
async def generate_image():
    """Generate image endpoint stub"""
    return {
        "success": False,
        "message": "Image generation temporarily unavailable - OpenAI service not configured"
    }