from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # API Keys
    openai_api_key: str = ""
    serper_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./socialmedia.db"  # Default to SQLite for development
    postgres_url: str = ""  # PostgreSQL for production
    
    # JWT (Updated with proper naming)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    jwt_secret: str = "your-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_seconds: int = 900  # 15 minutes
    jwt_refresh_ttl_seconds: int = 1209600  # 14 days
    
    # Redis/Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = ""  # Will default to redis_url if empty
    celery_result_backend: str = ""  # Will default to redis_url if empty
    
    # Social Media APIs - Twitter/X
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    twitter_bearer_token: str = ""
    
    # LinkedIn
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    linkedin_access_token: str = ""
    linkedin_user_id: str = ""
    
    # Instagram/Facebook
    instagram_app_id: str = ""
    instagram_app_secret: str = ""
    instagram_access_token: str = ""
    instagram_business_id: str = ""
    
    facebook_app_id: str = ""
    facebook_app_secret: str = ""
    facebook_access_token: str = ""
    facebook_page_id: str = ""
    facebook_page_access_token: str = ""
    
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
    return Settings()