from flask import Flask
from config import config_by_name
from .extensions import db, migrate, jwt, celery

    # Importa os modelos para que o Alembic os reconheça
from app.models.comment import Comentario, TagFuncionalidade

    # Registra os Blueprints (rotas)
from .api import api_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inicializa as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Atualiza a configuração do Celery com a da app
    celery.conf.update(app.config)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
