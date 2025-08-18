from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from backend.db.database import Base
import uuid

# Import multi-tenant models to ensure all relationships are properly established
from backend.db.multi_tenant_models import (
    Organization, Team, Role, Permission, OrganizationInvitation, 
    UserOrganizationRole, user_teams, role_permissions
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String)  # For local authentication
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)  # For FastAPI Users
    is_verified = Column(Boolean, default=False)  # For FastAPI Users
    tier = Column(String, default="base")  # base, pro, enterprise
    auth_provider = Column(String, default="local")  # local, auth0
    
    # Multi-tenancy: Default organization for personal accounts
    default_organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    content_logs = relationship("ContentLog", back_populates="user")
    metrics = relationship("Metric", back_populates="user")
    user_settings = relationship("UserSetting", back_populates="user", uselist=False)
    goals = relationship("Goal", back_populates="user")
    workflow_executions = relationship("WorkflowExecution", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    # Multi-tenancy relationships
    default_organization = relationship("Organization", foreign_keys=[default_organization_id])
    teams = relationship("Team", secondary="user_teams", back_populates="members")
    organization_roles = relationship("UserOrganizationRole", back_populates="user")
    
    # Organization ownership and invitations
    owned_organizations = relationship("Organization", foreign_keys="Organization.owner_id")
    sent_invitations = relationship("OrganizationInvitation", foreign_keys="OrganizationInvitation.invited_by_id")
    received_invitations = relationship("OrganizationInvitation", foreign_keys="OrganizationInvitation.invited_user_id")

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
    external_post_id = Column(String, index=True)  # For idempotency tracking
    
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
    metric_metadata = Column(JSON, default={})
    
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
    enable_autonomous_mode = Column(Boolean, default=False)  # For autonomous scheduling
    timezone = Column(String, default="UTC")  # User timezone for scheduling
    
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


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True)  # UUID string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    goal_type = Column(String, nullable=False)  # follower_growth, engagement_rate, etc.
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    target_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="active")  # active, paused, completed, failed
    platform = Column(String)  # optional platform-specific goal
    
    # Progress tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Metadata
    goal_metadata = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="goals")
    progress_logs = relationship("GoalProgress", back_populates="goal")
    milestones = relationship("Milestone", back_populates="goal")


class GoalProgress(Base):
    __tablename__ = "goal_progress"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(String, ForeignKey("goals.id"), nullable=False)
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    change_amount = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String)  # manual, automatic, import
    notes = Column(Text)
    
    # Relationships
    goal = relationship("Goal", back_populates="progress_logs")


class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(String, ForeignKey("goals.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    target_value = Column(Float, nullable=False)
    target_date = Column(DateTime(timezone=True))
    achieved = Column(Boolean, default=False)
    achieved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    goal = relationship("Goal", back_populates="milestones")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    memory_type = Column(String, nullable=False)  # content, research, template, trend, insight
    vector_id = Column(String, index=True)  # FAISS vector ID
    relevance_score = Column(Float, default=1.0)
    
    # Metadata
    memory_metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Performance tracking
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True))


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text, nullable=False)
    platform = Column(String, nullable=False)
    status = Column(String, default="draft")  # draft, scheduled, published
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    
    # Engagement metrics
    engagement_data = Column(JSON, default={})
    performance_score = Column(Float, default=0.0)
    
    # AI generation metadata
    ai_model = Column(String)
    prompt_used = Column(Text)
    generation_params = Column(JSON, default={})
    
    # Vector reference
    memory_id = Column(Integer, ForeignKey("memories.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContentItem(Base):
    """Enhanced content model with comprehensive metadata and performance tracking"""
    __tablename__ = "content_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String, index=True)  # SHA256 hash for deduplication
    
    # Platform and type information
    platform = Column(String, nullable=False, index=True)  # twitter, linkedin, instagram, facebook
    content_type = Column(String, nullable=False, index=True)  # text, image, video, carousel, story
    content_format = Column(String)  # post, thread, article, etc.
    
    # Status tracking
    status = Column(String, default="draft", index=True)  # draft, scheduled, published, failed, archived
    published_at = Column(DateTime(timezone=True), index=True)
    scheduled_for = Column(DateTime(timezone=True), index=True)
    
    # External platform references
    platform_post_id = Column(String, index=True)  # ID from social media platform
    platform_url = Column(String)  # Direct URL to the post
    
    # FAISS vector integration
    embedding_id = Column(String, index=True)  # Reference to FAISS vector store
    embedding_model = Column(String, default="text-embedding-ada-002")
    
    # Performance metrics (updated by background tasks)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)  # retweets, reposts, etc.
    comments_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)  # impressions, views
    click_count = Column(Integer, default=0)  # link clicks
    engagement_rate = Column(Float, default=0.0)  # calculated metric
    
    # Performance categorization
    performance_tier = Column(String, default="unknown", index=True)  # viral, high, medium, low, poor
    viral_score = Column(Float, default=0.0)  # 0-1 score for viral potential
    
    # Content categorization and analysis
    topic_category = Column(String, index=True)  # AI-determined topic
    sentiment = Column(String, index=True)  # positive, negative, neutral
    tone = Column(String)  # professional, casual, humorous, etc.
    reading_level = Column(String)  # beginner, intermediate, advanced
    
    # AI generation metadata
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String)  # gpt-4, gpt-3.5-turbo, etc.
    generation_prompt = Column(Text)
    generation_params = Column(JSON, default={})
    
    # Content optimization
    hashtags = Column(JSON, default=[])  # extracted hashtags
    mentions = Column(JSON, default=[])  # @mentions
    links = Column(JSON, default=[])  # URLs in content
    keywords = Column(JSON, default=[])  # SEO keywords
    
    # Timing and scheduling optimization
    optimal_posting_time = Column(DateTime(timezone=True))
    time_zone = Column(String, default="UTC")
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    hour_of_day = Column(Integer)  # 0-23
    
    # Content relationships
    parent_content_id = Column(String, ForeignKey("content_items.id"))  # For repurposed content
    template_id = Column(String)  # Template used for generation
    campaign_id = Column(String)  # Marketing campaign association
    
    # A/B testing
    ab_test_group = Column(String)  # A, B, C, etc.
    ab_test_id = Column(String, index=True)  # Test identifier
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String)  # User ID who approved
    approved_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    
    # Quality metrics
    content_quality_score = Column(Float, default=0.0)  # AI-calculated quality
    brand_voice_alignment = Column(Float, default=0.0)  # Brand consistency score
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_performance_update = Column(DateTime(timezone=True))
    
    # Additional metadata
    content_metadata = Column(JSON, default={})
    
    # Relationships
    user = relationship("User")
    parent_content = relationship("ContentItem", remote_side=[id])
    performance_snapshots = relationship("ContentPerformanceSnapshot", back_populates="content_item")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_content_user_platform', user_id, platform),
        Index('idx_content_performance', performance_tier, engagement_rate),
        Index('idx_content_topic_sentiment', topic_category, sentiment),
        Index('idx_content_created_platform', created_at, platform),
        Index('idx_content_ab_test', ab_test_id, ab_test_group),
    )


class ContentPerformanceSnapshot(Base):
    """Time-series performance data for content items"""
    __tablename__ = "content_performance_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(String, ForeignKey("content_items.id"), nullable=False)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Performance metrics at this point in time
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Growth metrics (since last snapshot)
    likes_growth = Column(Integer, default=0)
    shares_growth = Column(Integer, default=0)
    comments_growth = Column(Integer, default=0)
    reach_growth = Column(Integer, default=0)
    
    # Velocity metrics (per hour/day)
    engagement_velocity = Column(Float, default=0.0)
    viral_coefficient = Column(Float, default=0.0)
    
    # Platform-specific metrics
    platform_metrics = Column(JSON, default={})
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="performance_snapshots")
    
    __table_args__ = (
        Index('idx_snapshot_content_time', content_item_id, snapshot_time),
    )


class ContentCategory(Base):
    """Hierarchical content categorization system"""
    __tablename__ = "content_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("content_categories.id"))
    
    # Category metadata
    color = Column(String, default="#6B7280")  # Hex color for UI
    icon = Column(String)  # Icon identifier
    
    # Performance tracking at category level
    avg_engagement_rate = Column(Float, default=0.0)
    total_content_count = Column(Integer, default=0)
    
    # AI training data
    keywords = Column(JSON, default=[])  # Keywords associated with category
    training_samples = Column(JSON, default=[])  # Sample content for AI classification
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("ContentCategory", remote_side=[id])
    children = relationship("ContentCategory")


class ContentTemplate(Base):
    """Reusable content templates for consistent generation"""
    __tablename__ = "content_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Template content
    template_content = Column(Text, nullable=False)  # With placeholders like {topic}, {insight}
    prompt_template = Column(Text)  # AI prompt template
    
    # Template metadata
    platform = Column(String, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("content_categories.id"))
    content_type = Column(String, nullable=False)  # text, image, video
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    avg_performance = Column(Float, default=0.0)  # Average engagement of content using this template
    
    # Template configuration
    variables = Column(JSON, default=[])  # List of template variables
    constraints = Column(JSON, default={})  # Length limits, required elements, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Shareable templates
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    category = relationship("ContentCategory")


class MemoryContent(Base):
    """Legacy table - keeping for backward compatibility"""
    __tablename__ = "memory_content"

    id = Column(String, primary_key=True)  # UUID string
    content = Column(Text, nullable=False)
    content_type = Column(String, nullable=False)  # research, post, insight, trend
    source = Column(String)  # twitter, web, manual, generated
    platform = Column(String)  # platform this content relates to
    
    # Vector storage
    embedding_id = Column(String)  # Reference to FAISS vector
    similarity_cluster = Column(String)  # Cluster for similar content
    
    # Performance data
    engagement_score = Column(Float, default=0.0)
    performance_tier = Column(String, default="unknown")  # high, medium, low
    
    # Categorization
    tags = Column(JSON, default=[])
    sentiment = Column(String)  # positive, negative, neutral
    topic_category = Column(String)
    relevance_score = Column(Float, default=0.5)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Metadata
    content_metadata = Column(JSON, default={})


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(String, primary_key=True)  # UUID string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workflow_type = Column(String, nullable=False)  # daily, optimization, manual
    status = Column(String, default="running")  # running, completed, failed, cancelled
    
    # Execution details
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Workflow stages
    current_stage = Column(String)
    completed_stages = Column(JSON, default=[])
    failed_stages = Column(JSON, default=[])
    
    # Results
    content_generated = Column(Integer, default=0)
    posts_scheduled = Column(Integer, default=0)
    research_items = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    execution_params = Column(JSON, default={})
    results_summary = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="workflow_executions")


class Notification(Base):
    """User notifications for goals and system events"""
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification content
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False, index=True)  # milestone_25, goal_completed, etc.
    priority = Column(String, default="medium")  # high, medium, low
    
    # Related entities
    goal_id = Column(String, ForeignKey("goals.id"), nullable=True)
    content_id = Column(String, nullable=True)  # For content-related notifications
    workflow_id = Column(String, nullable=True)  # For workflow notifications
    
    # Notification state
    is_read = Column(Boolean, default=False, index=True)
    is_dismissed = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    # Action data
    action_url = Column(String)  # URL to navigate to when clicked
    action_label = Column(String)  # Button text for action
    
    # Metadata
    notification_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True))  # Optional expiration
    
    # Relationships
    user = relationship("User")
    goal = relationship("Goal")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_notification_user_read', user_id, is_read),
        Index('idx_notification_user_type', user_id, notification_type),
        Index('idx_notification_created', created_at.desc()),
    )


class RefreshTokenBlacklist(Base):
    """Store revoked/blacklisted refresh tokens"""
    __tablename__ = "refresh_token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String, unique=True, index=True, nullable=False)  # JWT ID claim
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Original token expiration
    
    # Relationships
    user = relationship("User")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blacklist_token_user', token_jti, user_id),
        Index('idx_blacklist_expires', expires_at),
    )


# Social Platform Connection Models

class SocialPlatformConnection(Base):
    """Stores OAuth tokens and connection details for social platforms"""
    __tablename__ = "social_platform_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)  # twitter, linkedin, instagram, facebook
    
    # Platform account details
    platform_user_id = Column(String, nullable=False, index=True)  # ID from the platform
    platform_username = Column(String, nullable=False)  # @username or handle
    platform_display_name = Column(String)  # Full name or display name
    profile_image_url = Column(String)
    profile_url = Column(String)
    
    # OAuth tokens (encrypted at rest)
    access_token = Column(Text, nullable=False)  # Encrypted OAuth access token
    refresh_token = Column(Text)  # Encrypted OAuth refresh token (if available)
    token_expires_at = Column(DateTime(timezone=True))  # Token expiration
    
    # Token metadata
    token_type = Column(String, default="Bearer")  # Token type (Bearer, etc.)
    scope = Column(String)  # OAuth scopes granted
    
    # Connection status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)  # Platform verification status
    connection_status = Column(String, default="connected")  # connected, expired, revoked, error
    
    # Platform-specific metadata
    platform_metadata = Column(JSON, default={})  # Follower count, verified status, etc.
    
    # Rate limiting info
    rate_limit_remaining = Column(Integer)
    rate_limit_reset = Column(DateTime(timezone=True))
    daily_post_count = Column(Integer, default=0)
    daily_post_limit = Column(Integer)  # Platform-specific limits
    
    # Error tracking
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    last_error_at = Column(DateTime(timezone=True))
    
    # Posting preferences for this connection
    auto_post_enabled = Column(Boolean, default=True)
    preferred_posting_times = Column(JSON, default={})  # {"weekdays": "09:00", "weekends": "10:00"}
    content_filters = Column(JSON, default={})  # Content type preferences, hashtag rules, etc.
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))
    last_refreshed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    posts = relationship("SocialPost", back_populates="connection")
    
    # Unique constraint: one connection per platform per user
    __table_args__ = (
        Index('idx_social_conn_user_platform', user_id, platform),
        Index('idx_social_conn_platform_user', platform, platform_user_id),
    )


class SocialPost(Base):
    """Tracks posts made to social platforms with detailed metadata"""
    __tablename__ = "social_posts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    connection_id = Column(Integer, ForeignKey("social_platform_connections.id"), nullable=False)
    content_item_id = Column(String, ForeignKey("content_items.id"), nullable=True)  # Link to original content
    
    # Platform details
    platform = Column(String, nullable=False, index=True)
    platform_post_id = Column(String, nullable=False, index=True)  # ID from the platform
    platform_url = Column(String)  # Direct URL to the post
    
    # Post content
    content_text = Column(Text)
    media_urls = Column(JSON, default=[])  # Images, videos attached
    hashtags = Column(JSON, default=[])
    mentions = Column(JSON, default=[])
    
    # Post type and format
    post_type = Column(String, default="text")  # text, image, video, carousel, story, reel
    post_format = Column(String)  # single, thread, article (for LinkedIn)
    
    # Scheduling and timing
    scheduled_for = Column(DateTime(timezone=True))
    posted_at = Column(DateTime(timezone=True), index=True)
    
    # Status tracking
    status = Column(String, default="draft", index=True)  # draft, scheduled, posted, failed, deleted
    failure_reason = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Performance metrics (updated by background jobs)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)  # retweets, reposts, etc.
    comments_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)  # impressions, views
    click_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Performance tracking
    last_metrics_update = Column(DateTime(timezone=True))
    metrics_update_count = Column(Integer, default=0)
    peak_engagement_time = Column(DateTime(timezone=True))
    
    # Platform-specific metrics
    platform_metrics = Column(JSON, default={})  # Platform-specific engagement data
    
    # Content analysis
    sentiment = Column(String)  # positive, negative, neutral
    topics = Column(JSON, default=[])  # AI-extracted topics
    keywords = Column(JSON, default=[])
    
    # Campaign and tracking
    campaign_id = Column(String, index=True)
    utm_parameters = Column(JSON, default={})  # UTM tracking for links
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    connection = relationship("SocialPlatformConnection", back_populates="posts")
    content_item = relationship("ContentItem")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_social_post_user_platform', user_id, platform),
        Index('idx_social_post_connection_status', connection_id, status),
        Index('idx_social_post_posted_engagement', posted_at, engagement_rate),
        Index('idx_social_post_campaign', campaign_id),
    )


class PlatformMetricsSnapshot(Base):
    """Time-series snapshots of account metrics across platforms"""
    __tablename__ = "platform_metrics_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("social_platform_connections.id"), nullable=False)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Account metrics
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    
    # Engagement metrics
    avg_likes_per_post = Column(Float, default=0.0)
    avg_comments_per_post = Column(Float, default=0.0)
    avg_shares_per_post = Column(Float, default=0.0)
    overall_engagement_rate = Column(Float, default=0.0)
    
    # Growth metrics (calculated)
    followers_growth = Column(Integer, default=0)  # Since last snapshot
    posts_growth = Column(Integer, default=0)
    engagement_growth = Column(Float, default=0.0)
    
    # Platform-specific metrics
    platform_specific_metrics = Column(JSON, default={})
    
    # Relationships
    connection = relationship("SocialPlatformConnection")
    
    __table_args__ = (
        Index('idx_metrics_snapshot_conn_time', connection_id, snapshot_time),
    )


class SocialPostTemplate(Base):
    """Platform-specific post templates with formatting rules"""
    __tablename__ = "social_post_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Platform and formatting
    platform = Column(String, nullable=False, index=True)
    post_type = Column(String, nullable=False)  # text, image, video, thread
    
    # Template content
    template_text = Column(Text, nullable=False)  # With variables like {topic}, {insight}
    hashtag_template = Column(String)  # Hashtag pattern
    
    # Platform-specific formatting
    max_length = Column(Integer)  # Character limit
    thread_split_rules = Column(JSON, default={})  # For Twitter threads
    formatting_rules = Column(JSON, default={})  # Bold, italic, links, etc.
    
    # Usage and performance
    usage_count = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)
    
    # Template metadata
    variables = Column(JSON, default=[])  # List of template variables
    required_media = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_social_template_user_platform', user_id, platform),
    )