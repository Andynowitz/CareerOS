from app.tasks.celery_app import celery_app


@celery_app.task
def test_ai_task() -> str:
    return "AI task executed successfully"