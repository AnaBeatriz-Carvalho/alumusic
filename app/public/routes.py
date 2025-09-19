from . import public_bp
from flask import jsonify
from redis import Redis
import json
from app.extensions import celery
from app.core.reporting_service import generate_charts

REDIS_CACHE_KEY = "realtime_report_data"
CACHE_TIMEOUT_SECONDS = 60

@public_bp.route('/relatorio/semana', methods=['GET'])
def get_realtime_report():
    """
    Endpoint público que serve dados do cache ou os gera sob demanda se o cache expirou.
    """
    try:
        redis_client = Redis.from_url(celery.conf.broker_url)
        cached_data = redis_client.get(REDIS_CACHE_KEY)
        
        if cached_data:
            # Se encontrou dados no cache, decodifica do JSON e retorna
            charts = json.loads(cached_data.decode('utf-8'))
            return jsonify({"graficos": charts}), 200
        else:
            charts = generate_charts()
            
            redis_client.setex(
                REDIS_CACHE_KEY,
                CACHE_TIMEOUT_SECONDS,
                json.dumps(charts)
            )
            
            # Retorna os gráficos recém-criados para o usuário
            return jsonify({"graficos": charts}), 200

    except Exception as e:
        return jsonify({"erro": f"Não foi possível gerar ou buscar o relatório: {e}"}), 500