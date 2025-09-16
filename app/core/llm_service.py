# app/core/llm_service.py
import os
import json
import google.generativeai as genai

# Variável para armazenar o modelo inicializado
model = None

# Inicialize o modelo uma vez para reutilização
try:
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")
    
    genai.configure(api_key=google_api_key)

    # CORREÇÃO: Configurar o modelo para gerar JSON
    generation_config = {
      "response_mime_type": "application/json",
    }
    
    # CORREÇÃO: Instanciar o modelo do Gemini que será usado
    # Use 'gemini-1.5-pro-latest' ou 'gemini-pro'
    model = genai.GenerativeModel(
        "gemini-1.5-pro-latest",
        generation_config=generation_config
    )
    
except Exception as e:
    print(f"Erro ao inicializar o modelo Gemini: {e}")

PROMPT_CLASSIFICACAO = """
Você é um analista de sentimentos para a indústria musical na empresa AluMusic.
Sua tarefa é classificar um comentário de ouvinte e extrair funcionalidades mencionadas.
O comentário é: "{texto_do_comentario}"

Analise o comentário e retorne um objeto JSON com a seguinte estrutura:
{{
  "categoria": "...",
  "tags_funcionalidades": [
    {{"codigo": "...", "explicacao": "..."}}
  ],
  "confianca": 0.0
}}

As regras são:
1.  A "categoria" deve ser UMA das seguintes: ELOGIO, CRÍTICA, SUGESTÃO, DÚVIDA, SPAM.
2.  "tags_funcionalidades" é uma lista de aspectos específicos mencionados. Crie um `codigo` curto (snake_case) e uma `explicacao` clara. Se nada for mencionado, retorne uma lista vazia [].
3.  "confianca" é um float de 0.0 a 1.0 indicando sua certeza na classificação da categoria.
4.  Responda APENAS com o JSON válido. Não adicione texto extra nem use markdown (```json).
"""

def classificar_comentario(texto: str) -> dict:
    """
    Usa um LLM para classificar um comentário e extrair tags.
    Retorna um dicionário com a estrutura definida no prompt.
    """
    # CORREÇÃO: Verificar se o modelo foi inicializado corretamente
    if not model:
        # Você pode optar por lançar uma exceção ou retornar um erro padrão
        error_msg = "Modelo Gemini não inicializado. Verifique a chave de API e os logs de inicialização."
        print(error_msg)
        return {
            "categoria": "ERRO",
            "tags_funcionalidades": [],
            "confianca": 0.0,
            "error_message": error_msg
        }

    prompt_formatado = PROMPT_CLASSIFICACAO.format(texto_do_comentario=texto)

    try:
        # CORREÇÃO: Usar o método generate_content do Gemini
        response = model.generate_content(prompt_formatado)
        
        # CORREÇÃO: A resposta JSON está em response.text
        resultado_str = response.text
        return json.loads(resultado_str)
        
    except Exception as e:
        print(f"Erro na chamada da API do LLM: {e}")
        # Retornar uma estrutura de erro padrão
        return {
            "categoria": "ERRO",
            "tags_funcionalidades": [],
            "confianca": 0.0,
            "error_message": str(e)
        }