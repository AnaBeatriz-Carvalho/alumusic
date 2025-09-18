# app/__init__.py

from flask import Flask
from config import config_by_name
from .extensions import db, migrate, jwt, celery
from app.models.comment import Comentario, TagFuncionalidade
from app.models.tag_catalog import TagCatalogo
from app.models.artists import Artista
from app.models.music import Musica

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

    # Adicionar rota de saúde
    @app.route('/health')
    def health():
        return {"status": "ok", "message": "API funcionando"}, 200

    # Inicializar dados automaticamente após criar as tabelas
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            
            # Inicializar dados básicos automaticamente
            from app.scripts.init_data import init_database
            init_database()
        except Exception as e:
            app.logger.error(f"Erro na inicialização automática: {e}")

    return app