"""Task queue abstraction.

- inline: executes jobs synchronously in-process (default; zero infra).
- celery: dispatches to a Celery worker (production / docker-compose).
"""
import logging

from app.core.config import settings

logger = logging.getLogger("healthsphere.tasks")


def enqueue_process_report(report_id: int) -> None:
    if settings.task_queue_mode == "celery":
        from app.workers.celery_app import process_report_task

        process_report_task.delay(report_id)
        return
    # Inline mode: run in background thread so the API request returns fast.
    import threading

    thread = threading.Thread(target=_run_inline, args=(report_id,), daemon=True)
    thread.start()


def _run_inline(report_id: int) -> None:
    from app.core.database import SessionLocal
    from app.services.pipeline import process_report

    db = SessionLocal()
    try:
        process_report(db, report_id)
    except Exception:
        logger.exception("Inline processing failed for report %s", report_id)
        db.rollback()
        _mark_failed(db, report_id)
    finally:
        db.close()


def _mark_failed(db, report_id: int) -> None:
    try:
        from app.models import MedicalReport, ReportStatus

        report = db.get(MedicalReport, report_id)
        if report and report.status != ReportStatus.complete:
            report.status = ReportStatus.failed
            report.error_message = "Processing failed unexpectedly. The file was stored safely."
            job = _get_job(db, report_id)
            if job:
                job.status = "failed"
                job.last_error = "unexpected error"
            db.commit()
    except Exception:
        logger.exception("Could not mark report %s as failed", report_id)
        db.rollback()


def _get_job(db, report_id: int):
    from app.models import DocumentProcessingJob

    return (
        db.query(DocumentProcessingJob)
        .filter(DocumentProcessingJob.report_id == report_id)
        .order_by(DocumentProcessingJob.id.desc())
        .first()
    )
