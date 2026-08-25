from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "healthsphere",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_max_tasks_per_child=100,
)


@celery_app.task(name="process_report", bind=True, max_retries=2)
def process_report_task(self, report_id: int):
    from app.core.database import SessionLocal
    from app.services.pipeline import process_report

    db = SessionLocal()
    try:
        process_report(db, report_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()
