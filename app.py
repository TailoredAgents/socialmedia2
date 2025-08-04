#!/usr/bin/env python3
"""
FastAPI app instance for production deployment
This file creates the app instance that uvicorn will serve
"""
import sys
import os
import logging
from pathlib import Path

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("🚀 Initializing AI Social Media Content Agent")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))
    logger.info(f"Added backend path: {backend_path}")

# Import the complete app with better error handling
try:
    from backend.app_complete import app
    logger.info("✅ Successfully imported complete backend app")
    
    # Add production health check
    @app.get("/render-health")
    async def render_health():
        """Special health check for Render deployment"""
        return {
            "status": "healthy",
            "mode": "production",
            "version": "2.0.0",
            "python_version": sys.version,
            "available_routes": len(app.routes)
        }
        
except ImportError as e:
    logger.error(f"❌ Failed to import complete app: {e}")
    logger.info("Creating fallback app...")
    
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="AI Social Media Content Agent - Fallback",
        description="Fallback deployment version with minimal functionality", 
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware for fallback
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def fallback_root():
        return {
            "message": "AI Social Media Content Agent API (Fallback Mode)",
            "status": "limited_functionality",
            "error": "Could not load complete backend - check server logs",
            "python_version": sys.version
        }
    
    @app.get("/health")
    async def fallback_health():
        return {"status": "healthy", "mode": "fallback"}
    
    @app.get("/render-health")
    async def fallback_render_health():
        return {"status": "healthy", "mode": "fallback", "error": "Main app failed to load"}

# Export the app so uvicorn can find it
__all__ = ["app"]