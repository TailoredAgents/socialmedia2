from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    tier = Column(String, default="base")  # base, pro, enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    content_logs = relationship("ContentLog", back_populates="user")
    metrics = relationship("Metric", back_populates="user")
    user_settings = relationship("UserSetting", back_populates="user", uselist=False)

class ContentLog(Base):
    __tablename__ = "content_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)  # twitter, linkedin, instagram
    content = Column(Text, nullable=False)
    content_type = Column(String, nullable=False)  # text, image, video
    status = Column(String, default="draft")  # draft, scheduled, published, failed
    engagement_data = Column(JSON, default={})
    scheduled_for = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # External IDs
    platform_post_id = Column(String)  # ID from social platform
    
    # Relationships
    user = relationship("User", back_populates="content_logs")

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    metric_type = Column(String, nullable=False)  # engagement, reach, followers, etc.
    platform = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    date_recorded = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="metrics")

class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Brand settings
    brand_name = Column(String)
    brand_voice = Column(String, default="professional")
    primary_color = Column(String, default="#3b82f6")
    logo_url = Column(String)
    
    # Content preferences
    content_frequency = Column(Integer, default=3)  # posts per week
    preferred_platforms = Column(JSON, default=["twitter", "linkedin"])
    posting_times = Column(JSON, default={"twitter": "09:00", "linkedin": "10:00"})
    
    # AI settings
    creativity_level = Column(Float, default=0.7)  # 0-1 scale
    enable_images = Column(Boolean, default=True)
    enable_repurposing = Column(Boolean, default=True)
    
    # Integrations
    connected_accounts = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_settings")

class ResearchData(Base):
    __tablename__ = "research_data"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String)
    platform_source = Column(String)  # twitter, web, etc.
    relevance_score = Column(Float, default=0.0)
    embedding_id = Column(String)  # FAISS vector ID
    tags = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Content categorization
    sentiment = Column(String)  # positive, negative, neutral
    topic_category = Column(String)
    trending_score = Column(Float, default=0.0)