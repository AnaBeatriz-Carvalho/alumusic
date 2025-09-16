
from flask import request, jsonify
from . import api_bp
from app.tasks import processar_comentario_task
from app.models import Comentario  
from app import db     

@api_bp.route('/comentarios', methods=['POST'])
def adicionar_comentarios():
    """
    Endpoint para receber comentários individualmente ou em lote.
    O ID é gerado automaticamente pelo servidor.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"erro": "Requisição precisa ser JSON"}), 400

    
    if isinstance(json_data, dict):
        comentarios_input = [json_data]
    elif isinstance(json_data, list):
        comentarios_input = json_data
    else:
        return jsonify({"erro": "Formato de entrada inválido. Envie um objeto ou uma lista de objetos."}), 400

    ids_enfileirados = []
    
    for comentario_data in comentarios_input:
        texto = comentario_data.get('texto')

        
        if not texto:
            continue  

        
        
     
        novo_comentario = Comentario(texto=texto)
        
        
        db.session.add(novo_comentario)
        db.session.commit()
        
        
        processar_comentario_task.delay(novo_comentario.id, texto)
        
       
        ids_enfileirados.append(novo_comentario.id)
      
    if not ids_enfileirados:
        return jsonify({
            "erro": "Nenhum comentário válido foi processado. O campo 'texto' é obrigatório."
        }), 400

    return jsonify({
        "mensagem": f"{len(ids_enfileirados)} comentários recebidos e enfileirados para processamento.",
        "ids_enfileirados": ids_enfileirados
    }), 202 # 202 Accepted: A requisição foi aceita e o processamento continuará em segundo plano.