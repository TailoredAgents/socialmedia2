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
    
    # Auth0
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_audience: str = ""
    
    # JWT
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis/Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Social Media APIs
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    twitter_client_id: str = ""  # Added missing field
    twitter_client_secret: str = ""  # Added missing field
    twitter_bearer_token: str = ""  # Added missing field
    
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
    
    # TikTok
    tiktok_client_id: str = ""
    tiktok_client_secret: str = ""
    tiktok_access_token: str = ""
    
    # Server
    port: int = 8000
    host: str = "0.0.0.0"
    
    # CORS & Security
    allowed_hosts: str = "localhost,127.0.0.1"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Production Features
    demo_mode: str = "false"
    mock_social_apis: str = "false"
    show_sample_data: str = "false"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL based on environment"""
        if self.environment == "production" and self.postgres_url:
            return self.postgres_url
        return self.database_url

@lru_cache()
def get_settings():
    return Settings()