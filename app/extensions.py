from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from celery import Celery
from celery.schedules import crontab

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# Configuração do Celery
celery = Celery(__name__, 
                broker='redis://redis:6379/0', 
                backend='redis://redis:6379/0')
celery.conf.beat_schedule = {
    # Tarefa agendada para gerar o resumo semanal
    'generate-weekly-summary-sunday-morning': {
        # Caminho completo para a função da tarefa
        'task': 'tasks.weekly_summary.generate_weekly_summary_task',
        # Executa todo domingo às 8h da manhã
        'schedule': crontab(hour=8, minute=0, day_of_week=0),
    },
}