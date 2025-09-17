import os
import json
import google.generativeai as genai

# Inicialização do Gemini
model = None
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel(
        "gemini-1.5-pro-latest",
        generation_config={"response_mime_type": "application/json"}
    )
except Exception as e:
    print(f"Erro ao inicializar Gemini: {e}")

# Prompt base
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
4. Retorne somente JSON, sem explicações adicionais.
"""

def classificar_comentario(texto: str) -> dict:
    """Classifica um único comentário usando o Gemini"""
    if not model:
        return {"categoria": "ERRO", "tags_funcionalidades": [], "confianca": 0.0}

    prompt = PROMPT_CLASSIFICACAO.format(texto_do_comentario=texto)
    try:
        response = model.generate_content(prompt)

        # Algumas versões do SDK retornam em response.candidates[0].content.parts
        output = getattr(response, "text", None) or str(response)

        data = json.loads(output)

        # Garantir defaults
        return {
            "categoria": data.get("categoria", "SPAM"),
            "tags_funcionalidades": data.get("tags_funcionalidades", []),
            "confianca": float(data.get("confianca", 0.5)),
        }
    except Exception as e:
        print(f"[ERRO GEMINI] {e}")
        return {"categoria": "ERRO", "tags_funcionalidades": [], "confianca": 0.0}


def classificar_lote(comentarios: list[str]) -> list[dict]:
    """Classifica uma lista de comentários (sequencial por enquanto)"""
    resultados = []
    for texto in comentarios:
        resultados.append(classificar_comentario(texto))
    return resultados
