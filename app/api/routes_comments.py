# app/api/routes_comments.py

from flask import request, jsonify
from . import api_bp
from app.tasks import processar_comentario_task
# from flask_jwt_extended import jwt_required # Descomente quando a autenticação de usuário estiver pronta

@api_bp.route('/comentarios', methods=['POST'])
# @jwt_required() # Protege a rota
def adicionar_comentarios():
    """
    Endpoint para receber comentários individualmente ou em lote.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"erro": "Requisição precisa ser JSON"}), 400

    # Lógica para aceitar tanto um objeto único quanto uma lista
    if isinstance(json_data, dict):
         comentarios = [json_data]
    elif isinstance(json_data, list):
         comentarios = json_data
    else:
        return jsonify({"erro": "Formato de entrada inválido. Envie um objeto ou uma lista de objetos."}), 400


    ids_enfileirados = []
    for comentario in comentarios:
        comentario_id = comentario.get('id')
        texto = comentario.get('texto')

        if not comentario_id or not texto:
            # Pular item inválido ou retornar erro
            continue 

        # Envia a tarefa para o Celery processar em segundo plano
        processar_comentario_task.delay(comentario_id, texto)
        ids_enfileirados.append(comentario_id)

    return jsonify({
        "mensagem": f"{len(ids_enfileirados)} comentários recebidos e enfileirados para processamento.",
        "ids_enfileirados": ids_enfileirados
    }), 202 # 202 Accepted: A requisição foi aceita e será processada.