from flask import Blueprint

# Cria o objeto Blueprint
public_bp = Blueprint('public', __name__)

# Importa as rotas para registrá-las no blueprint
from . import routes