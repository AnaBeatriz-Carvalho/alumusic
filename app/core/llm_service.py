import os
import json
import google.generativeai as genai

model = None

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel(
        "gemini-1.5-pro-latest",
        generation_config={"response_mime_type": "application/json"}
    )
except Exception as e:
    print(f"Erro ao inicializar Gemini: {e}")

PROMPT_CLASSIFICACAO = """
Você é um analista de sentimentos para a indústria musical.
Comentário: "{texto_do_comentario}"
Retorne JSON:
{{
  "categoria": "...",
  "tags_funcionalidades": [{{"codigo": "...", "explicacao": "..."}}],
  "confianca": 0.0
}}
Regras:
1. categoria ∈ [ELOGIO, CRÍTICA, SUGESTÃO, DÚVIDA, SPAM]
2. tags_funcionalidades é uma lista, ou [] se nada.
3. confianca ∈ [0.0, 1.0]
4. Retorne somente JSON.
"""

def classificar_comentario(texto: str) -> dict:
    if not model:
        return {"categoria": "ERRO", "tags_funcionalidades": [], "confianca": 0.0}

    prompt = PROMPT_CLASSIFICACAO.format(texto_do_comentario=texto)
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {"categoria": "ERRO", "tags_funcionalidades": [], "confianca": 0.0}
