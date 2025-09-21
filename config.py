import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

class Config:
    # Configurações comuns a todos os ambientes
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta-muito-segura')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'chave-jwt-muito-segura')

    # Configuração do Celery usando as variáveis do .env
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')


class DevelopmentConfig(Config):
    # Configurações para o ambiente de desenvolvimento usado no Docker
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(DevelopmentConfig):
    # Configurações para o ambiente de testes usado pelo Pytest
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    default=DevelopmentConfig  
)