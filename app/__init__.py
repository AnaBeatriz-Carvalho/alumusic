# app/__init__.py

from flask import Flask
from config import config_by_name
from .extensions import db, migrate, jwt, celery

# 👇 IMPORTAÇÃO CORRIGIDA AQUI 👇
# Importe os modelos aqui, na ordem correta, para que o Alembic os reconheça.
# O modelo 'Usuario' deve vir ANTES do 'Comentario', pois 'Comentario' depende de 'Usuario'.
from app.models.user import Usuario
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

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    import logging
    app.logger.setLevel(logging.DEBUG)
    
    # Registra Blueprints
    from .api import api_bp
    from .auth import auth_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app