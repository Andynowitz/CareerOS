from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "careeros",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.ai_tasks",
        "app.tasks.job_analysis",
        "app.tasks.job_insight",
        "app.tasks.resume_analysis",
    ],
)