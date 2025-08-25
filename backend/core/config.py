from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True
    
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
                raise ValueError("DATABASE_URL must be set in production")
        
        # Add SSL mode for Render PostgreSQL if not already present
        if db_url.startswith("postgresql://") and "sslmode" not in db_url:
            db_url += "?sslmode=require"
        
        return db_url
    
    # JWT (Updated with proper naming)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your-32-byte-encryption-key-change-this")
    jwt_secret: str = "your-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_seconds: int = 900  # 15 minutes
    jwt_refresh_ttl_seconds: int = 1209600  # 14 days
    
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
    
    # Production Features
    demo_mode: str = "false"
    mock_social_apis: str = "false"
    show_sample_data: str = "false"
    enable_registration: str = "true"
    require_email_verification: str = "false"
    
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