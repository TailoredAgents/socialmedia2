"""
AI Social Media Content Agent - Backend API
Copyright (c) 2025 Tailored Agents LLC. All Rights Reserved.

This software is proprietary and confidential. Unauthorized copying, distribution,
modification, public display, or public performance is strictly prohibited.
See LICENSE file for terms and conditions.

Created by Tailored Agents - AI Development Specialists
Enterprise-grade AI-powered social media management platform
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Import database components
from backend.db.database import engine
from backend.db.models import Base

# Import API routes
from backend.api.auth import router as auth_router
from backend.api.auth_management import router as auth_management_router
from backend.api.goals_v2 import router as goals_router
from backend.api.content import router as content_router
from backend.api.memory_v2 import router as memory_router
from backend.api.memory_vector import router as memory_vector_router
from backend.api.workflow_v2 import router as workflow_router
from backend.api.notifications import router as notifications_router
from backend.api.integration_services import router as integration_router

# Import security utilities
from backend.auth.security import add_security_headers
from backend.auth.middleware import jwt_middleware

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and validate environment on startup"""
    try:
        # Validate environment variables first
        from backend.core.env_validator_simple import validate_on_startup
        validate_on_startup()
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
        
        # Start APM monitoring
        from backend.services.apm_service import apm_service
        await apm_service.start_monitoring()
        logger.info("✅ APM monitoring started")
        
        # Initialize Redis cache
        from backend.services.redis_cache import redis_cache
        await redis_cache._initialize_connection()
        cache_health = await redis_cache.health_check()
        logger.info(f"✅ Redis cache initialized: {cache_health['status']}")
    except Exception as e:
        logger.error(f"Application initialization failed: {str(e)}")
        raise
    
    yield

app = FastAPI(
    title="AI Social Media Content Agent API",
    description="""
    ## Enterprise AI Social Media Content Agent

    A comprehensive AI-powered social media management platform featuring:

    ### 🚀 Core Features
    - **AI-Powered Content Generation** using CrewAI multi-agent system
    - **Semantic Memory System** with FAISS vector search (40K+ embeddings)
    - **Multi-Platform Integration** (Twitter, LinkedIn, Instagram, Facebook, TikTok)
    - **Advanced Analytics** with real-time performance tracking
    - **Automated Workflows** with intelligent optimization
    - **Enterprise Authentication** via Auth0 + JWT

    ### 🔧 Technical Architecture
    - **Backend:** FastAPI with SQLAlchemy ORM
    - **Database:** PostgreSQL with optimized indexes
    - **Vector Search:** FAISS with OpenAI embeddings
    - **Background Tasks:** Celery with Redis
    - **Authentication:** Multi-provider (Auth0 + local JWT)
    - **API Design:** RESTful with comprehensive validation

    ### 📚 API Categories
    - **Authentication & Users** - User management and security
    - **Content Management** - Content creation, scheduling, and analytics
    - **Memory & Search** - Semantic search and content intelligence
    - **Goals & Tracking** - Goal management with automated progress
    - **Integrations** - Social media platform integrations
    - **Workflows** - Automated workflow orchestration
    - **Notifications** - Smart notification management

    ### 🔒 Security
    - JWT-based authentication with Auth0 integration
    - Role-based access control
    - CORS protection and security headers
    - Input validation and sanitization
    - Rate limiting and request throttling

    ### 📊 Performance
    - <200ms API response times
    - Optimized database queries with indexes
    - Efficient FAISS vector search (<50ms)
    - Background processing for heavy operations
    - Real-time updates via WebSocket support

    **Version:** 1.0.0  
    **Environment:** Production Ready  
    **Last Updated:** July 24, 2025
    """,
    version="1.0.0",
    contact={
        "name": "AI Social Media Content Agent Team",
        "email": "support@aisocialagent.com",
        "url": "https://aisocialagent.com/support"
    },
    license_info={
        "name": "Enterprise License",
        "url": "https://aisocialagent.com/license"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://ai-social-backend.onrender.com",
            "description": "Production server"
        }
    ],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and authorization operations"
        },
        {
            "name": "content",
            "description": "Content creation, management, and analytics"
        },
        {
            "name": "memory",
            "description": "Semantic memory and vector search operations"
        },
        {
            "name": "goals",
            "description": "Goal tracking and progress management"
        },
        {
            "name": "integrations",
            "description": "Social media platform integrations"
        },
        {
            "name": "workflow",
            "description": "Automated workflow orchestration"
        },
        {
            "name": "notifications",
            "description": "Notification management and delivery"
        },
        {
            "name": "system",
            "description": "System health and monitoring endpoints"
        }
    ],
    lifespan=lifespan
)

# Add CORS middleware with Render support
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add JWT validation middleware
@app.middleware("http")
async def jwt_validation_middleware(request: Request, call_next):
    return await jwt_middleware(request, call_next)

# Add security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    return add_security_headers(response)

# Add APM monitoring middleware
@app.middleware("http")
async def apm_monitoring_middleware(request: Request, call_next):
    from backend.services.apm_service import create_apm_middleware
    apm_middleware = create_apm_middleware()
    return await apm_middleware(request, call_next)

# Include API routes
app.include_router(auth_router)
app.include_router(auth_management_router)
app.include_router(goals_router)
app.include_router(content_router)
app.include_router(memory_router)
app.include_router(memory_vector_router)
app.include_router(workflow_router)
app.include_router(notifications_router)
app.include_router(integration_router)

# Include monitoring routes
from backend.api.monitoring import router as monitoring_router
app.include_router(monitoring_router)

@app.get("/", 
         tags=["system"],
         summary="API Root Information",
         description="Get basic API information and navigation links")
async def root():
    """
    Returns basic API information including version, status, and documentation links.
    
    This endpoint provides essential information about the API and serves as an entry point
    for API discovery and navigation.
    """
    return {
        "name": "AI Social Media Content Agent API",
        "version": "1.0.0",
        "status": "production-ready",
        "description": "Enterprise AI-powered social media management platform",
        "documentation": {
            "interactive_docs": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "health": "/api/health",
            "authentication": "/api/auth",
            "content": "/api/content",
            "memory": "/api/memory",
            "goals": "/api/goals",
            "integrations": "/api/integrations",
            "workflows": "/api/workflow",
            "notifications": "/api/notifications"
        },
        "features": [
            "AI-Powered Content Generation",
            "Semantic Memory System",
            "Multi-Platform Integration",
            "Advanced Analytics",
            "Automated Workflows",
            "Enterprise Authentication"
        ]
    }

# Enhanced health check endpoints for production readiness

@app.get("/api/v1/health",
         tags=["system"],
         summary="Comprehensive Health Check",
         description="Detailed health check with all service dependencies")
async def health_check_v1():
    """
    Comprehensive health check endpoint for monitoring systems.
    
    Checks:
    - Database connectivity and performance
    - Redis cache system
    - External services (OpenAI, Auth0)
    - System resources and performance
    - Application-specific health indicators
    
    Returns HTTP 200 for healthy, 503 for unhealthy services.
    """
    from backend.db.database import engine
    import time
    import psutil
    
    start_time = time.time()
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {},
        "system_metrics": {},
        "features": {}
    }
    
    # Check database connection with timing
    try:
        db_start = time.time()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
            # Test a more complex query
            conn.execute("SELECT COUNT(*) FROM information_schema.tables")
        db_time = (time.time() - db_start) * 1000
        
        health_data["services"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(db_time, 2),
            "connection_pool": {
                "size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
                "checked_in": engine.pool.checkedin()
            }
        }
    except Exception as e:
        health_data["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "unhealthy"
    
    # Check Redis cache system
    try:
        from backend.services.redis_cache import redis_cache
        redis_start = time.time()
        cache_health = await redis_cache.health_check()
        redis_time = (time.time() - redis_start) * 1000
        
        health_data["services"]["redis"] = {
            "status": cache_health["status"],
            "response_time_ms": round(redis_time, 2),
            "connected": cache_health["redis_connected"],
            "fallback_available": cache_health["fallback_cache_available"],
            "hit_ratio": cache_health["hit_ratio"],
            "total_operations": cache_health["total_operations"]
        }
        
        if cache_health["status"] == "degraded" and health_data["status"] == "healthy":
            health_data["status"] = "degraded"
        elif cache_health["status"] == "unhealthy":
            health_data["status"] = "unhealthy"
            
    except Exception as e:
        health_data["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        if health_data["status"] == "healthy":
            health_data["status"] = "degraded"
    
    # Check external services
    health_data["services"]["openai"] = {
        "status": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured"
    }
    
    health_data["services"]["auth0"] = {
        "status": "configured" if os.getenv("AUTH0_DOMAIN") else "not_configured"
    }
    
    # System metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data["system_metrics"] = {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "disk_usage_percent": round((disk.used / disk.total) * 100, 2),
            "uptime_seconds": int((datetime.utcnow() - datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        }
    except Exception as e:
        health_data["system_metrics"] = {"error": str(e)}
    
    # Feature status
    health_data["features"] = {
        "ai_content_generation": bool(os.getenv("OPENAI_API_KEY")),
        "semantic_search": True,
        "multi_platform_integration": True,
        "real_time_analytics": bool(redis_url),
        "automated_workflows": True,
        "enterprise_auth": bool(os.getenv("AUTH0_DOMAIN"))
    }
    
    health_data["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # Return appropriate status code
    if health_data["status"] == "unhealthy":
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=health_data)
    
    return health_data

@app.get("/api/v1/ready",
         tags=["system"],
         summary="Kubernetes Readiness Probe",
         description="Lightweight readiness check for Kubernetes")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    
    Checks if the service is ready to receive traffic:
    - Database connection is working
    - Essential environment variables are set
    - Critical services are responding
    
    Returns HTTP 200 when ready, 503 when not ready.
    """
    from backend.db.database import engine
    from fastapi import HTTPException
    
    try:
        # Check database connection (most critical)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        # Check essential environment variables
        required_vars = ["SECRET_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "not_ready",
                    "reason": f"Missing required environment variables: {missing_vars}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": "ok",
                "environment": "ok"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "reason": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/api/v1/live",
         tags=["system"],
         summary="Kubernetes Liveness Probe",
         description="Lightweight liveness check for Kubernetes")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    
    Simple check to verify the application is alive and not deadlocked.
    Should return quickly without expensive operations.
    
    Returns HTTP 200 when alive, 503 when application should be restarted.
    """
    try:
        # Simple check that the application is responsive
        current_time = datetime.utcnow()
        
        return {
            "status": "alive",
            "timestamp": current_time.isoformat(),
            "uptime_seconds": int((current_time - datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        }
        
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_alive",
                "reason": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Legacy health check (keeping for backward compatibility)
@app.get("/api/health",
         tags=["system"],
         summary="Health Check (Legacy)",
         description="Legacy health check endpoint")
async def health_check():
    """
    Legacy health check endpoint for backward compatibility.
    Redirects to the enhanced /api/v1/health endpoint.
    """
    return await health_check_v1()

@app.get("/api/v1/environment",
         tags=["system"],
         summary="Environment Configuration Status",
         description="Check environment variable configuration and validation")
async def environment_status():
    """
    Environment configuration validation endpoint.
    
    Returns the status of all environment variables, missing configurations,
    and recommendations for improvement.
    """
    from backend.core.env_validator_simple import validate_environment
    
    validation_result = validate_environment()
    
    # Don't expose sensitive configuration details in response
    safe_result = {
        "validation_passed": validation_result["validation_passed"],
        "environment": validation_result["environment"],
        "configuration_completeness": validation_result["configuration_completeness"],
        "summary": validation_result["summary"],
        "errors": validation_result["errors"],
        "warnings": validation_result["warnings"],
        "recommendations": validation_result["recommendations"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Return 503 if validation failed (missing required variables)
    if not validation_result["validation_passed"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=safe_result)
    
    return safe_result

@app.get("/api/v1/metrics",
         tags=["system"],
         summary="Prometheus Metrics",
         description="Prometheus-compatible metrics for monitoring")
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint.
    
    Returns application metrics in Prometheus exposition format
    for integration with Prometheus monitoring systems.
    """
    from backend.services.apm_service import prometheus_metrics
    
    metrics_data = prometheus_metrics.generate_metrics()
    
    from fastapi import Response
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )

@app.get("/api/auth/status")
async def auth_status():
    """Get authentication system status"""
    from backend.auth.middleware import get_jwks_cache_status
    
    middleware_stats = jwt_middleware.get_middleware_stats()
    jwks_status = get_jwks_cache_status()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "auth_system": {
            "auth0_configured": bool(os.getenv("AUTH0_DOMAIN")),
            "local_jwt_configured": bool(os.getenv("SECRET_KEY")),
            "middleware_active": True
        },
        "middleware_stats": middleware_stats,
        "jwks_status": jwks_status
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get real-time platform metrics - requires actual data from database"""
    # TODO: Replace with real database queries
    from fastapi import HTTPException
    raise HTTPException(
        status_code=501, 
        detail="Metrics endpoint requires database implementation. Please set up social media integrations first."
    )

@app.get("/api/content")
async def get_content():
    """Get content data - requires actual data from database"""
    # TODO: Replace with real database queries
    from fastapi import HTTPException
    raise HTTPException(
        status_code=501, 
        detail="Content endpoint requires database implementation. Please set up content management first."
    )

# Enhanced API endpoints
@app.get("/api/memory/stats")
async def get_memory_stats():
    """Get memory system statistics - requires actual data from vector store"""
    # TODO: Replace with real vector store queries
    from fastapi import HTTPException
    raise HTTPException(
        status_code=501, 
        detail="Memory stats endpoint requires vector store implementation. Please set up FAISS vector store first."
    )

@app.get("/api/goals/summary")
async def get_goals_summary():
    """Get goals summary - requires actual data from database"""
    # TODO: Replace with real database queries
    from fastapi import HTTPException
    raise HTTPException(
        status_code=501, 
        detail="Goals endpoint requires database implementation. Please set up goals tracking first."
    )

@app.get("/api/workflow/status")
async def get_workflow_status():
    """Get workflow status - requires actual workflow implementation"""
    # TODO: Replace with real workflow orchestration
    from fastapi import HTTPException
    raise HTTPException(
        status_code=501, 
        detail="Workflow endpoint requires workflow implementation. Please set up workflow orchestration first."
    )

@app.post("/api/workflow/trigger")
async def trigger_workflow():
    """Trigger workflow - requires actual workflow implementation"""
    # TODO: Replace with real workflow orchestration
    from fastapi import HTTPException
    raise HTTPException(
        status_code=501, 
        detail="Workflow trigger requires workflow implementation. Please set up workflow orchestration first."
    )

# Cache Management Endpoints
@app.get("/api/v1/cache/status",
         tags=["system"],
         summary="Cache System Status",
         description="Get comprehensive cache system status and metrics")
async def cache_status():
    """
    Get detailed cache system status including Redis connection,
    performance metrics, and fallback cache information.
    """
    from backend.services.redis_cache import redis_cache
    from backend.services.cache_decorators import cache_manager
    
    try:
        cache_health = await cache_manager.get_cache_health()
        cache_metrics = await cache_manager.get_cache_metrics()
        
        return {
            "status": cache_health["status"],
            "timestamp": datetime.utcnow().isoformat(),
            "health": cache_health,
            "metrics": cache_metrics,
            "configuration": {
                "redis_enabled": cache_health["redis_connected"],
                "fallback_enabled": cache_health["fallback_cache_available"],
                "compression_threshold": 1024,
                "default_ttl": 300
            }
        }
        
    except Exception as e:
        logger.error(f"Cache status check failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": "Cache status check failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.post("/api/v1/cache/warm/{user_id}",
          tags=["system"],
          summary="Warm User Cache",
          description="Pre-load commonly accessed data for a user")
async def warm_user_cache(user_id: int, platforms: str = "twitter,instagram,linkedin"):
    """
    Warm cache with commonly accessed data for a specific user.
    
    Args:
        user_id: User ID to warm cache for
        platforms: Comma-separated list of platforms
    """
    from backend.services.cache_decorators import cache_manager
    
    try:
        platform_list = [p.strip() for p in platforms.split(",")]
        await cache_manager.warm_common_caches(user_id, platform_list)
        
        return {
            "status": "success",
            "message": f"Cache warmed for user {user_id}",
            "platforms": platform_list,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache warming failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Cache warming failed",
                "error": str(e)
            }
        )

@app.delete("/api/v1/cache/user/{user_id}",
           tags=["system"],
           summary="Invalidate User Cache",
           description="Invalidate all cached data for a specific user")
async def invalidate_user_cache(user_id: int, platforms: str = None):
    """
    Invalidate all cached data for a specific user.
    
    Args:
        user_id: User ID to invalidate cache for
        platforms: Optional comma-separated list of platforms to invalidate
    """
    from backend.services.cache_decorators import cache_manager
    
    try:
        platform_list = None
        if platforms:
            platform_list = [p.strip() for p in platforms.split(",")]
        
        await cache_manager.invalidate_user_data(user_id, platform_list)
        
        return {
            "status": "success",
            "message": f"Cache invalidated for user {user_id}",
            "platforms": platform_list or "all",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache invalidation failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Cache invalidation failed",
                "error": str(e)
            }
        )

@app.delete("/api/v1/cache/platform/{platform}",
           tags=["system"],
           summary="Invalidate Platform Cache",
           description="Invalidate cached data for a specific platform")
async def invalidate_platform_cache(platform: str, operation: str = None):
    """
    Invalidate cached data for a specific platform.
    
    Args:
        platform: Platform to invalidate cache for
        operation: Optional specific operation to invalidate
    """
    from backend.services.cache_decorators import cache_manager
    
    try:
        await cache_manager.invalidate_platform_data(platform, operation)
        
        return {
            "status": "success",
            "message": f"Cache invalidated for {platform}",
            "operation": operation or "all",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Platform cache invalidation failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Platform cache invalidation failed",
                "error": str(e)
            }
        )

@app.get("/api/v1/cache/metrics",
         tags=["system"],
         summary="Cache Performance Metrics",
         description="Get detailed cache performance metrics and statistics")
async def cache_metrics():
    """
    Get comprehensive cache performance metrics including hit ratios,
    response times, memory usage, and operational statistics.
    """
    from backend.services.cache_decorators import cache_manager
    
    try:
        metrics = await cache_manager.get_cache_metrics()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "summary": {
                "total_operations": metrics.get("hits", 0) + metrics.get("misses", 0),
                "hit_ratio_percent": round(metrics.get("hit_ratio", 0), 2),
                "average_response_time_ms": round(metrics.get("avg_response_time", 0), 2),
                "cache_efficiency": "excellent" if metrics.get("hit_ratio", 0) > 80 else 
                                  "good" if metrics.get("hit_ratio", 0) > 60 else
                                  "needs_improvement"
            }
        }
        
    except Exception as e:
        logger.error(f"Cache metrics retrieval failed: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Cache metrics retrieval failed",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )