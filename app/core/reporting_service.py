import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io
import base64
from app.extensions import db
from sqlalchemy import text
import numpy as np 

def generate_charts():
    
    charts = [] # Lista para armazenar todos os gráficos gerados
    
    # Executa as funções de geração de cada gráfico
    charts.append(generate_category_distribution_chart()) # Gráfico 1 
    charts.append(generate_daily_volume_chart()) # Gráfico 2
    charts.append(generate_top_tags_chart()) # Gráfico 3
    charts.append(generate_sentiment_confidence_scatter()) # Gráfico 4
    charts.append(generate_sentiment_ratio_chart()) # Gráfico 5
    charts.append(generate_avg_confidence_chart()) # Gráfico 6
    
    # Filtra quaisquer resultados None
    return [chart for chart in charts if chart is not None]

def fig_to_base64(fig):
    # Converte uma figura Matplotlib para uma string base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_category_distribution_chart():
    # GRÁFICO 1: Distribuição de Comentários por Categoria
    query = text("SELECT categoria, COUNT(id) as total FROM comentarios WHERE status = 'CONCLUIDO' AND categoria IS NOT NULL GROUP BY categoria ORDER BY total DESC")
    df = pd.read_sql_query(query, db.engine)
    if df.empty: return None
    fig, ax = plt.subplots(figsize=(8, 5))
    df.plot(kind='bar', x='categoria', y='total', ax=ax, legend=False, color='skyblue')
    ax.set_title('Distribuição de Comentários por Categoria')
    ax.set_ylabel('Quantidade')
    ax.set_xlabel('')
    plt.xticks(rotation=0)
    plt.tight_layout()
    return {"titulo": "Visão Geral das Categorias", "imagem_base64": fig_to_base64(fig)}

def generate_daily_volume_chart():
    # GRÁFICO 2: Evolução do volume de comentários nos últimos 14 dias.
    query = text("""SELECT DATE(data_recebimento) as dia, COUNT(id) as total FROM comentarios WHERE status = 'CONCLUIDO' AND data_recebimento >= current_date - interval '14 days' GROUP BY dia ORDER BY dia;""")
    df = pd.read_sql_query(query, db.engine)
    if df.empty: return None
    fig, ax = plt.subplots(figsize=(10, 5))
    df.plot(kind='line', x='dia', y='total', ax=ax, legend=False, marker='o', color='mediumseagreen')
    ax.set_title('Volume de Comentários Recebidos (Últimos 14 Dias)')
    ax.set_ylabel('Quantidade de Comentários')
    ax.set_xlabel('Data')
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return {"titulo": "Evolução do Volume de Feedback", "imagem_base64": fig_to_base64(fig)}

def generate_top_tags_chart():
    # GRÁFICO 3: Tags mais citadas nas últimas 48 horas.
    query = text("""SELECT t.codigo, COUNT(t.id) as total FROM tags_funcionalidades t JOIN comentarios c ON t.comentario_id = c.id WHERE c.data_recebimento >= NOW() - INTERVAL '48 hours' GROUP BY t.codigo ORDER BY total DESC LIMIT 7;""")
    df = pd.read_sql_query(query, db.engine)
    if df.empty: return None
    fig, ax = plt.subplots(figsize=(10, 6))
    df.sort_values('total').plot(kind='barh', x='codigo', y='total', ax=ax, legend=False, color='coral')
    ax.set_title('Tópicos Mais Comentados (Últimas 48 Horas)')
    ax.set_xlabel('Quantidade de Menções')
    ax.set_ylabel('Tag')
    plt.tight_layout()
    return {"titulo": "Hot Topics das Últimas 48h", "imagem_base64": fig_to_base64(fig)}

def generate_sentiment_confidence_scatter():
    # GRÁFICO 4 (Aprimorado): Relação Categoria vs. Confiança com Jitter.
    query = text("SELECT categoria, confianca FROM comentarios WHERE status = 'CONCLUIDO' AND categoria IN ('ELOGIO', 'CRÍTICA')")
    df = pd.read_sql_query(query, db.engine)
    if df.empty or len(df) < 2: return None
    jitter_strength = 0.2
    x_jitter = np.random.normal(0, jitter_strength, size=len(df))
    colors = df['categoria'].map({'ELOGIO': 'seagreen', 'CRÍTICA': 'crimson'})
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.scatter(pd.factorize(df['categoria'])[0] + x_jitter, df['confianca'], c=colors, alpha=0.6, s=50)
    ax.set_title('Distribuição da Confiança da IA por Categoria de Sentimento', fontsize=16)
    ax.set_ylabel('Nível de Confiança', fontsize=12)
    ax.set_xlabel('Categoria', fontsize=12)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Elogio', 'Crítica'], fontsize=12)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return {"titulo": "Análise de Confiança da Classificação", "imagem_base64": fig_to_base64(fig)}
  
def generate_sentiment_ratio_chart():
    # GRÁFICO 5 (Novo): Proporção entre Elogios e Críticas.
    query = text("""
        SELECT categoria, COUNT(id) as total
        FROM comentarios
        WHERE status = 'CONCLUIDO' AND categoria IN ('ELOGIO', 'CRÍTICA')
        GROUP BY categoria;
    """)
    df = pd.read_sql_query(query, db.engine)
    
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    
    data = df.set_index('categoria')['total']
    colors = data.index.map({'ELOGIO': 'lightgreen', 'CRÍTICA': 'salmon'})
    
    data.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=140,
              colors=colors, textprops={'fontsize': 12})
    
    ax.set_title('Análise de Sentimento (Elogios vs. Críticas)')
    ax.set_ylabel('') # Remove o label 'total' do eixo y
    ax.axis('equal')  # Garante que o gráfico seja um círculo
    
    plt.tight_layout()
    return {"titulo": "Balanço Geral de Sentimentos", "imagem_base64": fig_to_base64(fig)}

def generate_avg_confidence_chart():
    # GRÁFICO 6: Nível de Confiança Médio da IA por Categoria.
    query = text("""
        SELECT
            categoria,
            AVG(confianca) as confianca_media
        FROM
            comentarios
        WHERE
            status = 'CONCLUIDO' AND categoria IS NOT NULL AND confianca IS NOT NULL
        GROUP BY
            categoria
        ORDER BY
            confianca_media DESC;
    """)
    df = pd.read_sql_query(query, db.engine)
    
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(df['categoria'], df['confianca_media'], color='teal')
    
    ax.set_title('Nível de Confiança Médio da IA por Categoria')
    ax.set_ylabel('Confiança Média')
    ax.set_xlabel('Categoria')
    
    # Formata o eixo Y como porcentagem
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    ax.set_ylim(0, 1)   # Garante que o eixo Y vá de 0 a 100%
    
    # Adiciona os rótulos de porcentagem em cima de cada barra
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f'{yval:.1%}', ha='center', va='bottom')

    plt.xticks(rotation=0)
    plt.tight_layout()
    return {"titulo": "Confiança Média da Classificação por Categoria", "imagem_base64": fig_to_base64(fig)}