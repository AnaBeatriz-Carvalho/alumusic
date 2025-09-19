import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

class Config:
    """Configurações base, compartilhadas por todos os ambientes."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'uma-chave-secreta-muito-segura')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'uma-chave-jwt-muito-segura')

    # Configuração do Celery (usando as variáveis do .env)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')


class DevelopmentConfig(Config):
    """Configurações para o ambiente de desenvolvimento (usado no Docker)."""
    DEBUG = True
    # Usa a variável DATABASE_URL do seu arquivo .env
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(DevelopmentConfig):
    """Configurações para o ambiente de testes (usado pelo Pytest)."""
    TESTING = True
    # Para testes, podemos usar o mesmo banco de desenvolvimento por enquanto.
    # Em um projeto maior, seria ideal usar um banco de dados separado para testes.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class ProductionConfig(Config):
    """Configurações para o ambiente de produção."""
    DEBUG = False
    # Em produção, você usaria uma variável de ambiente específica para o DB de produção.
    SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCTION_DATABASE_URL')


# Dicionário para facilitar a seleção da configuração
config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig  
)