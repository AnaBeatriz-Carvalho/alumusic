from flask import request, jsonify
from . import api_bp
from app.extensions import db
from app.models.comment import Comentario
from app.models.user import Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Response 
import json
import uuid

@api_bp.route('/comentarios', methods=['POST'])
@jwt_required()
def adicionar_comentarios():
    user_email = get_jwt_identity()
    usuario = db.session.scalar(db.select(Usuario).where(Usuario.email == user_email))
    if not usuario:
        return jsonify({"erro": "Usuário do token não encontrado."}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"erro": "Requisição precisa ser JSON"}), 400

    comentarios_input = [json_data] if isinstance(json_data, dict) else json_data
    
    ids_enfileirados = []
    comentarios_para_salvar = []

    for item in comentarios_input:
        texto = item.get("texto")
        if not texto:
            continue

        novo_comentario = Comentario(
            id=uuid.UUID(item.get("id")) if item.get("id") else uuid.uuid4(),
            texto=texto,
            usuario_id=usuario.id,
            status='PENDENTE'
        )
        # 👆👆👆 FIM DA LINHA-CHAVE 👆👆👆
        
        comentarios_para_salvar.append(novo_comentario)
    
    if not comentarios_para_salvar:
        return jsonify({"erro": "Nenhum comentário válido para processar"}), 400

    db.session.add_all(comentarios_para_salvar)
    db.session.commit()

    from tasks.process_comment import processar_classificacao_task

    for comentario in comentarios_para_salvar:
        processar_classificacao_task.delay(str(comentario.id))
        ids_enfileirados.append(str(comentario.id))

    return jsonify({
        "mensagem": f"{len(ids_enfileirados)} comentários recebidos e enfileirados.",
        "ids_enfileirados": ids_enfileirados
    }), 202

@api_bp.route('/comentarios', methods=['GET'])
@jwt_required()
def listar_comentarios():
    user_email = get_jwt_identity()
    usuario = db.session.scalar(db.select(Usuario).where(Usuario.email == user_email))
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    # Pega os parâmetros da URL, incluindo o novo parâmetro 'format'
    search_query = request.args.get('search', '')
    status_filter = request.args.getlist('status')
    category_filter = request.args.getlist('category')
    export_format = request.args.get('format', None) # 👈 NOVO: Pega o formato

    # ... (sua lógica de query continua a mesma) ...
    query = Comentario.query.order_by(Comentario.data_recebimento.desc())
    if search_query:
        query = query.filter(Comentario.texto.ilike(f'%{search_query}%'))
    if status_filter:
        query = query.filter(Comentario.status.in_(status_filter))
    if category_filter:
        query = query.filter(Comentario.categoria.in_(category_filter))
    comentarios = query.all()

    # Prepara a lista de resultados (serialização)
    resultado = []
    for c in comentarios:
        resultado.append({
            "id": str(c.id), "texto": c.texto, "status": c.status,
            "categoria": c.categoria, "confianca": c.confianca,
            "data_recebimento": c.data_recebimento.isoformat() if c.data_recebimento else None,
            "tags": [{"codigo": t.codigo, "explicacao": t.explicacao} for t in c.tags]
        })
    
    # 👇 NOVO: Lógica para decidir o formato da resposta 👇
    if export_format == 'json':
        # Se o formato for 'json', preparamos uma resposta de download
        return Response(
            json.dumps(resultado, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment;filename=comentarios.json'}
        )
    else:
        # Caso contrário, retorna o JSON normal para o dashboard
        return jsonify({"comentarios": resultado}), 200
    
@api_bp.route('/comentarios/<uuid:comentario_id>', methods=['GET'])
@jwt_required()
def get_comentario_por_id(comentario_id):
    """Retorna os detalhes de um único comentário pelo seu ID."""
    # O UUID já é convertido pela rota do Flas
    comentario = db.session.get(Comentario, comentario_id)
    
    if not comentario:
        return jsonify({"erro": "Comentário não encontrado"}), 404

    # Serializa os dados do comentário específico
    resultado = {
        "id": str(comentario.id),
        "texto": comentario.texto,
        "status": comentario.status,
        "categoria": comentario.categoria,
        "confianca": comentario.confianca,
        "data_recebimento": comentario.data_recebimento.isoformat() if comentario.data_recebimento else None,
        "tags": [{"codigo": t.codigo, "explicacao": t.explicacao} for t in comentario.tags]
    }
    
    return jsonify(resultado), 200