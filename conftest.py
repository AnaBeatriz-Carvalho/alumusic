import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='session')
def app():
    """
    Cria e configura uma nova instância da aplicação para a sessão de testes.
    Esta fixture é descoberta automaticamente pelo Pytest.
    """
    # Usa a configuração de 'testing' que definimos em config.py
    app = create_app(config_name='testing')
    
    # 'yield' disponibiliza a instância da aplicação para os testes que a solicitarem.
    yield app