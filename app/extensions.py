# app/extensions.py

import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # 👈 Importe o Migrate
from flask_jwt_extended import JWTManager  # 👈 Importe o JWTManager
from celery import Celery

# Cria a instância do banco de dados
db = SQLAlchemy()

# Cria a instância do Flask-Migrate
migrate = Migrate()  # 👈 Defina a variável 'migrate'

# Cria a instância do Flask-JWT-Extended
jwt = JWTManager()  # 👈 Defina a variável 'jwt'

# Cria a instância do Celery
celery = Celery(__name__,
                broker=os.environ.get('CELERY_BROKER_URL'),
                backend=os.environ.get('CELERY_RESULT_BACKEND'))