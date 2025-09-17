from flask import request, jsonify
from . import api_bp
from app.models.comment import Comentario, TagFuncionalidade
from app.extensions import db
from app.core.llm_service import classificar_comentario
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/comentarios', methods=['POST'])
@jwt_required()
def adicionar_comentarios():
    usuario_id = get_jwt_identity()  # pega o UUID do usuário logado
    logger.debug(f"Usuário logado (UUID): {usuario_id}")

    json_data = request.get_json()
    logger.debug(f"JSON recebido: {json_data}")

    if not json_data:
        logger.error("Nenhum JSON enviado")
        return jsonify({"erro": "Requisição precisa ser JSON"}), 400

    comentarios_input = [json_data] if isinstance(json_data, dict) else json_data if isinstance(json_data, list) else None
    if comentarios_input is None:
        logger.error("Formato inválido de JSON")
        return jsonify({"erro": "Formato inválido"}), 400

    ids_enfileirados = []

    for comentario_data in comentarios_input:
        texto = comentario_data.get("texto")
        if not texto:
            continue

        comentario = Comentario(
            id=str(uuid.uuid4()),
            texto=texto,
            usuario_id=usuario_id
        )
        db.session.add(comentario)
        try:
            db.session.commit()
            logger.debug(f"Comentário salvo: {comentario.id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao salvar comentário: {e}")
            return jsonify({"erro": "Falha ao salvar comentário"}), 500

        resultado = classificar_comentario(texto)
        comentario.categoria = resultado.get("categoria")
        comentario.confianca = resultado.get("confianca")
        db.session.commit()

        for tag in resultado.get("tags_funcionalidades", []):
            nova_tag = TagFuncionalidade(
                comentario_id=comentario.id,
                codigo=tag.get("codigo"),
                explicacao=tag.get("explicacao")
            )
            db.session.add(nova_tag)
        db.session.commit()

        ids_enfileirados.append(comentario.id)

    return jsonify({
        "mensagem": f"{len(ids_enfileirados)} comentários processados.",
        "ids_enfileirados": ids_enfileirados,
    }), 202
