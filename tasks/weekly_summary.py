from celery_app import celery
from celery.utils.log import get_task_logger
from app import create_app
from datetime import datetime, timedelta

logger = get_task_logger(__name__)

@celery.task
def generate_weekly_summary_task():
    app = create_app()
    with app.app_context():
        from app.extensions import db
        from app.models.comment import Comentario
        from app.models.summary import WeeklySummary
        from app.models.stakeholder import Stakeholder
        from app.core.llm_service import generate_weekly_summary
        from app.core.email_service import send_summary_email

        logger.info("Iniciando a tarefa de resumo semanal...")
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)

        comments = db.session.query(Comentario.texto).filter(
            Comentario.status == 'CONCLUIDO',
            Comentario.data_recebimento.between(start_date, end_date)
        ).all()

        if not comments:
            logger.info("Nenhum comentário novo na última semana. Nenhum resumo gerado.")
            return

        comment_texts = [c.texto for c in comments]
        summary_text = generate_weekly_summary(comment_texts)
        
        new_summary = WeeklySummary(start_date=start_date, end_date=end_date, summary_text=summary_text)
        db.session.add(new_summary)
        db.session.commit()
        logger.info(f"Novo resumo semanal salvo no banco de dados.")

        stakeholders = db.session.query(Stakeholder.email).all()
        recipients = [s.email for s in stakeholders]
        if recipients:
            send_summary_email(summary_text, start_date, end_date, recipients)