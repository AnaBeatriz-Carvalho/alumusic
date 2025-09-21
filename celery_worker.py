from app import create_app
from app.extensions import celery
from celery.schedules import crontab

app = create_app()

import tasks.process_comment
import tasks.weekly_summary # 

# Configuração da agenda de tarefas
celery.conf.beat_schedule = {
    'generate-weekly-summary-sunday-morning': {
        'task': 'tasks.weekly_summary.generate_weekly_summary_task',
        'schedule': crontab(hour=8, minute=0, day_of_week=0), # Domingo às 8h
    },
}