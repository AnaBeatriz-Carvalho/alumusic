
from app import create_app
from app.extensions import celery

# Create a Flask app instance to provide context
app = create_app()