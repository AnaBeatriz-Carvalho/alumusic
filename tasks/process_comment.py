import uuid
from app.extensions import celery, db
from app.models.comment import Comentario, TagFuncionalidade
from app.core.llm_service import classificar_comentario
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery.task(bind=True)
def processar_classificacao_task(self, comentario_id_str: str):
    # Sem 'create_app()' ou 'with app.app_context()' aqui.
    # A ContextTask configurada no app/__init__.py cuidará disso.
    
    logger.info(f"Iniciando processamento para o comentário ID: {comentario_id_str}")
    comentario_id = uuid.UUID(comentario_id_str)
    # Esta linha agora deve funcionar
    comentario = db.session.get(Comentario, comentario_id)

    if not comentario or comentario.status != 'PENDENTE':
        logger.warning(f"Comentário {comentario_id} não encontrado ou já processado.")
        return

    try:
        comentario.status = 'PROCESSANDO'
        db.session.commit()

        resultado_llm = classificar_comentario(comentario.texto)

        if resultado_llm.get('categoria') == 'ERRO':
            raise ValueError(f"Falha na classificação pelo LLM: {resultado_llm.get('error_message', 'Erro desconhecido')}")

        comentario.categoria = resultado_llm.get('categoria')
        comentario.confianca = resultado_llm.get('confianca')

        tags_to_delete = TagFuncionalidade.query.filter_by(comentario_id=comentario.id).all()
        for tag in tags_to_delete:
            db.session.delete(tag)

        novas_tags = [
            TagFuncionalidade(
                codigo=tag_data.get('codigo'),
                explicacao=tag_data.get('explicacao'),
                comentario_id=comentario.id
            )
            for tag_data in resultado_llm.get('tags_funcionalidades', [])
        ]
        if novas_tags:
            db.session.bulk_save_objects(novas_tags)

        comentario.status = 'CONCLUIDO'
        db.session.commit()
        
        logger.info(f"Comentário {comentario_id} processado com sucesso.")

    except Exception as e:
        db.session.rollback()
        if comentario:
            comentario.status = 'FALHOU'
            db.session.commit()
        logger.error(f"Falha ao processar comentário {comentario_id}: {e}", exc_info=True)
        raise