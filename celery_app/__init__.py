# celery_app/__init__.py
from app.extensions import celery

# Importa as tarefas para que o Celery as encontre ao iniciar
import tasks.process_comment
import tasks.process_uploaded_file
import tasks.weekly_summary