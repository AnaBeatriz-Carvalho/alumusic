from app.models.user import Usuario 
from flask import request, jsonify
from . import api_bp
from app.models.comment import Comentario, TagFuncionalidade
from app.models.music import Musica
from app.extensions import db
from app.core.llm_service import classificar_comentario
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import logging
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Usuario 
from app.tasks import processar_classificacao_task 
from app.models.artists import Artista



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

    texto = json_data.get("texto")
    musica_id = json_data.get("musica_id")
    artista_id = json_data.get("artista_id")

    if not texto:
        return jsonify({"erro": "Texto do comentário é obrigatório."}), 400

    if not musica_id and not artista_id:
        return jsonify({"erro": "O comentário deve ser associado a uma música ou a um artista."}), 400

    if musica_id:
        musica = Musica.query.filter_by(id=musica_id).first()
        if not musica:
            return jsonify({"erro": "Música não encontrada."}), 404

    if artista_id:
        artista = Artista.query.filter_by(id=artista_id).first()
        if not artista:
            return jsonify({"erro": "Artista não encontrado."}), 404

    comentario = Comentario(
        texto=texto,
        usuario_id=usuario_logado.id,
        musica_id=musica_id,
        artista_id=artista_id,
        status='PENDENTE'
    )

    db.session.add(comentario)
    db.session.commit()

    return jsonify({"mensagem": "Comentário criado com sucesso.", "id": str(comentario.id)}), 201

@api_bp.route('/comentarios', methods=['GET'])
@jwt_required()
def listar_comentarios():
    user_email = get_jwt_identity()
    usuario = Usuario.query.filter_by(email=user_email).first()

    if not usuario:
        return jsonify({"erro": "Usuário do token não encontrado."}), 404

    comentarios = Comentario.query.filter_by(usuario_id=usuario.id).all()
    
    comentarios_serializados = []
    for comentario in comentarios:
        comentario_data = {
            "id": str(comentario.id),
            "texto": comentario.texto,
            "status": comentario.status,
            "data_recebimento": comentario.data_recebimento.isoformat() if comentario.data_recebimento else None,
            "associado_a": None
        }
        
        # Verificar se está associado a uma música
        if comentario.musica_id and comentario.musica:
            comentario_data["associado_a"] = f"Música: {comentario.musica.titulo}"
        # Verificar se está associado a um artista
        elif comentario.artista_id and comentario.artista:
            comentario_data["associado_a"] = f"Artista: {comentario.artista.nome}"
        else:
            comentario_data["associado_a"] = "Não especificado"
            
        comentarios_serializados.append(comentario_data)
    
    return jsonify({"comentarios": comentarios_serializados}), 200

# Criar artista
@api_bp.route('/artistas', methods=['POST'])
@jwt_required()
def criar_artista():
    data = request.get_json() or {}
    nome = data.get('nome')
    if not nome:
        return jsonify({"erro": "nome é obrigatório"}), 400
    artista = Artista(nome=nome, slug=data.get('slug'))
    db.session.add(artista)
    db.session.commit()
    return jsonify({"id": str(artista.id), "nome": artista.nome}), 201

# Listar artistas
@api_bp.route('/artistas', methods=['GET'])
def listar_artistas():
    artistas = Artista.query.all()
    return jsonify([{"id": str(a.id), "nome": a.nome, "slug": a.slug} for a in artistas]), 200

# Criar música (associa a artista existente via artist_id)
@api_bp.route('/musicas', methods=['POST'])
@jwt_required()
def criar_musica():
    data = request.get_json() or {}
    titulo = data.get('titulo')
    artista_id = data.get('artista_id')
    if not titulo or not artista_id:
        return jsonify({"erro": "titulo e artista_id são obrigatórios"}), 400
    artista = Artista.query.filter_by(id=artista_id).first()
    if not artista:
        return jsonify({"erro": "artista_id não encontrado"}), 404
    musica = Musica(titulo=titulo, duracao_segundos=data.get('duracao_segundos'), artista_id=artista.id)
    db.session.add(musica)
    db.session.commit()
    return jsonify({"id": str(musica.id), "titulo": musica.titulo, "artista_id": str(artista.id)}), 201

# Listar músicas (opcionalmente filtrar por artista_id)
@api_bp.route('/musicas', methods=['GET'])
def listar_musicas():
    artista_id = request.args.get('artista_id')
    query = Musica.query
    if artista_id:
        query = query.filter_by(artista_id=artista_id)
    musicas = query.all()
    return jsonify([{"id": str(m.id), "titulo": m.titulo, "artista_id": str(m.artista_id)} for m in musicas]), 200

@api_bp.route('/init-data', methods=['POST'])
def init_data():
    """Inicializa dados de exemplo no banco"""
    try:
        from app.scripts.init_data import init_database
        init_database()
        return jsonify({"mensagem": "Dados inicializados com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@api_bp.route('/classificacoes', methods=['GET'])
@jwt_required()
def listar_classificacoes():
    """Lista o histórico de classificações do usuário"""
    user_email = get_jwt_identity()
    usuario = Usuario.query.filter_by(email=user_email).first()

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado."}), 404

    # Buscar comentários do usuário com suas tags
    comentarios = Comentario.query.filter_by(usuario_id=usuario.id).filter(
        Comentario.status != 'PENDENTE'
    ).all()
    
    classificacoes = []
    for comentario in comentarios:
        for tag in comentario.tags:
            classificacao = {
                "id": str(comentario.id),
                "texto": comentario.texto,
                "categoria": comentario.categoria,
                "confianca": comentario.confianca,
                "tag_nome": tag.nome,
                "tag_codigo": tag.codigo,
                "data_processamento": comentario.data_recebimento.isoformat() if comentario.data_recebimento else None,
                "associado_a": None
            }
            
            # Verificar associação
            if comentario.musica_id and comentario.musica:
                classificacao["associado_a"] = f"Música: {comentario.musica.titulo}"
            elif comentario.artista_id and comentario.artista:
                classificacao["associado_a"] = f"Artista: {comentario.artista.nome}"
            else:
                classificacao["associado_a"] = "Não especificado"
                
            classificacoes.append(classificacao)
    
    return jsonify({"classificacoes": classificacoes}), 200

@api_bp.route('/relatorio/semana', methods=['GET'])
def relatorio_semana():
    """Gera relatório da última semana"""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Backend não-interativo
        import matplotlib.pyplot as plt
        import pandas as pd
        from datetime import datetime, timedelta
        import base64
        import io

        # Data de uma semana atrás
        semana_atras = datetime.now() - timedelta(days=7)
        
        # Buscar comentários da última semana
        comentarios = Comentario.query.filter(
            Comentario.data_recebimento >= semana_atras
        ).all()

        if not comentarios:
            return jsonify({
                "graficos": [],
                "mensagem": "Nenhum comentário encontrado na última semana"
            }), 200

        # Preparar dados para gráficos
        dados = []
        for comentario in comentarios:
            dados.append({
                "data": comentario.data_recebimento.date(),
                "categoria": comentario.categoria or "Não classificado",
                "status": comentario.status,
                "confianca": comentario.confianca or 0
            })

        df = pd.DataFrame(dados)
        graficos = []

        # Gráfico 1: Comentários por dia
        plt.figure(figsize=(10, 6))
        comentarios_por_dia = df.groupby('data').size()
        comentarios_por_dia.plot(kind='bar')
        plt.title('Comentários por Dia (Última Semana)')
        plt.xlabel('Data')
        plt.ylabel('Número de Comentários')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graficos.append({
            "titulo": "Comentários por Dia",
            "imagem_base64": base64.b64encode(buffer.getvalue()).decode()
        })
        plt.close()

        # Gráfico 2: Distribuição por categoria
        if 'categoria' in df.columns:
            plt.figure(figsize=(8, 8))
            categorias = df['categoria'].value_counts()
            categorias.plot(kind='pie', autopct='%1.1f%%')
            plt.title('Distribuição por Categoria')
            plt.ylabel('')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graficos.append({
                "titulo": "Distribuição por Categoria",
                "imagem_base64": base64.b64encode(buffer.getvalue()).decode()
            })
            plt.close()

        # Gráfico 3: Status dos comentários
        plt.figure(figsize=(8, 6))
        status_counts = df['status'].value_counts()
        status_counts.plot(kind='bar')
        plt.title('Status dos Comentários')
        plt.xlabel('Status')
        plt.ylabel('Quantidade')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graficos.append({
            "titulo": "Status dos Comentários",
            "imagem_base64": base64.b64encode(buffer.getvalue()).decode()
        })
        plt.close()

        return jsonify({"graficos": graficos}), 200

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        return jsonify({"erro": f"Erro ao gerar relatório: {str(e)}"}), 500