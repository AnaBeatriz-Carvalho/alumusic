from celery_app import celery
from celery.utils.log import get_task_logger
from app import create_app
from redis import Redis
import json
from app.extensions import db
from app.models.summary import WeeklySummary
from app.core.reporting_service import generate_charts
from app.core.llm_service import generate_weekly_summary
from datetime import date, timedelta

logger = get_task_logger(__name__)

@celery.task
def weekly_summary_task():
    """Aggregate data, call LLM to generate a weekly summary, store it and email stakeholders."""
    app = create_app()
    with app.app_context():
        try:
            # Define period: last 7 days
            end = date.today()
            start = end - timedelta(days=7)

            # Generate charts (reporting_service returns list of chart dicts)
            charts = generate_charts()

            # Ask LLM to produce subject/body
            summary = generate_weekly_summary(charts)

            # Persist into DB
            ws = WeeklySummary(
                period_start=start,
                period_end=end,
                subject=summary.get('subject', 'Resumo Semanal'),
                body=summary.get('body', ''),
                charts_json=summary.get('charts_json')
            )
            db.session.add(ws)
            db.session.commit()

            # NOTE: email sending was removed per user request. The summary is persisted
            # and can be retrieved via the admin endpoint for manual review.
            logger.info("Weekly summary generated and persisted")
        except Exception as e:
            logger.error(f"Failed to generate weekly summary: {e}", exc_info=True)
