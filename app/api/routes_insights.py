import io
import base64
import matplotlib.pyplot as plt
from flask import Blueprint, jsonify
from app.models.comment import Comentario, TagFuncionalidade
from app.extensions import db
from datetime import datetime, timedelta

from . import api_bp

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img_base64

@api_bp.route('/relatorio/semana', methods=['GET'])
def relatorio_semanal():
    agora = datetime.utcnow()
    semana_atras = agora - timedelta(days=7)

    # Exemplo 1: Categorias mais frequentes por artista
    dados = db.session.query(
        Comentario.categoria, db.func.count(Comentario.id)
    ).filter(
        Comentario.data_recebimento >= semana_atras
    ).group_by(
        Comentario.categoria
    ).all()

    categorias = [d[0] for d in dados]
    counts = [d[1] for d in dados]

    fig1, ax1 = plt.subplots()
    ax1.bar(categorias, counts)
    ax1.set_title("Categorias mais frequentes")
    img1 = fig_to_base64(fig1)

    # Exemplo 2: Evolução de críticas após lançamento
    # (Ajuste conforme seu modelo)
    evolucao = db.session.query(
        db.func.date_trunc('day', Comentario.data_recebimento),
        db.func.count(Comentario.id)
    ).filter(
        Comentario.data_recebimento >= semana_atras
    ).group_by(
        db.func.date_trunc('day', Comentario.data_recebimento)
    ).order_by(
        db.func.date_trunc('day', Comentario.data_recebimento)
    ).all()

    datas = [str(d[0].date()) for d in evolucao]
    counts_evolucao = [d[1] for d in evolucao]

    fig2, ax2 = plt.subplots()
    ax2.plot(datas, counts_evolucao)
    ax2.set_title("Evolução de críticas após lançamento")
    img2 = fig_to_base64(fig2)

    # Exemplo 3: Tags mais citadas nas últimas 48h
    dois_dias = agora - timedelta(hours=48)
    tags = db.session.query(
        TagFuncionalidade.codigo, db.func.count(TagFuncionalidade.id)
    ).join(Comentario).filter(
        Comentario.data_recebimento >= dois_dias
    ).group_by(
        TagFuncionalidade.codigo
    ).order_by(
        db.func.count(TagFuncionalidade.id).desc()
    ).limit(10).all()

    tag_nomes = [t[0] for t in tags]
    tag_counts = [t[1] for t in tags]

    fig3, ax3 = plt.subplots()
    ax3.bar(tag_nomes, tag_counts)
    ax3.set_title("Tags mais citadas nas últimas 48h")
    img3 = fig_to_base64(fig3)

    # Exemplo 4: Distribuição de status dos comentários
    status_data = db.session.query(
        Comentario.status, db.func.count(Comentario.id)
    ).filter(
        Comentario.data_recebimento >= semana_atras
    ).group_by(
        Comentario.status
    ).all()

    status_labels = [s[0] for s in status_data]
    status_counts = [s[1] for s in status_data]

    fig4, ax4 = plt.subplots()
    ax4.pie(status_counts, labels=status_labels, autopct='%1.1f%%')
    ax4.set_title("Distribuição de status dos comentários")
    img4 = fig_to_base64(fig4)

    # Exemplo 5: Comentários por dia na semana
    dias_data = db.session.query(
        db.func.date_trunc('day', Comentario.data_recebimento),
        db.func.count(Comentario.id)
    ).filter(
        Comentario.data_recebimento >= semana_atras
    ).group_by(
        db.func.date_trunc('day', Comentario.data_recebimento)
    ).order_by(
        db.func.date_trunc('day', Comentario.data_recebimento)
    ).all()

    dias = [str(d[0].date()) for d in dias_data]
    dias_counts = [d[1] for d in dias_data]

    fig5, ax5 = plt.subplots()
    ax5.bar(dias, dias_counts)
    ax5.set_title("Comentários por dia na semana")
    img5 = fig_to_base64(fig5)

    return jsonify({
        "graficos": [
            {"titulo": "Categorias mais frequentes", "imagem_base64": img1},
            {"titulo": "Evolução de críticas após lançamento", "imagem_base64": img2},
            {"titulo": "Tags mais citadas nas últimas 48h", "imagem_base64": img3},
            {"titulo": "Distribuição de status dos comentários", "imagem_base64": img4},
            {"titulo": "Comentários por dia na semana", "imagem_base64": img5},
        ],
        "dados": {
            "categorias_por_artista": dict(zip(categorias, counts)),
            "evolucao_criticas": dict(zip(datas, counts_evolucao)),
            "tags_mais_citadas": dict(zip(tag_nomes, tag_counts)),
        }
    })


@api_bp.route('/insights/perguntar', methods=['POST'])
# @jwt_required()
def perguntar_insight():
    # TODO: Implementar a lógica do Q&A opcional.
    return jsonify({"mensagem": "Funcionalidade de Q&A em desenvolvimento."})