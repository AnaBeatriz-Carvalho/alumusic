from flask import Flask
from config import config_by_name
# Importe a instância 'celery' daqui
from .extensions import db, migrate, jwt, celery

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inicializa as outras extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # =================================================================
    # ESTE É O BLOCO DE CÓDIGO MAIS IMPORTANTE PARA RESOLVER SEU PROBLEMA
    # =================================================================
    # 1. Atualiza a configuração do Celery com a do Flask
    celery.conf.update(app.config.get("CELERY", {}))
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    # =================================================================

    # Registra os Blueprints
    from .api import api_bp
    from .auth import auth_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Registra os comandos CLI
    from . import commands
    commands.register_commands(app)

    return app