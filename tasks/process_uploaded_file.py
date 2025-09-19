import io
from celery.utils.log import get_task_logger
from app.extensions import celery
from app.core.llm_service import classificar_comentario

logger = get_task_logger(__name__)


@celery.task(bind=True)
def process_uploaded_texts(self, textos, user_identity=None):
    """Processa uma lista de textos chamando o classificar_comentario para cada um.
    Retorna uma lista de {texto, analise}.
    """
    logger.info(f"Iniciando processamento em lote para {len(textos)} textos (usuario={user_identity})")
    resultados = []
    for texto in textos:
        try:
            analise = classificar_comentario(texto)
            resultados.append({"texto": texto, "analise": analise})
        except Exception as e:
            logger.error(f"Erro ao processar texto: {e}", exc_info=True)
            resultados.append({"texto": texto, "analise": {"categoria": "ERRO", "error_message": str(e)}})

    logger.info("Processamento em lote finalizado")
    return resultados
