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

    # 1. Categorias mais frequentes por artista
    dados_cat_artista = db.session.query(
        Comentario.categoria,
        Comentario.artista_id,
        db.func.count(Comentario.id)
    ).filter(
        Comentario.data_recebimento >= semana_atras,
        Comentario.categoria.isnot(None)
    ).group_by(
        Comentario.categoria, Comentario.artista_id
    ).all()

    categorias = [d[0] for d in dados_cat_artista]
    artistas_ids = [d[1] for d in dados_cat_artista]
    counts = [d[2] for d in dados_cat_artista]

    fig1, ax1 = plt.subplots()
    ax1.barh(range(len(counts)), counts)
    ax1.set_yticks(range(len(counts)))
    ax1.set_yticklabels([f"{c} - {a}" for c, a in zip(categorias, artistas_ids)])
    ax1.set_title("Categorias mais frequentes por artista")
    ax1.set_xlabel("Contagem")
    img1 = fig_to_base64(fig1)

    # 2. Evolução de comentários na semana
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
    ax2.plot(datas, counts_evolucao, marker='o')
    ax2.set_title("Evolução de comentários (últimos 7 dias)")
    ax2.set_xlabel("Data")
    ax2.set_ylabel("Qtde de Comentários")
    plt.xticks(rotation=45)
    img2 = fig_to_base64(fig2)

    # 3. Tags mais citadas nas últimas 48h
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
    ax3.barh(tag_nomes, tag_counts)
    ax3.set_title("Tags mais citadas (últimas 48h)")
    ax3.set_xlabel("Frequência")
    img3 = fig_to_base64(fig3)

    # 4. Distribuição de status dos comentários
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

    # 5. Top 5 artistas/músicas mais comentados
    top_musicas = db.session.query(
        Comentario.musica_id, db.func.count(Comentario.id)
    ).filter(
        Comentario.data_recebimento >= semana_atras
    ).group_by(
        Comentario.musica_id
    ).order_by(
        db.func.count(Comentario.id).desc()
    ).limit(5).all()

    musicas_ids = [str(t[0]) for t in top_musicas]
    musicas_counts = [t[1] for t in top_musicas]

    fig5, ax5 = plt.subplots()
    ax5.bar(musicas_ids, musicas_counts)
    ax5.set_title("Top 5 músicas mais comentadas (semana)")
    ax5.set_xlabel("Música ID")
    ax5.set_ylabel("Qtde de Comentários")
    img5 = fig_to_base64(fig5)

    return jsonify({
        "graficos": [
            {"titulo": "Categorias mais frequentes por artista", "imagem_base64": img1},
            {"titulo": "Evolução de comentários (últimos 7 dias)", "imagem_base64": img2},
            {"titulo": "Tags mais citadas (48h)", "imagem_base64": img3},
            {"titulo": "Distribuição de status", "imagem_base64": img4},
            {"titulo": "Top 5 músicas mais comentadas", "imagem_base64": img5},
        ],
        "dados": {
            "categorias_por_artista": dict(zip(categorias, counts)),
            "evolucao_comentarios": dict(zip(datas, counts_evolucao)),
            "tags_mais_citadas": dict(zip(tag_nomes, tag_counts)),
            "status": dict(zip(status_labels, status_counts)),
            "top_musicas": dict(zip(musicas_ids, musicas_counts))
        }
    })


@api_bp.route('/insights/perguntar', methods=['POST'])
# @jwt_required()
def perguntar_insight():
    # TODO: Implementar a lógica do Q&A opcional.
    return jsonify({"mensagem": "Funcionalidade de Q&A em desenvolvimento."})