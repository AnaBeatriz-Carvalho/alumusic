# app/tasks.py

from .extensions import celery, db
# 🚫 REMOVA ESTA LINHA PARA QUEBRAR O CICLO DE IMPORTAÇÃO:
# from . import create_app 

from .core.llm_service import classificar_comentario
# 👇 ATUALIZE OS IMPORTS DO MODELO (REMOVA Classificacao)
from .models import Comentario, TagFuncionalidade

@celery.task(bind=True) # Adicione bind=True para ter acesso ao 'self' da tarefa
def processar_comentario_task(self, comentario_id, texto):
    """
    Tarefa Celery para processar um único comentário em segundo plano.
    O contexto da aplicação é fornecido pelo Celery.
    """
    # 👇 Acessamos a aplicação através do 'self.app' fornecido pelo Celery
    #    Isso elimina a necessidade de chamar create_app() aqui.
    with self.app.app_context():
        # 1. Verifica se o comentário já existe (lógica de idempotência)
        comentario_existente = Comentario.query.get(comentario_id)
        if comentario_existente:
            print(f"Comentário com ID {comentario_id} já existe. Pulando.")
            return

        # 2. Chama o LLM para classificar ANTES de interagir com o banco
        resultado_llm = classificar_comentario(texto)
        
        if resultado_llm['categoria'] == 'ERRO':
            print(f"Erro ao classificar o comentário ID {comentario_id}. Lógica de fallback pode ser adicionada aqui.")
            # A tarefa pode ser tentada novamente se configurada
            # self.retry(exc=Exception("Falha na classificação do LLM"))
            return

        # 3. Salva o comentário com os dados da classificação
        novo_comentario = Comentario(
            id=comentario_id,
            texto=texto,
            categoria=resultado_llm.get('categoria', 'INDEFINIDO'),
            confianca=resultado_llm.get('confianca', 0.0)
        )
        db.session.add(novo_comentario)

        # 4. Salva as tags, vinculando-as diretamente ao novo comentário
        for tag_data in resultado_llm.get('tags_funcionalidades', []):
            nova_tag = TagFuncionalidade(
                # Associa a tag diretamente ao comentário
                comentario=novo_comentario, 
                codigo=tag_data.get('codigo'),
                explicacao=tag_data.get('explicacao')
            )
            db.session.add(nova_tag)
            
        db.session.commit()
        print(f"Comentário ID {comentario_id} processado e salvo com sucesso.")