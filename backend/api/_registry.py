"""
Centralized router registry for all API endpoints
"""
from . import (
    auth,
    auth_fastapi_users,
    admin,
    user_credentials,
    content,
    goals,
    memory,
    workflow_v2,
    monitoring,
    diagnostics,
    content_history,
    notifications,
    vector_search,
    vector_search_production,
    similarity,
    deep_research,
    integration_services,
    feature_flags,
    autonomous,
    performance_monitoring,
    social_platforms,
    organizations,
)

# All routers to be registered with the FastAPI app
ROUTERS = [
    auth_fastapi_users.router,  # FastAPI Users authentication (primary)
    auth.router,  # Real JWT auth endpoints with registration key validation
    admin.router,  # Admin authentication and management system
    user_credentials.router,  # User social media credentials management
    content.router,
    goals.router,
    memory.router,
    workflow_v2.router,
    monitoring.router,
    diagnostics.router,
    content_history.router,
    notifications.router,
    vector_search_production.router,  # Production pgvector search (primary)
    vector_search.router,  # Legacy vector search (will be phased out)
    similarity.router,
    deep_research.router,
    integration_services.router,
    feature_flags.router,
    autonomous.router,
    performance_monitoring.router,
    social_platforms.router,  # Social media platform connections and posting
    organizations.router,  # Multi-tenant organization management
]