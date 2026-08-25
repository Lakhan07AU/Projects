"""Medical report processing pipeline.

UPLOAD → VALIDATE → STORE ORIGINAL → CREATE JOB → TEXT EXTRACTION
→ CLASSIFICATION → ENTITY EXTRACTION → NORMALIZATION → SAVE STRUCTURED DATA
→ TREND SYNC → AI EXPLANATION → SAFETY CHECK → MARK COMPLETE

Runs in a background worker (thread or Celery). Never blocks the upload request.
"""
import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.ai.base import get_ai_provider
from app.models import (
    Consent,
    DocumentProcessingJob,
    MedicalEntity,
    MedicalReport,
    ReportStatus,
    TimelineEventType,
)
from app.services import documents, timeline as timeline_service, trends as trend_service

logger = logging.getLogger("healthsphere.pipeline")

SAFETY_BANNED_PHRASES = [
    "you have diabetes", "you definitely have", "you are diagnosed with",
    "take this medicine", "stop taking your medicine", "i prescribe",
]


def safety_validate(text: str) -> str:
    """Final safety gate on generated explanations."""
    lowered = text.lower()
    for phrase in SAFETY_BANNED_PHRASES:
        if phrase in lowered:
            return (
                "An automated summary of your extracted results is available above. "
                "Please discuss the results with a qualified healthcare professional."
            )
    return text


def process_report(db: Session, report_id: int) -> None:
    report = db.get(MedicalReport, report_id)
    if not report:
        return

    job = (
        db.query(DocumentProcessingJob)
        .filter(DocumentProcessingJob.report_id == report_id)
        .order_by(DocumentProcessingJob.id.desc())
        .first()
    )
    if not job:
        job = DocumentProcessingJob(report_id=report_id)
        db.add(job)
        db.flush()

    try:
        # ---- consent check: AI analysis can be disabled by the user ----
        ai_allowed = _ai_consent(db, report.user_id)

        # ---- text extraction ----
        job.status = "running"
        job.stage = "ocr"
        db.commit()

        from app.services.storage import get_storage

        content = get_storage().read(report.storage_key)

        if not report.extracted_text:
            text, needs_ocr = documents.extract_text(content, report.mime_type)
            if needs_ocr:
                report.status = ReportStatus.failed
                report.error_message = (
                    "We couldn't reliably extract information from this document. "
                    "Please verify the document quality or enter the relevant values "
                    "manually as health metrics."
                )
                job.status = "failed"
                job.last_error = "text extraction failed (needs OCR)"
                db.commit()
                timeline_service.add_event(
                    db,
                    user_id=report.user_id,
                    event_type=TimelineEventType.report_analyzed,
                    title="Report could not be read automatically",
                    description=report.file_name,
                    source="pipeline",
                    related_entity_type="report",
                    related_entity_id=report.id,
                )
                db.commit()
                return
            report.extracted_text = text  # never logged

        # ---- classification + entity extraction ----
        job.stage = "extraction"
        report.status = ReportStatus.analyzing
        db.commit()

        provider = get_ai_provider()
        extraction = provider.extract_medical_data(report.extracted_text)

        # Persist previous entity ids so we can replace them
        db.query(MedicalEntity).filter(MedicalEntity.report_id == report.id).delete()

        for ent in extraction.entities:
            db.add(
                MedicalEntity(
                    report_id=report.id,
                    test_name=str(ent["test_name"]),
                    value=float(ent["value"]),
                    unit=ent.get("unit"),
                    reference_low=ent.get("reference_low"),
                    reference_high=ent.get("reference_high"),
                    abnormal_flag=bool(ent.get("abnormal_flag")),
                    confidence=float(ent.get("confidence", 0.0)),
                    page_number=ent.get("page_number"),
                    source_text=(ent.get("source_text") or "")[:500],
                )
            )
        db.flush()  # session uses autoflush=False; make entities queryable

        report.category = extraction.document_type or report.category or "other"
        report.laboratory = extraction.laboratory or report.laboratory
        if extraction.report_date:
            try:
                report.report_date = datetime.strptime(extraction.report_date, "%Y-%m-%d")
            except ValueError:
                pass

        # ---- sync lab values into health metric values for trend continuity ----
        _sync_entities_to_metrics(db, report)

        # ---- AI explanation (optional; system works without it) ----
        job.stage = "analysis"
        db.commit()
        explanation = ""
        if ai_allowed:
            flagged = (
                db.query(MedicalEntity)
                .filter(MedicalEntity.report_id == report.id, MedicalEntity.abnormal_flag.is_(True))
                .all()
            )
            context_json = json.dumps({
                "flagged_results": [
                    {"test_name": e.test_name, "value": e.value, "unit": e.unit} for e in flagged
                ],
                "category": report.category,
            })
            try:
                explanation = provider.explain_report(context_json)
                explanation = safety_validate(explanation)  # final safety gate
            except Exception:
                logger.warning("AI explanation unavailable; continuing without it")
                explanation = ""
        else:
            explanation = ""

        report.analysis_summary = explanation or None
        report.status = ReportStatus.complete
        job.stage = "complete"
        job.status = "complete"

        timeline_service.add_event(
            db,
            user_id=report.user_id,
            event_type=_timeline_type(),
            title=f"Report analyzed — {len(extraction.entities)} value(s) extracted",
            description=f"{report.file_name} ({report.category.replace('_', ' ')})",
            source="pipeline",
            related_entity_type="report",
            related_entity_id=report.id,
        )
        db.commit()

    except Exception as exc:
        logger.exception("Pipeline failed for report %s", report_id)
        db.rollback()
        report = db.get(MedicalReport, report_id)
        job = (
            db.query(DocumentProcessingJob)
            .filter(DocumentProcessingJob.report_id == report_id)
            .order_by(DocumentProcessingJob.id.desc())
            .first()
        )
        if report:
            report.status = ReportStatus.failed
            report.error_message = (
                "The medical report could not be processed. Your file has been stored safely."
            )
        if job:
            job.status = "failed"
            job.last_error = str(exc)[:500]
        db.commit()


def _ai_consent(db: Session, user_id: int) -> bool:
    consent = (
        db.query(Consent)
        .filter(Consent.user_id == user_id, Consent.consent_type == "ai_analysis")
        .order_by(Consent.granted_at.desc())
        .first()
    )
    return bool(consent and consent.granted)


def _sync_entities_to_metrics(db: Session, report: MedicalReport) -> None:
    """Store extracted lab values also as health-metric points so trends unify
    manual + reported data. Only for recognized standard keys."""
    from app.models import HealthMetricValue

    key_map = {
        "hba1c": "hba1c",
        "fasting blood glucose": "blood_glucose_fasting",
        "total cholesterol": "cholesterol_total",
        "ldl cholesterol": "cholesterol_ldl",
        "hdl cholesterol": "cholesterol_hdl",
        "triglycerides": "triglycerides",
        "hemoglobin": "hemoglobin",
        "tsh": "tsh",
        "serum creatinine": "creatinine",
    }
    entities = db.query(MedicalEntity).filter(MedicalEntity.report_id == report.id).all()
    when = report.report_date or report.created_at
    for ent in entities:
        key = key_map.get(ent.test_name.lower())
        if not key:
            continue
        exists = (
            db.query(HealthMetricValue)
            .filter(
                HealthMetricValue.user_id == report.user_id,
                HealthMetricValue.metric_key == key,
                HealthMetricValue.recorded_at == when,
                HealthMetricValue.source == "report",
                HealthMetricValue.notes == f"report:{report.id}",
            )
            .first()
        )
        if exists:
            continue
        db.add(
            HealthMetricValue(
                user_id=report.user_id,
                metric_key=key,
                value=ent.value,
                unit=ent.unit,
                recorded_at=when,
                source="report",
                notes=f"report:{report.id}",
            )
        )


def _timeline_type():
    from app.models import TimelineEventType

    return TimelineEventType.report_analyzed
