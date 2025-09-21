from flask import request, jsonify, Response
from . import api_bp
from app.extensions import db, celery
from app.models.comment import Comentario
from app.models.user import Usuario
from app.models.summary import WeeklySummary
from app.models.stakeholder import Stakeholder
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import json
import csv
from werkzeug.utils import secure_filename

# Rota para análise de texto via LLM (envio de arquivo ou texto bruto)
@api_bp.route('/llm/analyze', methods=['POST'])
@jwt_required()
def llm_analyze():
    """Recebe um arquivo CSV/JSON ou texto bruto e enfileira para análise."""
    textos = []
    if 'file' in request.files and request.files['file'].filename != '':
        f = request.files['file']
        filename = secure_filename(f.filename)
        try:
            if filename.endswith('.csv'):
                decoded = f.read().decode('utf-8')
                reader = csv.DictReader(decoded.splitlines())
                for row in reader:
                    textos.append(row.get('texto') or list(row.values())[0])
            elif filename.endswith('.json'):
                payload = json.load(f)
                if isinstance(payload, list):
                    textos = [item.get('texto') if isinstance(item, dict) else str(item) for item in payload]
                elif isinstance(payload, dict) and 'texto' in payload:
                    textos = [payload['texto']]
            else:
                return jsonify({'erro': 'Formato de arquivo não suportado. Use .csv ou .json.'}), 400
        except Exception as e:
            return jsonify({'erro': 'Falha ao processar o ficheiro enviado', 'detail': str(e)}), 400
    elif request.form.get('text'):
        textos = [request.form.get('text')]
    else:
        return jsonify({'erro': 'Envie um ficheiro no campo "file" ou um texto no campo "text".'}), 400

    textos = [t for t in textos if t and t.strip()]
    if not textos:
        return jsonify({'erro': 'Nenhum texto válido para processar.'}), 400

    from tasks.process_comment import processar_classificacao_task
    user_email = get_jwt_identity()
    usuario = db.session.scalar(db.select(Usuario).where(Usuario.email == user_email))
    if not usuario:
        return jsonify({"erro": "Utilizador não encontrado."}), 404

    ids_enfileirados = []
    for t in textos:
        novo_comentario = Comentario(texto=t, usuario_id=usuario.id, status='PENDENTE')
        db.session.add(novo_comentario)
        db.session.commit()
        processar_classificacao_task.delay(str(novo_comentario.id))
        ids_enfileirados.append(str(novo_comentario.id))

    return jsonify({
        "mensagem": f"{len(ids_enfileirados)} comentários recebidos e enfileirados.",
        "ids_enfileirados": ids_enfileirados
    }), 202

# Rota para adicionar comentários via JSON (único ou lista)
@api_bp.route('/comentarios', methods=['POST'])
@jwt_required()
def adicionar_comentarios():
    from tasks.process_comment import processar_classificacao_task
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
        if not texto: continue
        novo_comentario = Comentario(
            id=uuid.UUID(item.get("id")) if item.get("id") else uuid.uuid4(),
            texto=texto,
            usuario_id=usuario.id,
            status='PENDENTE'
        )
        comentarios_para_salvar.append(novo_comentario)
    if not comentarios_para_salvar:
        return jsonify({"erro": "Nenhum comentário válido para processar"}), 400
    db.session.add_all(comentarios_para_salvar)
    db.session.commit()
    for comentario in comentarios_para_salvar:
        processar_classificacao_task.delay(str(comentario.id))
        ids_enfileirados.append(str(comentario.id))
    return jsonify({
        "mensagem": f"{len(ids_enfileirados)} comentários recebidos e enfileirados.",
        "ids_enfileirados": ids_enfileirados
    }), 202

# Rota de listagem de comentários com filtros e opção de exportação
@api_bp.route('/comentarios', methods=['GET'])
@jwt_required()
def listar_comentarios():
    search_query = request.args.get('search', '')
    status_filter = request.args.getlist('status')
    category_filter = request.args.getlist('category')
    export_format = request.args.get('format', None)
    
    query = Comentario.query.order_by(Comentario.data_recebimento.desc())
    if search_query: query = query.filter(Comentario.texto.ilike(f'%{search_query}%'))
    if status_filter: query = query.filter(Comentario.status.in_(status_filter))
    if category_filter: query = query.filter(Comentario.categoria.in_(category_filter))
    comentarios = query.all()

    resultado = [{
        "id": str(c.id), "texto": c.texto, "status": c.status,
        "categoria": c.categoria, "confianca": c.confianca,
        "data_recebimento": c.data_recebimento.isoformat() if c.data_recebimento else None,
        "tags": [{"codigo": t.codigo, "explicacao": t.explicacao} for t in c.tags]
    } for c in comentarios]
    
    if export_format == 'json':
        return Response(
            json.dumps(resultado, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment;filename=comentarios.json'}
        )
    else:
        return jsonify({"comentarios": resultado}), 200
    
# Rota de consulta de comentário por ID
@api_bp.route('/comentarios/<uuid:comentario_id>', methods=['GET'])
@jwt_required()
def get_comentario_por_id(comentario_id):
    comentario = db.session.get(Comentario, comentario_id)
    if not comentario:
        return jsonify({"erro": "Comentário não encontrado"}), 404
    resultado = {
        "id": str(comentario.id), "texto": comentario.texto, "status": comentario.status,
        "categoria": comentario.categoria, "confianca": comentario.confianca,
        "data_recebimento": comentario.data_recebimento.isoformat() if c.data_recebimento else None,
        "tags": [{"codigo": t.codigo, "explicacao": t.explicacao} for t in comentario.tags]
    }
    return jsonify(resultado), 200

# Rota para fazer perguntas sobre os resumos semanais
@api_bp.route('/insights/perguntar', methods=['POST'])
@jwt_required()
def ask_insight_question():
    data = request.get_json()
    question = data.get("pergunta")
    if not question:
        return jsonify({"erro": "A pergunta é obrigatória."}), 400

    recent_summaries = db.session.query(WeeklySummary).order_by(WeeklySummary.created_at.desc()).limit(3).all()
    if not recent_summaries:
        return jsonify({"erro": "Não há resumos semanais suficientes para responder."}), 404

    from app.core.llm_service import answer_question_with_context
    context = "\n\n".join([f"**Resumo da Semana {s.start_date.strftime('%Y-W%U')}**:\n{s.summary_text}" for s in recent_summaries])
    source_weeks = [s.start_date.strftime('%Y-W%U') for s in recent_summaries]
    generated_text = answer_question_with_context(question, context)

    return jsonify({
        "texto_gerado": generated_text,
        "semanas_citadas": source_weeks
    }), 200

# Endpoint para gerenciar stakeholders 
@api_bp.route('/stakeholders', methods=['GET'])
@jwt_required()
def get_stakeholders():
    stakeholders = db.session.query(Stakeholder).all()
    return jsonify([{"id": str(s.id), "email": s.email} for s in stakeholders])

@api_bp.route('/stakeholders', methods=['POST'])
@jwt_required()
def add_stakeholder():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"erro": "Email é obrigatório."}), 400
    
    existing = db.session.query(Stakeholder).filter_by(email=email).first()
    if existing:
        return jsonify({"erro": "Este e-mail já está cadastrado."}), 409

    new_stakeholder = Stakeholder(email=email)
    db.session.add(new_stakeholder)
    db.session.commit()
    return jsonify({"id": str(new_stakeholder.id), "email": new_stakeholder.email}), 201

@api_bp.route('/stakeholders/<uuid:stakeholder_id>', methods=['DELETE'])
@jwt_required()
def delete_stakeholder(stakeholder_id):
    stakeholder = db.session.get(Stakeholder, stakeholder_id)
    if not stakeholder:
        return jsonify({"erro": "Stakeholder não encontrado."}), 404
    
    db.session.delete(stakeholder)
    db.session.commit()
    return '', 204

