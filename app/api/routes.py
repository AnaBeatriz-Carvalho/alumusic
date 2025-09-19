from flask import request, jsonify
from . import api_bp
from app.extensions import db
from app.models.comment import Comentario
from app.models.user import Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import celery
from flask import Response 
import json
import uuid
from werkzeug.utils import secure_filename
import csv
import json

@api_bp.route('/llm/analyze', methods=['POST'])
@jwt_required()
def llm_analyze():
    """Recebe um arquivo CSV ou JSON (multipart/form-data) ou texto bruto e retorna
    a análise do LLM para cada texto encontrado.
    Campo esperado no form-data: 'file' (opcional), ou 'text' (opcional).
    """
    # Permite que o usuário envie um arquivo CSV/JSON ou um campo de texto
    textos = []
    if 'file' in request.files:
        f = request.files['file']
        filename = secure_filename(f.filename)
        content_type = f.content_type or ''

        try:
            if filename.endswith('.csv') or 'csv' in content_type:
                # Parse CSV assumindo uma coluna chamada 'texto' ou primeira coluna
                decoded = f.read().decode('utf-8')
                reader = csv.DictReader(decoded.splitlines())
                for row in reader:
                    if 'texto' in row:
                        textos.append(row['texto'])
                    else:
                        textos.append(list(row.values())[0])
            else:
                # assume JSON array ou objeto JSON único
                payload = json.load(f)
                if isinstance(payload, list):
                    textos = [item.get('texto') if isinstance(item, dict) else str(item) for item in payload]
                elif isinstance(payload, dict):
                    if 'texto' in payload:
                        textos = [payload['texto']]
                    else:
                        textos = [json.dumps(payload, ensure_ascii=False)]
                else:
                    textos = [str(payload)]
        except Exception as e:
            return jsonify({'erro': 'Falha ao processar o arquivo enviado', 'detail': str(e)}), 400

    elif request.form.get('text'):
        textos = [request.form.get('text')]
    else:
        return jsonify({'erro': 'Envie um arquivo (file) ou um campo de texto (text).'}), 400

    # Validações de tamanho e quantidade
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
    MAX_TEXTS = 500

    # Rejeita payloads muito grandes
    if 'file' in request.files:
        try:
            request.files['file'].stream.seek(0, 2)
            size = request.files['file'].stream.tell()
            request.files['file'].stream.seek(0)
            if size > MAX_FILE_SIZE:
                return jsonify({'erro': 'Arquivo muito grande (máx 2MB).'}), 413
        except Exception:
            # Se não for possível medir, continue e confie nas outras validações
            pass

    textos = [t for t in textos if t]
    if len(textos) == 0:
        return jsonify({'erro': 'Nenhum texto válido para processar.'}), 400
    if len(textos) > MAX_TEXTS:
        return jsonify({'erro': f'Muitos itens no arquivo (máx {MAX_TEXTS}).'}), 413

    # Persiste cada texto como um Comentario e enfileira a task já existente
    user_email = get_jwt_identity()
    usuario = db.session.scalar(db.select(Usuario).where(Usuario.email == user_email))
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado."}), 404

    comentarios_para_salvar = []
    ids_enfileirados = []
    for t in textos:
        novo_comentario = Comentario(
            id=uuid.uuid4(),
            texto=t,
            usuario_id=usuario.id,
            status='PENDENTE'
        )
        comentarios_para_salvar.append(novo_comentario)

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


@api_bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """Retorna o status e resultado (se disponível) de uma task Celery.
    """
    async_res = celery.AsyncResult(task_id)
    status = async_res.status
    result = None
    try:
        if async_res.ready():
            result = async_res.result
    except Exception:
        # Se houver problema ao acessar o resultado, retorne status atual
        result = None

    return jsonify({
        'task_id': task_id,
        'status': status,
        'result': result
    }), 200

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

    search_query = request.args.get('search', '')
    status_filter = request.args.getlist('status')
    category_filter = request.args.getlist('category')
    export_format = request.args.get('format', None)

    query = Comentario.query.order_by(Comentario.data_recebimento.desc())
    if search_query:
        query = query.filter(Comentario.texto.ilike(f'%{search_query}%'))
    if status_filter:
        query = query.filter(Comentario.status.in_(status_filter))
    if category_filter:
        query = query.filter(Comentario.categoria.in_(category_filter))
    comentarios = query.all()

    # Lista dos resultados serializados
    resultado = []
    for c in comentarios:
        resultado.append({
            "id": str(c.id), "texto": c.texto, "status": c.status,
            "categoria": c.categoria, "confianca": c.confianca,
            "data_recebimento": c.data_recebimento.isoformat() if c.data_recebimento else None,
            "tags": [{"codigo": t.codigo, "explicacao": t.explicacao} for t in c.tags]
        })
    
    
    if export_format == 'json':
        # Se o formato de exportação for JSON, retorna como um arquivo para download
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