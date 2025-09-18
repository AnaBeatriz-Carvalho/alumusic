from . import public_bp
from flask import jsonify
from redis import Redis
import json
from app.extensions import celery

@public_bp.route('/relatorio/semana', methods=['GET'])
def get_realtime_report():
    """
    Endpoint público e rápido que lê os dados pré-calculados do cache do Redis.
    """
    try:
        redis_client = Redis.from_url(celery.conf.broker_url)
        cached_data = redis_client.get("realtime_report_data") # Usa a mesma chave
        
        if cached_data:
            # Se encontrou dados no cache, decodifica e retorna
            charts = json.loads(cached_data.decode('utf-8'))
            return jsonify({"graficos": charts}), 200
        else:
            # Se o cache está vazio (ex: a tarefa ainda não rodou)
            return jsonify({"mensagem": "Relatório está sendo gerado, por favor, aguarde e atualize em um minuto."}), 202

    except Exception as e:
        return jsonify({"erro": f"Não foi possível buscar o relatório do cache: {e}"}), 500