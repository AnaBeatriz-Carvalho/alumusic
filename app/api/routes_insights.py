# app/api/routes_insights.py

from flask import jsonify
from . import api_bp
# from flask_jwt_extended import jwt_required

@api_bp.route('/relatorio/semana', methods=['GET'])
def relatorio_semanal():
    # TODO: Implementar a lógica para buscar dados do banco,
    # agregar e retornar os 5 gráficos/JSONs.
    # Lembre-se de usar cache aqui!
    return jsonify({"mensagem": "Relatório semanal em desenvolvimento."})


@api_bp.route('/insights/perguntar', methods=['POST'])
# @jwt_required()
def perguntar_insight():
    # TODO: Implementar a lógica do Q&A opcional.
    return jsonify({"mensagem": "Funcionalidade de Q&A em desenvolvimento."})