from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from celery import Celery  # Importe a classe Celery

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


celery = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
