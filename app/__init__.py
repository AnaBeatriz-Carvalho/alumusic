from flask import Flask, logging
from config import config_by_name
from .extensions import db, migrate, jwt, celery
from .auth import auth_bp
from .api import api_bp

# Importa os modelos para que o Alembic os reconheça
from app.models.comment import Comentario, TagFuncionalidade

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Atualiza a configuração do Celery
    celery.conf.update(app.config)

    # Importa modelos para Alembic
    from app.models.comment import Comentario, TagFuncionalidade
    from app.models.user import Usuario

    import logging
    app.logger.setLevel(logging.DEBUG)
    # Registra Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
