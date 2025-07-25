"""
Goal Milestone Notification Service
Handles milestone detection and notification generation for goal progress tracking
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
from sqlalchemy.orm import Session

from backend.db.models import Goal, GoalProgress, User
from backend.core.config import get_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

class NotificationType(Enum):
    """Types of goal notifications"""
    MILESTONE_25 = "milestone_25"
    MILESTONE_50 = "milestone_50" 
    MILESTONE_75 = "milestone_75"
    MILESTONE_90 = "milestone_90"
    GOAL_COMPLETED = "goal_completed"
    GOAL_OVERDUE = "goal_overdue"
    GOAL_AT_RISK = "goal_at_risk"
    PROGRESS_STAGNANT = "progress_stagnant"
    EXCEPTIONAL_PROGRESS = "exceptional_progress"

@dataclass
class NotificationMessage:
    """Notification message structure"""
    id: str
    user_id: int
    goal_id: str
    notification_type: NotificationType
    title: str
    message: str
    priority: str  # high, medium, low
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_notification(
        self,
        db: Session,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create a new notification"""
        from backend.db.models import Notification
        
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            notification_metadata=metadata or {},
            is_read=False,
            priority="medium"
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    async def check_all_goals(self, db: Session, user_id: int) -> List[Any]:
        """Check all goals for notifications"""
        # Implementation would check for goal milestones and create notifications
        return []

class GoalNotificationService:
    """
    Goal Milestone Notification Service
    
    Features:
    - Progress milestone detection (25%, 50%, 75%, 90%, 100%)
    - Goal completion notifications
    - Overdue goal alerts
    - At-risk goal warnings (slow progress near deadline)
    - Stagnant progress detection
    - Exceptional progress recognition
    - Smart notification timing to avoid spam
    """
    
    def __init__(self):
        """Initialize the notification service"""
        self.milestone_thresholds = [25, 50, 75, 90, 100]
        self.notification_cooldown = timedelta(hours=6)  # Minimum time between similar notifications
        self.at_risk_days_threshold = 7  # Days before deadline to warn about slow progress
        self.stagnant_days_threshold = 14  # Days without progress to consider stagnant
        
        logger.info("GoalNotificationService initialized with milestone tracking")
    
    def detect_milestone_achievements(
        self, 
        goal: Goal, 
        old_progress: float, 
        new_progress: float
    ) -> List[NotificationType]:
        """
        Detect which milestones were achieved with this progress update
        
        Args:
            goal: Goal object
            old_progress: Previous progress percentage (0-100)
            new_progress: New progress percentage (0-100)
            
        Returns:
            List of achieved milestone notification types
        """
        achieved_milestones = []
        
        for threshold in self.milestone_thresholds:
            # Check if we crossed a milestone threshold
            if old_progress < threshold <= new_progress:
                if threshold == 25:
                    achieved_milestones.append(NotificationType.MILESTONE_25)
                elif threshold == 50:
                    achieved_milestones.append(NotificationType.MILESTONE_50)
                elif threshold == 75:
                    achieved_milestones.append(NotificationType.MILESTONE_75)
                elif threshold == 90:
                    achieved_milestones.append(NotificationType.MILESTONE_90)
                elif threshold >= 100:
                    achieved_milestones.append(NotificationType.GOAL_COMPLETED)
        
        return achieved_milestones
    
    def detect_exceptional_progress(
        self, 
        goal: Goal, 
        progress_change: float, 
        time_period: timedelta
    ) -> bool:
        """
        Detect if progress change is exceptionally good
        
        Args:
            goal: Goal object
            progress_change: Progress percentage change
            time_period: Time period over which change occurred
            
        Returns:
            True if progress is exceptional
        """
        # Calculate daily progress rate
        if time_period.days == 0:
            return False
            
        daily_progress_rate = progress_change / time_period.days
        
        # Determine if progress rate is exceptional based on goal type
        exceptional_thresholds = {
            "follower_growth": 5.0,  # 5% per day
            "engagement_rate": 3.0,  # 3% per day
            "reach_increase": 4.0,   # 4% per day
            "content_volume": 10.0,  # 10% per day (easier to achieve)
            "custom": 5.0            # Default threshold
        }
        
        threshold = exceptional_thresholds.get(goal.goal_type, 5.0)
        return daily_progress_rate >= threshold
    
    def detect_at_risk_goals(self, db: Session, user_id: int) -> List[Goal]:
        """
        Detect goals that are at risk of not being completed
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of at-risk goals
        """
        at_risk_goals = []
        cutoff_date = datetime.utcnow() + timedelta(days=self.at_risk_days_threshold)
        
        # Get active goals approaching deadline
        goals = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active",
            Goal.target_date <= cutoff_date
        ).all()
        
        for goal in goals:
            progress_percentage = (goal.current_value / goal.target_value) * 100 if goal.target_value > 0 else 0
            days_remaining = (goal.target_date - datetime.utcnow()).days
            
            # Calculate required daily progress to meet goal
            remaining_progress = 100 - progress_percentage
            required_daily_progress = remaining_progress / max(days_remaining, 1)
            
            # Get recent progress rate
            recent_progress = self._get_recent_progress_rate(db, goal.id, days=7)
            
            # Goal is at risk if recent progress is significantly slower than required
            if required_daily_progress > recent_progress * 2 and remaining_progress > 10:
                at_risk_goals.append(goal)
        
        return at_risk_goals
    
    def detect_stagnant_goals(self, db: Session, user_id: int) -> List[Goal]:
        """
        Detect goals with stagnant progress
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of stagnant goals
        """
        stagnant_goals = []
        cutoff_date = datetime.utcnow() - timedelta(days=self.stagnant_days_threshold)
        
        # Get active goals
        goals = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active"
        ).all()
        
        for goal in goals:
            # Check if there's been any progress in the threshold period
            recent_progress = db.query(GoalProgress).filter(
                GoalProgress.goal_id == goal.id,
                GoalProgress.recorded_at >= cutoff_date,
                GoalProgress.change_amount > 0
            ).first()
            
            if not recent_progress:
                stagnant_goals.append(goal)
        
        return stagnant_goals
    
    def _get_recent_progress_rate(self, db: Session, goal_id: str, days: int) -> float:
        """Get average daily progress rate over recent period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        progress_logs = db.query(GoalProgress).filter(
            GoalProgress.goal_id == goal_id,
            GoalProgress.recorded_at >= cutoff_date,
            GoalProgress.change_amount > 0
        ).all()
        
        if not progress_logs:
            return 0.0
        
        total_change = sum(log.change_amount for log in progress_logs)
        return total_change / days
    
    def generate_milestone_notification(
        self, 
        goal: Goal, 
        milestone_type: NotificationType,
        progress_percentage: float
    ) -> NotificationMessage:
        """
        Generate notification message for milestone achievement
        
        Args:
            goal: Goal object
            milestone_type: Type of milestone achieved
            progress_percentage: Current progress percentage
            
        Returns:
            Notification message
        """
        import uuid
        
        # Generate notification content based on milestone type
        notification_content = self._get_milestone_content(goal, milestone_type, progress_percentage)
        
        return NotificationMessage(
            id=str(uuid.uuid4()),
            user_id=goal.user_id,
            goal_id=goal.id,
            notification_type=milestone_type,
            title=notification_content["title"],
            message=notification_content["message"],
            priority=notification_content["priority"],
            action_url=f"/goals/{goal.id}",
            metadata={
                "goal_title": goal.title,
                "progress_percentage": progress_percentage,
                "target_value": goal.target_value,
                "current_value": goal.current_value,
                "goal_type": goal.goal_type,
                "platform": goal.platform
            }
        )
    
    def _get_milestone_content(
        self, 
        goal: Goal, 
        milestone_type: NotificationType, 
        progress_percentage: float
    ) -> Dict[str, str]:
        """Generate milestone-specific notification content"""
        
        content_templates = {
            NotificationType.MILESTONE_25: {
                "title": "🎯 25% Progress Milestone!",
                "message": f"Great start! You've achieved 25% progress on '{goal.title}'. Keep up the momentum!",
                "priority": "medium"
            },
            NotificationType.MILESTONE_50: {
                "title": "🚀 Halfway There!",
                "message": f"Amazing progress! You're 50% complete on '{goal.title}'. You're doing great!",
                "priority": "medium"
            },
            NotificationType.MILESTONE_75: {
                "title": "⭐ 75% Complete!",
                "message": f"Outstanding work! You've reached 75% progress on '{goal.title}'. The finish line is in sight!",
                "priority": "high"
            },
            NotificationType.MILESTONE_90: {
                "title": "🔥 90% Complete!",
                "message": f"So close! You've achieved 90% progress on '{goal.title}'. One final push to victory!",
                "priority": "high"
            },
            NotificationType.GOAL_COMPLETED: {
                "title": "🏆 Goal Achieved!",
                "message": f"Congratulations! You've successfully completed '{goal.title}'! Time to celebrate and set new goals!",
                "priority": "high"
            },
            NotificationType.GOAL_OVERDUE: {
                "title": "⏰ Goal Overdue",
                "message": f"Your goal '{goal.title}' is past its target date. Consider updating the timeline or adjusting the target.",
                "priority": "high"
            },
            NotificationType.GOAL_AT_RISK: {
                "title": "⚠️ Goal At Risk",
                "message": f"Your goal '{goal.title}' may be at risk. Current progress might not meet the target date. Consider adjusting your strategy.",
                "priority": "high"
            },
            NotificationType.PROGRESS_STAGNANT: {
                "title": "📈 Progress Update Needed",
                "message": f"No recent progress recorded for '{goal.title}'. Time to take action and move forward!",
                "priority": "medium"
            },
            NotificationType.EXCEPTIONAL_PROGRESS: {
                "title": "🌟 Exceptional Progress!",
                "message": f"Wow! Your progress on '{goal.title}' is exceptional. You're ahead of schedule - keep it up!",
                "priority": "high"
            }
        }
        
        return content_templates.get(milestone_type, {
            "title": "Goal Update",
            "message": f"Update on your goal '{goal.title}'",
            "priority": "medium"
        })
    
    async def process_goal_progress_update(
        self, 
        db: Session, 
        goal: Goal, 
        old_value: float, 
        new_value: float
    ) -> List[NotificationMessage]:
        """
        Process a goal progress update and generate appropriate notifications
        
        Args:
            db: Database session
            goal: Goal object
            old_value: Previous goal value
            new_value: New goal value
            
        Returns:
            List of notification messages to send
        """
        notifications = []
        
        if goal.target_value <= 0:
            return notifications
        
        # Calculate progress percentages
        old_progress = (old_value / goal.target_value) * 100
        new_progress = (new_value / goal.target_value) * 100
        
        # Detect milestone achievements
        achieved_milestones = self.detect_milestone_achievements(goal, old_progress, new_progress)
        
        for milestone_type in achieved_milestones:
            notification = self.generate_milestone_notification(goal, milestone_type, new_progress)
            notifications.append(notification)
        
        # Check for exceptional progress
        progress_change = new_progress - old_progress
        if progress_change > 0:
            # Assume update happened today for exceptional progress detection
            if self.detect_exceptional_progress(goal, progress_change, timedelta(days=1)):
                exceptional_notification = self.generate_milestone_notification(
                    goal, NotificationType.EXCEPTIONAL_PROGRESS, new_progress
                )
                notifications.append(exceptional_notification)
        
        logger.info(f"Generated {len(notifications)} notifications for goal {goal.id} progress update")
        return notifications
    
    async def check_all_user_goals(self, db: Session, user_id: int) -> List[NotificationMessage]:
        """
        Check all user goals for various notification conditions
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of notification messages
        """
        notifications = []
        
        # Check for at-risk goals
        at_risk_goals = self.detect_at_risk_goals(db, user_id)
        for goal in at_risk_goals:
            progress_percentage = (goal.current_value / goal.target_value) * 100 if goal.target_value > 0 else 0
            notification = self.generate_milestone_notification(goal, NotificationType.GOAL_AT_RISK, progress_percentage)
            notifications.append(notification)
        
        # Check for stagnant goals
        stagnant_goals = self.detect_stagnant_goals(db, user_id)
        for goal in stagnant_goals:
            progress_percentage = (goal.current_value / goal.target_value) * 100 if goal.target_value > 0 else 0
            notification = self.generate_milestone_notification(goal, NotificationType.PROGRESS_STAGNANT, progress_percentage)
            notifications.append(notification)
        
        # Check for overdue goals
        overdue_goals = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active",
            Goal.target_date < datetime.utcnow().date()
        ).all()
        
        for goal in overdue_goals:
            progress_percentage = (goal.current_value / goal.target_value) * 100 if goal.target_value > 0 else 0
            notification = self.generate_milestone_notification(goal, NotificationType.GOAL_OVERDUE, progress_percentage)
            notifications.append(notification)
        
        logger.info(f"Generated {len(notifications)} notifications for user {user_id} goal check")
        return notifications
    
    def format_notification_for_display(self, notification: NotificationMessage) -> Dict[str, Any]:
        """
        Format notification for frontend display
        
        Args:
            notification: Notification message
            
        Returns:
            Formatted notification for API response
        """
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "goal_id": notification.goal_id,
            "type": notification.notification_type.value,
            "title": notification.title,
            "message": notification.message,
            "priority": notification.priority,
            "action_url": notification.action_url,
            "metadata": notification.metadata,
            "created_at": notification.created_at.isoformat(),
            "is_read": False  # Default to unread
        }

# Global notification service instance
notification_service = GoalNotificationService()