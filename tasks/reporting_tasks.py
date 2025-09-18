from celery_app import celery
from celery.utils.log import get_task_logger
from redis import Redis
import json
from app import create_app

logger = get_task_logger(__name__)
# Chave que usaremos para salvar o relatório no cache do Redis
REDIS_CACHE_KEY = "realtime_report_data"

@celery.task
def generate_report_task():
    """
    Tarefa que gera os gráficos e os salva como JSON no cache do Redis.
    """
    app = create_app()
    with app.app_context():
        from app.core.reporting_service import generate_charts
        
        logger.info("Iniciando geração do relatório em tempo real...")
        try:
            charts_data = generate_charts()
            redis_client = Redis.from_url(celery.conf.broker_url)
            # Converte a lista de gráficos para uma string JSON e salva no Redis
            redis_client.set(REDIS_CACHE_KEY, json.dumps(charts_data))
            logger.info(f"Relatório salvo no cache com {len(charts_data)} gráficos.")
        except Exception as e:
            logger.error(f"Falha ao gerar o relatório: {e}", exc_info=True)