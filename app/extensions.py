from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# Configuração do Celery
celery = Celery(__name__, 
                broker='redis://redis:6379/0', 
                backend='redis://redis:6379/0')