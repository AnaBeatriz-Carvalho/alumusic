# app/tasks.py

# 👇 Importe 'celery' e 'db' diretamente de extensions
from .extensions import celery, db
from .core.llm_service import classificar_comentario
from .models.comment import Comentario, TagFuncionalidade

@celery.task(bind=True)
def processar_classificacao_task(self, comentario_id):
    """
    Tarefa Celery para buscar um comentário PENDENTE, classificá-lo
    e ATUALIZAR seu status e dados no banco.
    O contexto da aplicação é injetado automaticamente.
    """
    try:
        # 1. Busca o comentário que a API já salvou
        comentario = db.session.query(Comentario).filter_by(id=comentario_id).first()
        
        if not comentario:
            print(f"ERRO: Comentário ID {comentario_id} não encontrado no banco.")
            return

        if comentario.status == 'CONCLUIDO':
            print(f"INFO: Comentário ID {comentario_id} já foi processado. Pulando.")
            return

        # 2. Chama o LLM para classificar (a parte demorada)
        resultado_llm = classificar_comentario(comentario.texto)
        
        if resultado_llm['categoria'] == 'ERRO':
            comentario.status = 'FALHOU'
            db.session.commit()
            # Tenta novamente em 60 segundos
            self.retry(exc=Exception("Falha na classificação do LLM"), countdown=60)
            return

        # 3. ATUALIZA o comentário existente com os resultados
        comentario.categoria = resultado_llm.get('categoria', 'INDEFINIDO')
        comentario.confianca = resultado_llm.get('confianca', 0.0)
        comentario.status = 'CONCLUIDO'

        # 4. Limpa tags antigas (caso a tarefa seja reexecutada) e adiciona as novas
        db.session.query(TagFuncionalidade).filter_by(comentario_id=comentario.id).delete()
        for tag_data in resultado_llm.get('tags_funcionalidades', []):
            nova_tag = TagFuncionalidade(
                comentario_id=comentario.id,
                codigo=tag_data.get('codigo'),
                explicacao=tag_data.get('explicacao')
            )
            db.session.add(nova_tag)
            
        db.session.commit()
        print(f"Comentário ID {comentario_id} processado e ATUALIZADO com sucesso.")

    except Exception as e:
        db.session.rollback()
        print(f"EXCEÇÃO ao processar {comentario_id}: {e}. Retentando...")
        self.retry(exc=e, countdown=60)
    finally:
        # Garante que a sessão do banco seja fechada para liberar a conexão
        db.session.close()