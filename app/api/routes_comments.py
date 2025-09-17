from flask import request, jsonify
from . import api_bp
from app.models.comment import Comentario, TagFuncionalidade
from app.extensions import db
from app.core.llm_service import classificar_comentario
from flask_jwt_extended import jwt_required

@api_bp.route('/comentarios', methods=['POST'])
# @jwt_required()
def adicionar_comentarios():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"erro": "Requisição precisa ser JSON"}), 400

    if isinstance(json_data, dict):
        comentarios_input = [json_data]
    elif isinstance(json_data, list):
        comentarios_input = json_data
    else:
        return jsonify({"erro": "Formato inválido"}), 400

    ids_enfileirados = []

    for comentario_data in comentarios_input:
        texto = comentario_data.get('texto')
        if not texto:
            continue

        # 1️⃣ cria o comentário no banco
        comentario = Comentario(texto=texto)
        db.session.add(comentario)
        db.session.commit()  # necessário para gerar o id

        # 2️⃣ classifica usando Gemini
        resultado = classificar_comentario(texto)
        comentario.categoria = resultado.get("categoria")
        comentario.confianca = resultado.get("confianca")
        db.session.commit()

        # 3️⃣ salva tags
        for tag in resultado.get("tags_funcionalidades", []):
            nova_tag = TagFuncionalidade(
                comentario_id=comentario.id,
                codigo=tag.get("codigo"),
                explicacao=tag.get("explicacao")
            )
            db.session.add(nova_tag)
        db.session.commit()

        ids_enfileirados.append(comentario.id)

    if not ids_enfileirados:
        return jsonify({"erro": "Nenhum comentário válido"}), 400

    return jsonify({
        "mensagem": f"{len(ids_enfileirados)} comentários processados.",
        "ids_enfileirados": ids_enfileirados
    }), 202
