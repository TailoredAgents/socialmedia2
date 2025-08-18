"""
Centralized router registry for all API endpoints
"""
from . import (
    auth,
    auth_fastapi_users,
    content,
    goals,
    memory,
    workflow_v2,
    monitoring,
    diagnostics,
    content_history,
    notifications,
    vector_search,
    similarity,
    deep_research,
    integration_services,
    feature_flags,
    autonomous,
    performance_monitoring,
)

# All routers to be registered with the FastAPI app
ROUTERS = [
    auth_fastapi_users.router,  # FastAPI Users authentication (primary)
    auth.router,  # Legacy auth endpoints (will be phased out)
    content.router,
    goals.router,
    memory.router,
    workflow_v2.router,
    monitoring.router,
    diagnostics.router,
    content_history.router,
    notifications.router,
    vector_search.router,
    similarity.router,
    deep_research.router,
    integration_services.router,
    feature_flags.router,
    autonomous.router,
    performance_monitoring.router,
]