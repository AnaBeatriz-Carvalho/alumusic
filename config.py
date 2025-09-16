import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

class Config:
    """Configurações base, compartilhadas por todos os ambientes."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'uma-chave-secreta-muito-segura')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'uma-chave-jwt-muito-segura')

    # Configuração do Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')


class ProductionConfig(Config):
    """Configurações para o ambiente de produção."""
    DEBUG = False
    # config.py (dentro da classe DevelopmentConfig)

    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'postgresql://user:alumusic@localhost/alumusic')


# Dicionário para facilitar a seleção da configuração
config_by_name = {

    'default': ProductionConfig
}