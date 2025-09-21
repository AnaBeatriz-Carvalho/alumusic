import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='session')
def app():
# Configura e retorna uma instância da aplicação Flask para testes.
    app = create_app(config_name='testing')
    app.config['CELERY'] = {
        'task_always_eager': True,
        'task_eager_propagates': True,
    }

    yield app