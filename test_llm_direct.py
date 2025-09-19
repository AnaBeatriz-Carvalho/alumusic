import json
from app import create_app
from app.core.llm_service import classificar_comentario

# Este script simula o que o worker tenta fazer, mas de forma direta.

print(">>> Iniciando teste direto do serviço de LLM...")

# Criamos uma instância do app para ter o contexto necessário
app = create_app()

with app.app_context():
    print(">>> Contexto da aplicação criado.")
    
    # Pegamos um exemplo de texto simples para testar
    texto_para_teste = "Amei a nova música! A produção está incrível."
    print(f">>> Enviando o seguinte texto para a classificação: '{texto_para_teste}'")
    
    # Chamamos a função diretamente
    resultado = classificar_comentario(texto_para_teste)
    
    print("\n" + "="*50)
    print(">>> Resultado recebido da função classificar_comentario:")
    # Usamos json.dumps para imprimir o dicionário de forma legível
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print("="*50)

    if resultado.get("categoria") == "ERRO":
        print("\n>>> DIAGNÓSTICO: A função retornou um erro!")
    else:
        print("\n>>> DIAGNÓSTICO: A função parece ter funcionado corretamente.")