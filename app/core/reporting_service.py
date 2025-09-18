import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io
import base64
from app.extensions import db
from sqlalchemy import text

def generate_charts():
    """
    Função principal que orquestra a geração de 5 gráficos obrigatórios.
    """
    charts = []
    
    # Executa as funções de geração de cada gráfico
    charts.append(generate_category_distribution_chart())
    charts.append(generate_daily_volume_chart())
    charts.append(generate_top_tags_chart())
    charts.append(generate_sentiment_confidence_scatter())
    charts.append(generate_status_overview_chart())
    
    # Filtra quaisquer resultados None caso um gráfico não tenha dados para ser gerado
    return [chart for chart in charts if chart is not None]

def fig_to_base64(fig):
    """Converte uma figura Matplotlib para uma string base64."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- GRÁFICOS OBRIGATÓRIOS ---

def generate_category_distribution_chart():
    """GRÁFICO 1: Distribuição geral de comentários por categoria."""
    query = text("SELECT categoria, COUNT(id) as total FROM comentarios WHERE status = 'CONCLUIDO' AND categoria IS NOT NULL GROUP BY categoria ORDER BY total DESC")
    df = pd.read_sql_query(query, db.engine)
    
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    df.plot(kind='bar', x='categoria', y='total', ax=ax, legend=False, color='skyblue')
    ax.set_title('Distribuição de Comentários por Categoria')
    ax.set_ylabel('Quantidade')
    ax.set_xlabel('')
    plt.xticks(rotation=0)
    plt.tight_layout()
    return {"titulo": "Visão Geral das Categorias", "imagem_base64": fig_to_base64(fig)}

def generate_daily_volume_chart():
    """GRÁFICO 2: Evolução do volume de comentários nos últimos 14 dias."""
    query = text("""
        SELECT DATE(data_recebimento) as dia, COUNT(id) as total 
        FROM comentarios 
        WHERE status = 'CONCLUIDO' AND data_recebimento >= current_date - interval '14 days'
        GROUP BY dia 
        ORDER BY dia;
    """)
    df = pd.read_sql_query(query, db.engine)
    
    if df.empty:
        return None
        
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
    """GRÁFICO 3: Tags mais citadas nas últimas 48 horas."""
    query = text("""
        SELECT t.codigo, COUNT(t.id) as total
        FROM tags_funcionalidades t
        JOIN comentarios c ON t.comentario_id = c.id
        WHERE c.data_recebimento >= NOW() - INTERVAL '48 hours'
        GROUP BY t.codigo
        ORDER BY total DESC
        LIMIT 7;
    """)
    df = pd.read_sql_query(query, db.engine)
    
    if df.empty:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    df.sort_values('total').plot(kind='barh', x='codigo', y='total', ax=ax, legend=False, color='coral')
    ax.set_title('Tópicos Mais Comentados (Últimas 48 Horas)')
    ax.set_xlabel('Quantidade de Menções')
    ax.set_ylabel('Tag')
    plt.tight_layout()
    return {"titulo": "Hot Topics das Últimas 48h", "imagem_base64": fig_to_base64(fig)}

def generate_sentiment_confidence_scatter():
    """GRÁFICO 4: Relação entre a Categoria e a Confiança da Classificação."""
    query = text("SELECT categoria, confianca FROM comentarios WHERE status = 'CONCLUIDO' AND categoria IN ('ELOGIO', 'CRÍTICA')")
    df = pd.read_sql_query(query, db.engine)
    
    if df.empty or len(df) < 2:
        return None
        
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = df['categoria'].map({'ELOGIO': 'green', 'CRÍTICA': 'red'})
    ax.scatter(df.index, df['confianca'], c=colors, alpha=0.6)
    ax.set_title('Confiança da IA na Classificação de Sentimentos')
    ax.set_ylabel('Nível de Confiança (0.0 a 1.0)')
    ax.set_xlabel('Comentários Individuais')
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    # Criando uma legenda customizada
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label='Elogio', markerfacecolor='green', markersize=10),
                       plt.Line2D([0], [0], marker='o', color='w', label='Crítica', markerfacecolor='red', markersize=10)]
    ax.legend(handles=legend_elements, title="Categoria")
    plt.tight_layout()
    return {"titulo": "Análise de Confiança da Classificação", "imagem_base64": fig_to_base64(fig)}
    
def generate_status_overview_chart():
    """GRÁFICO 5: Status geral dos comentários no sistema."""
    query = text("SELECT status, COUNT(id) as total FROM comentarios GROUP BY status")
    df = pd.read_sql_query(query, db.engine)
    
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    df.set_index('status')['total'].plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90,
                                         colors=['#66b3ff','#ff9999','#99ff99','#ffcc99'])
    ax.set_title('Status de Processamento dos Comentários')
    ax.set_ylabel('') # Remove o label 'total' do eixo y
    plt.tight_layout()
    return {"titulo": "Status Geral do Processamento", "imagem_base64": fig_to_base64(fig)}