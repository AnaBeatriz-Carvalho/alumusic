from flask import Flask
from config import config_by_name
from .extensions import db, migrate, jwt, celery

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inicializa as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configuração do Celery para entender o contexto da aplicação
    celery.conf.update(app.config.get("CELERY", {}))
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    
    # Registra os Blueprints
    from .api import api_bp
    from .auth import auth_bp
    from .public import public_bp # 👈 Importa o blueprint público

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # 👇 CORREÇÃO: Registra o blueprint público com o prefixo /api
    #    Isso cria a rota final /api/relatorio/semana
    app.register_blueprint(public_bp, url_prefix='/api')

    # Registra os comandos CLI
    from . import commands
    commands.register_commands(app)

    return app

    
