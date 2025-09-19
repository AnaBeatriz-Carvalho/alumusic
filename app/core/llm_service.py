import os
import google.generativeai as genai
import json
import re
import logging 


logger = logging.getLogger(__name__)


try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))# Pegando a chave do .env
except Exception as e:
    logger.error(f"Erro CRÍTICO ao configurar a API do Gemini: {e}. Verifique sua GOOGLE_API_KEY.", exc_info=True)

PROMPT_TEMPLATE = """
Sua única função é analisar um comentário e retornar um objeto JSON.
O comentário é: "{text}"

Pense passo a passo:
1.  Identifique o sentimento principal do texto (Elogio, Crítica, Sugestão, Dúvida ou Spam).
2.  Avalie se o texto é ambíguo ou contém sentimentos mistos.
3.  Baseado na sua avaliação, atribua um score de confiança.

Responda APENAS com o objeto JSON. Não inclua explicações ou marcadores.
O JSON deve ter a seguinte estrutura:
{{
  "categoria": "string",
  "tags_funcionalidades": [
    {{"codigo": "string", "explicacao": "string"}}
  ],
  "confianca": "float"
}}

Use a seguinte escala para o score de "confianca":
- 0.9 a 1.0: Certeza muito alta, texto claro e direto.
- 0.7 a 0.89: Confiança alta, mas com leve espaço para outra interpretação.
- 0.5 a 0.69: Confiança moderada, o texto é um pouco ambíguo.
- Abaixo de 0.5: Baixa confiança, o texto é vago, sarcástico ou contém sentimentos mistos.
"""

def classificar_comentario(texto: str) -> dict:
    """
    Chama o LLM para classificar o texto e retorna um dicionário estruturado.
    Esta versão tem logging e parsing de JSON aprimorados.
    """
    response_text = None # Resposta inicial vazia para logging em caso de erro
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest') # modelo que escolhi mas pode ser alterado
        prompt = PROMPT_TEMPLATE.format(text=texto)
        
        response = model.generate_content(prompt)
        response_text = response.text
        
        
        # Tenta extrair o JSON da resposta usando regex
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            # Se não encontrar JSON, loga a resposta completa para análise
            return json.loads(response_text)

    except Exception as e:

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