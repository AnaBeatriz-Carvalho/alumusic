import os
import google.generativeai as genai
import json
import re
import logging

logger = logging.getLogger(__name__)

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    logger.error(f"Erro CRÍTICO ao configurar a API do Gemini: {e}", exc_info=True)

PROMPT_TEMPLATE = """
Você é um especialista em análise de sentimentos para a indústria musical. Sua única função é analisar um comentário e retornar um objeto JSON.
O comentário a ser analisado é: "{text}"

Pense passo a passo:
1. Identifique o sentimento principal do texto (Elogio, Crítica, Sugestão, Dúvida ou Spam).
2. Extraia os tópicos ou funcionalidades específicas mencionadas no texto.
3. Avalie a ambiguidade do texto para definir um score de confiança.

Regras para Tags:
- O "codigo" da tag deve ser conciso, em inglês e usar o formato snake_case (ex: `qualidade_vocal`, `preco_ingresso`).
- A "explicacao" deve ser uma descrição curta em português.
- Se nenhum tópico específico for encontrado, retorne uma lista vazia.

Responda APENAS com o objeto JSON. Não inclua texto extra.
O JSON deve ter a seguinte estrutura:
{{
  "categoria": "string",
  "tags_funcionalidades": [
    {{"codigo": "string", "explicacao": "string"}}
  ],
  "confianca": "float"
}}

---
EXEMPLOS:
Comentário de Exemplo 1: "A batida é boa, mas o autotune exagerado estragou a música pra mim."
JSON de Saída Exemplo 1:
{{
  "categoria": "CRÍTICA",
  "tags_funcionalidades": [
    {{"codigo": "qualidade_batida", "explicacao": "Refere-se à qualidade da batida ou ritmo da música"}},
    {{"codigo": "uso_autotune", "explicacao": "Refere-se ao uso de autotune nos vocais"}}
  ],
  "confianca": 0.85
}}
---
"""

def classificar_comentario(texto: str) -> dict:
    response_text = None
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = PROMPT_TEMPLATE.format(text=texto)
        response = model.generate_content(prompt)
        response_text = response.text
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            json_output = json.loads(json_str)
            if 'categoria' in json_output and isinstance(json_output['categoria'], str):
                json_output['categoria'] = json_output['categoria'].upper()
            return json_output
        else:
            json_output = json.loads(response_text)
            if 'categoria' in json_output and isinstance(json_output['categoria'], str):
                json_output['categoria'] = json_output['categoria'].upper()
            return json_output
    except Exception as e:
        logger.error(f"Falha ao classificar comentário. Erro: {e}", exc_info=True)
        return {"categoria": "ERRO", "tags_funcionalidades": [], "confianca": 0.0, "error_message": str(e)}

def generate_weekly_summary(comments_data: list) -> str:
    all_comments_text = "\n- ".join(comments_data)
    summary_prompt = f"""
    Você é um analista de dados sênior... (seu prompt de resumo)
    Comentários da semana:
    - {all_comments_text}
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(summary_prompt)
        return response.text
    except Exception as e:
        logger.error(f"Falha ao gerar resumo semanal: {e}", exc_info=True)
        return "Não foi possível gerar o resumo devido a um erro na análise de IA."

def answer_question_with_context(question: str, context: str) -> str:
    qa_prompt = f"""
    Você é um assistente de IA da AluMusic... (seu prompt de Q&A)
    Contexto: {context}
    Pergunta: "{question}"
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(qa_prompt)
        return response.text
    except Exception as e:
        logger.error(f"Falha ao gerar resposta de Q&A: {e}", exc_info=True)
        return "Desculpe, não foi possível processar a sua pergunta."

