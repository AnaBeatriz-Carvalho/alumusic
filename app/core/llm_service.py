import os
import google.generativeai as genai
import json
import re
import logging # Usaremos o logger para depuração

# Configura um logger para este módulo
logger = logging.getLogger(__name__)

# Pega a chave de API do seu arquivo .env
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    logger.error(f"Erro CRÍTICO ao configurar a API do Gemini: {e}. Verifique sua GOOGLE_API_KEY.", exc_info=True)

# Prompt refinado para ser ainda mais direto e evitar textos extras.
PROMPT_TEMPLATE = """
Sua única função é analisar um comentário e retornar um objeto JSON.
O comentário é: "{text}"

Responda APENAS com o objeto JSON. Não inclua explicações, introduções, ou marcadores de formatação como ```json.
O JSON deve ter a seguinte estrutura e tipos de dados:
{{
  "categoria": "string",
  "tags_funcionalidades": [
    {{"codigo": "string", "explicacao": "string"}}
  ],
  "confianca": "float"
}}

As categorias válidas são: "ELOGIO", "CRÍTICA", "SUGESTÃO", "DÚVIDA", "SPAM".
Se não encontrar tags, retorne uma lista vazia.
"""

def classificar_comentario(texto: str) -> dict:
    """
    Chama o LLM para classificar o texto e retorna um dicionário estruturado.
    Esta versão tem logging e parsing de JSON aprimorados.
    """
    response_text = None # Para armazenar a resposta crua para depuração
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = PROMPT_TEMPLATE.format(text=texto)
        
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Lógica de limpeza e parsing mais robusta
        # 1. Tenta encontrar o JSON usando uma expressão regular que busca por { ... }
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            # 2. Se não encontrar, assume que a resposta pode ser o JSON puro e tenta carregar
            return json.loads(response_text)

    except Exception as e:
        # 👇 LOGGING MELHORADO 👇
        # Se qualquer erro ocorrer, vamos logar tudo que precisamos para depurar.
        logger.error(
            f"Falha ao classificar comentário. Erro: {e}",
            exc_info=True # Inclui o traceback completo do erro
        )
        logger.error(f"Texto do comentário (início): {texto[:100]}...")
        logger.error(f"Resposta CRUA recebida da LLM: {response_text}")
        
        # Retorna um dicionário de erro padronizado
        return {
            "categoria": "ERRO",
            "tags_funcionalidades": [],
            "confianca": 0.0,
            "error_message": str(e)
        }