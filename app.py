#!/usr/bin/env python3
"""
Production FastAPI app for Render deployment
Uses the complete backend implementation
"""
import sys
import os

print("Python version:", sys.version)
print("Working directory:", os.getcwd())
print("Directory contents:", os.listdir('.'))

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
print(f"Added backend path: {backend_path}")

# Import the complete app
try:
    from backend.app_complete import app
    print("✅ Successfully imported complete backend app")
except ImportError as e:
    print(f"❌ Failed to import complete app: {e}")
    # Fallback: create a minimal app
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="AI Social Media Content Agent - Fallback",
        description="Fallback deployment version", 
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
            "error": "Could not load complete backend"
        }
    
    @app.get("/health")
    async def fallback_health():
        return {"status": "healthy", "mode": "fallback"}

# Export the app so uvicorn can find it
__all__ = ["app"]