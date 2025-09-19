# celery_worker.py

from app import create_app
from app.extensions import celery


app = create_app()

import tasks.process_comment