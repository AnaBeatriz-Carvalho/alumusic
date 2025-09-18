# app/api/__init__.py

from flask import Blueprint

# 1. CRIE o Blueprint aqui, neste arquivo.
api_bp = Blueprint('api', __name__)

# 2. IMPORTE as rotas DEPOIS da criação do blueprint.
#    Isso faz com que o código em routes.py seja executado,
#    e as rotas (@api_bp.route) sejam registradas no objeto 'api_bp'.
from . import routes