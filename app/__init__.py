from flask import Flask
from config import config_by_name
from .extensions import db, migrate, jwt, celery

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configuração do Celery com contexto do Flask
    celery.conf.update(app.config.get("CELERY", {}))
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    # Registra os blueprints
    from .api import api_bp
    from .auth import auth_bp
    from .public import public_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(public_bp, url_prefix='/public') 


    
    from . import commands
    commands.register_commands(app) # Registra os comandos CLI

    return app