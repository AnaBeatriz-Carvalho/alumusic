# app/api/__init__.py

from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Importa as rotas para que sejam registradas no Blueprint
from . import routes_comments, routes_insights  