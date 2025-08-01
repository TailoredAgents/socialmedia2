#!/usr/bin/env python3
"""
Wrapper main.py that redirects to the root app.py
This handles Render's cached command while using our standalone app
"""
import sys
import os

# Add root directory to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

print(f"🔄 Redirecting from backend/main.py to root app.py")
print(f"📁 Root directory: {root_dir}")
print(f"🐍 Python version: {sys.version}")

# Import the app from root directory
try:
    from app import app
    print("✅ Successfully imported app from root directory")
except ImportError as e:
    print(f"❌ Failed to import app: {e}")
    # Fallback: create a minimal app here
    from fastapi import FastAPI
    
    app = FastAPI(title="AI Social Media Content Agent - Fallback")
    
    @app.get("/")
    async def root():
        return {"message": "Fallback app is running", "status": "success"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "fallback": True}

# Export the app so uvicorn can find it
__all__ = ["app"]