from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

def get_utc_now() -> datetime:
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Environment - Auto-detect production on Render
    environment: str = os.getenv("ENVIRONMENT", os.getenv("RENDER", "development") and "production" or "development")
    debug: bool = os.getenv("ENVIRONMENT", "").lower() != "production"
    
    # API Keys
    openai_api_key: str = ""
    xai_api_key: str = ""
    serper_api_key: str = ""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")  # PostgreSQL from environment
    postgres_url: str = os.getenv("DATABASE_URL", "")  # PostgreSQL for production (same as database_url)
    
    def get_database_url(self) -> str:
        """Get database URL with PostgreSQL preference and Render SSL support"""
        db_url = self.database_url or os.getenv("DATABASE_URL")
        if not db_url:
            # Fallback to SQLite only in development
            if self.environment == "development":
                return "sqlite:///./socialmedia.db"
            else:
                raise ValueError("DATABASE_URL must be set in production environment")
        
        # Add SSL mode for Render PostgreSQL if not already present
        if db_url.startswith("postgresql://") and "sslmode" not in db_url:
            db_url += "?sslmode=require"
        
        return db_url
    
    def validate_production_config(self) -> List[str]:
        """Validate production configuration and return missing required fields"""
        missing_fields = []
        
        if self.environment == "production":
            # Critical security fields
            if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-change-this-in-production":
                missing_fields.append("SECRET_KEY")
            
            if not self.encryption_key or self.encryption_key == "your-32-byte-encryption-key-change-this":
                missing_fields.append("ENCRYPTION_KEY")
            
            # Database
            if not self.get_database_url():
                missing_fields.append("DATABASE_URL")
            
            # Redis
            if not self.redis_url or self.redis_url == "redis://localhost:6379/0":
                missing_fields.append("REDIS_URL")
            
            # OpenAI API key (required for most features)
            if not self.openai_api_key:
                missing_fields.append("OPENAI_API_KEY")
        
        return missing_fields
    
    # JWT (Updated with proper naming and production security)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your-32-byte-encryption-key-change-this")
    jwt_secret: str = "your-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_seconds: int = 900  # 15 minutes (secure for production)
    jwt_refresh_ttl_seconds: int = 604800  # 7 days (reduced from 14 for security)
    
    # Redis/Celery
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    celery_broker_url: str = ""  # Will default to redis_url if empty
    celery_result_backend: str = ""  # Will default to redis_url if empty
    
    # Social Media APIs - Twitter/X OAuth 2.0 (Primary)
    twitter_client_id: str = ""
    twitter_client_secret: str = ""
    
    # Twitter API (Legacy - for backwards compatibility)
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    twitter_bearer_token: str = ""
    
    # LinkedIn - REMOVED (too restrictive API)
    
    # Meta Graph API (2025) - Unified Facebook/Instagram
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_access_token: str = ""
    meta_api_version: str = "v22.0"
    
    # Facebook Page
    facebook_page_id: str = ""
    facebook_page_access_token: str = ""
    
    # Instagram Business Account
    instagram_business_account_id: str = ""
    
    # Legacy (backwards compatibility)
    facebook_app_id: str = ""  # Maps to meta_app_id
    facebook_app_secret: str = ""  # Maps to meta_app_secret
    instagram_app_id: str = ""  # Maps to meta_app_id
    instagram_app_secret: str = ""  # Maps to meta_app_secret
    
    # Server
    port: int = 8000
    host: str = "0.0.0.0"
    
    # CORS & Security
    allowed_hosts: str = "localhost,127.0.0.1,lily-ai-socialmedia.com,www.lily-ai-socialmedia.com,api.lily-ai-socialmedia.com"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,https://lily-ai-socialmedia.com,https://www.lily-ai-socialmedia.com"
    
    # Feature Flags
    feature_flags: str = ""
    
    # OpenTelemetry
    otel_service_name: str = "ai-social-agent-api"
    otel_exporter_otlp_endpoint: str = ""
    
    # Monitoring & Observability
    sentry_dsn: str = ""
    prometheus_enabled: bool = False
    
    # Production Features (Hardened defaults)
    demo_mode: str = "false"
    mock_social_apis: str = "false"
    show_sample_data: str = "false"
    enable_registration: str = "false"  # Disabled by default for security
    require_email_verification: str = "true"  # Enabled by default for security
    
    # Timezone Configuration
    timezone: str = "America/New_York"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL based on environment"""
        if self.environment == "production" and self.postgres_url:
            return self.postgres_url
        return self.database_url
    
    def get_celery_broker_url(self) -> str:
        """Get Celery broker URL, defaulting to redis_url if not set"""
        return self.celery_broker_url or self.redis_url
    
    def get_celery_result_backend(self) -> str:
        """Get Celery result backend URL, defaulting to redis_url if not set"""
        return self.celery_result_backend or self.redis_url

@lru_cache()
def get_settings():
    """Get settings instance based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    # Force production settings when DATABASE_URL is set (Render/Heroku pattern)
    if os.getenv("DATABASE_URL") and not os.getenv("DATABASE_URL").startswith("sqlite"):
        settings = Settings()
        settings.environment = "production"
        settings.debug = False
        return settings
    
    return Settings()

# Global settings instance
settings = get_settings()