# Import warning suppression FIRST before any other imports
from backend.core.suppress_warnings import suppress_third_party_warnings
suppress_third_party_warnings()

from celery import Celery
from backend.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_social_media_agent",
    broker=settings.get_celery_broker_url(),
    backend=settings.get_celery_result_backend(),
    include=[
        "backend.tasks.content_tasks",
        "backend.tasks.research_tasks", 
        "backend.tasks.posting_tasks",
        "backend.tasks.optimization_tasks",
        "backend.tasks.autonomous_scheduler",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Production autonomous schedule for fully automated operation
celery_app.conf.beat_schedule = {
    # Daily autonomous content generation at 6 AM UTC
    'autonomous-daily-content': {
        'task': 'autonomous_daily_content_generation',
        'schedule': 60.0 * 60.0 * 24,  # Daily
        'options': {'queue': 'autonomous'},
    },
    
    # Weekly performance report on Sundays at 8 AM UTC  
    'autonomous-weekly-report': {
        'task': 'autonomous_weekly_report',
        'schedule': 60.0 * 60.0 * 24 * 7,  # Weekly
        'options': {'queue': 'reports'},
    },
    
    # Nightly metrics collection at 2 AM UTC
    'autonomous-metrics-collection': {
        'task': 'autonomous_metrics_collection',
        'schedule': 60.0 * 60.0 * 24,  # Daily
        'options': {'queue': 'metrics'},
    },
    
    # Process scheduled content every 15 minutes
    'autonomous-content-posting': {
        'task': 'autonomous_content_posting',
        'schedule': 60.0 * 15,  # Every 15 minutes
        'options': {'queue': 'posting'},
    },
    
    # Legacy tasks (will be phased out)
    'legacy-research': {
        'task': 'backend.tasks.research_tasks.run_daily_research',
        'schedule': 60.0 * 60.0 * 12,  # Every 12 hours (reduced frequency)
        'options': {'queue': 'legacy'},
    },
}