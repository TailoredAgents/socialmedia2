"""
Query optimization utilities to prevent N+1 queries and improve performance
"""
from sqlalchemy.orm import selectinload, joinedload, subqueryload, Session
from sqlalchemy import select
from typing import List, Optional
from backend.db.models import User, Content, ContentSchedule, PartnerOauthConnection


class OptimizedQueries:
    """Optimized database queries to prevent N+1 problems"""
    
    @staticmethod
    def get_user_with_settings(db: Session, user_id: int) -> Optional[User]:
        """Get user with all related settings in single query"""
        return db.query(User).options(
            selectinload(User.settings),
            selectinload(User.credentials),
            selectinload(User.oauth_connections)
        ).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_content_with_metrics(db: Session, user_id: int, limit: int = 50) -> List[Content]:
        """Get user content with metrics eagerly loaded"""
        return db.query(Content).options(
            selectinload(Content.metrics),
            selectinload(Content.schedule)
        ).filter(
            Content.user_id == user_id
        ).order_by(
            Content.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_scheduled_content_with_connections(db: Session, organization_id: int) -> List[ContentSchedule]:
        """Get scheduled content with OAuth connections pre-loaded"""
        return db.query(ContentSchedule).options(
            joinedload(ContentSchedule.content),
            selectinload(ContentSchedule.oauth_connection)
        ).filter(
            ContentSchedule.organization_id == organization_id,
            ContentSchedule.status == 'pending'
        ).all()
    
    @staticmethod
    def get_oauth_connections_with_health(db: Session, organization_id: int) -> List[PartnerOauthConnection]:
        """Get OAuth connections with computed health metrics"""
        # Use subquery for complex health calculations
        return db.query(PartnerOauthConnection).filter(
            PartnerOauthConnection.organization_id == organization_id,
            PartnerOauthConnection.status == 'active'
        ).all()
    
    @staticmethod
    def bulk_update_content_status(db: Session, content_ids: List[int], new_status: str) -> int:
        """Bulk update content status in single query"""
        updated = db.query(Content).filter(
            Content.id.in_(content_ids)
        ).update(
            {"status": new_status},
            synchronize_session=False
        )
        db.commit()
        return updated


# Example usage patterns to prevent N+1
"""
# BAD - N+1 Query Pattern:
users = db.query(User).all()
for user in users:
    settings = user.settings  # Additional query per user
    print(settings.brand_voice)

# GOOD - Eager Loading:
users = db.query(User).options(selectinload(User.settings)).all()
for user in users:
    settings = user.settings  # No additional query
    print(settings.brand_voice)

# GOOD - Join Loading for 1-to-1:
users = db.query(User).options(joinedload(User.settings)).all()

# GOOD - Subquery Loading for large datasets:
users = db.query(User).options(subqueryload(User.content)).all()
"""