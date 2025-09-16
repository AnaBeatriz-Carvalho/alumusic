# app/tasks.py
from .extensions import celery, db
from . import create_app
from .core.llm_service import classificar_comentario
from .models import Comentario, Classificacao, TagFuncionalidade

@celery.task
def processar_comentario_task(comentario_id, texto):
    """
    Tarefa Celery para processar um único comentário em segundo plano.
    """
    app = create_app('default') # Cria um contexto de aplicação para a tarefa
    with app.app_context():
        # 1. Verifica se o comentário já existe (lógica de idempotência)
        comentario_existente = Comentario.query.get(comentario_id)
        if comentario_existente:
            print(f"Comentário com ID {comentario_id} já existe. Pulando.")
            return

        # 2. Salva o comentário original no banco
        novo_comentario = Comentario(id=comentario_id, texto=texto)
        db.session.add(novo_comentario)

        # 3. Chama o LLM para classificar
        resultado_llm = classificar_comentario(texto)
        
        if resultado_llm['categoria'] == 'ERRO':
            print(f"Erro ao classificar o comentário ID {comentario_id}. Lógica de fallback pode ser adicionada aqui.")
            db.session.rollback() # Desfaz a adição do comentário se a classificação falhar
            return

        # 4. Salva a classificação e as tags
        nova_classificacao = Classificacao(
            comentario_id=comentario_id,
            categoria=resultado_llm.get('categoria', 'INDEFINIDO'),
            confianca=resultado_llm.get('confianca', 0.0)
        )
        db.session.add(nova_classificacao)
        db.session.flush()  # Garante que nova_classificacao.id esteja disponível

        for tag_data in resultado_llm.get('tags_funcionalidades', []):
            nova_tag = TagFuncionalidade(
                classificacao_id=nova_classificacao.id,
                codigo=tag_data.get('codigo'),
                explicacao=tag_data.get('explicacao')
            )
            db.session.add(nova_tag)
            
        db.session.commit()
        print(f"Comentário ID {comentario_id} processado e salvo com sucesso.")