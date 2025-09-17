# No início do seu arquivo, certifique-se de importar o modelo Usuario
from app.models.user import Usuario 
# (confirme o caminho correto para o seu modelo de usuário)
from flask import request, jsonify
from . import api_bp
from app.models.comment import Comentario, TagFuncionalidade
from app.extensions import db
from app.core.llm_service import classificar_comentario
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import logging
from sqlalchemy.dialects.postgresql import UUID

# No início do seu arquivo, confirme estes imports
import uuid
import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api_bp
from app.extensions import db
from app.models.user import Usuario 
from app.models.comment import Comentario
# 👇 Importe a sua tarefa Celery
from app.tasks import processar_classificacao_task 

logger = logging.getLogger(__name__)

@api_bp.route('/comentarios', methods=['POST'])
@jwt_required()
def adicionar_comentarios():
    """
    Recebe um lote de comentários, salva-os rapidamente no banco com status 'PENDENTE'
    e enfileira uma tarefa em background para cada um ser processado pelo LLM.
    """
    # 1. Valida o usuário do token
    user_identity_email = get_jwt_identity()
    usuario_logado = db.session.query(Usuario).filter_by(email=user_identity_email).first()
    if not usuario_logado:
        logger.warning(f"Usuário do token não encontrado: {user_identity_email}")
        return jsonify({"erro": "Usuário do token não é válido."}), 404
    
    # 2. Valida o corpo da requisição
    json_data = request.get_json()
    if not json_data:
        return jsonify({"erro": "Requisição precisa ser JSON"}), 400

    comentarios_input = [json_data] if isinstance(json_data, dict) else json_data if isinstance(json_data, list) else None
    if comentarios_input is None:
        return jsonify({"erro": "Formato inválido. Envie um objeto ou uma lista de objetos."}), 400

    comentarios_para_salvar = []

    # 3. Prepara os objetos Comentario para serem salvos
    for comentario_data in comentarios_input:
        texto = comentario_data.get("texto")
        if not texto: 
            continue

        # CRIANDO o comentário com status PENDENTE. Nenhum LLM é chamado aqui!
        novo_comentario = Comentario(
            texto=texto,
            usuario_id=usuario_logado.id,
            status='PENDENTE'
        )
        comentarios_para_salvar.append(novo_comentario)
    
    if not comentarios_para_salvar:
        return jsonify({"erro": "Nenhum comentário válido para processar"}), 400

    # 4. Salva todos os comentários no banco de dados de uma vez (operação rápida)
    try:
        db.session.add_all(comentarios_para_salvar)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar lote inicial de comentários: {e}")
        return jsonify({"erro": "Falha ao persistir comentários no banco"}), 500

    # 5. Agora que estão salvos, enfileira a tarefa de processamento para cada um
    ids_enfileirados = []
    from app.tasks import processar_classificacao_task  # <-- Importa aqui, dentro da função
    for comentario in comentarios_para_salvar:
        processar_classificacao_task.delay(comentario.id)
        ids_enfileirados.append(comentario.id)
    
    logger.info(f"{len(ids_enfileirados)} comentários foram enfileirados para processamento.")

    # 6. Retorna uma resposta imediata para o cliente
    return jsonify({
        "mensagem": "Comentários recebidos e enfileirados para processamento em segundo plano.",
        "ids_enfileirados": ids_enfileirados,
    }), 202 # 202 Accepted: A requisição foi aceita, mas o processamento não terminou.

id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)