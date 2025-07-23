from celery import Celery
from backend.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_social_media_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "backend.tasks.content_tasks",
        "backend.tasks.research_tasks",
        "backend.tasks.posting_tasks",
        "backend.tasks.optimization_tasks",
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

# Schedule for daily tasks
celery_app.conf.beat_schedule = {
    'daily-research': {
        'task': 'backend.tasks.research_tasks.run_daily_research',
        'schedule': 60.0 * 60.0 * 6,  # Every 6 hours
    },
    'daily-content-generation': {
        'task': 'backend.tasks.content_tasks.generate_daily_content',
        'schedule': 60.0 * 60.0 * 8,  # Every 8 hours
    },
    'performance-optimization': {
        'task': 'backend.tasks.optimization_tasks.analyze_performance',
        'schedule': 60.0 * 60.0 * 24,  # Daily
    },
}