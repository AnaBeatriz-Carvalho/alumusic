# generate_data.py
import json
import uuid

# Lista de comentários de exemplo para dar variedade
comentarios_base = [
    "Amei a nova música! A produção está incrível e a melodia não sai da minha cabeça.",
    "O clipe dessa banda é sempre uma obra de arte. A narrativa visual é fantástica.",
    "Achei a letra um pouco fraca, esperava mais profundidade do artista.",
    "O show foi insano! A energia da banda ao vivo é contagiante.",
    "Por que a plataforma não tem um modo offline para ouvir as playlists?",
    "Sugestão: uma integração com as letras das músicas seria perfeita.",
    "O som está estourado nesse álbum, a mixagem poderia ser melhor.",
    "Essa batida é viciante! Perfeita para treinar.",
    "Dúvida: Onde eu encontro a agenda de shows atualizada?",
    "Comprem agora o novo hit do verão! Link na bio!",
    "A colaboração (feat) entre esses dois artistas foi inesperada, mas funcionou muito bem.",
    "O autotune está muito exagerado nessa faixa, prefiro a voz natural dele.",
    "A duração do show foi muito curta, fiquei querendo mais.",
]

total_comentarios = 500  # Defina aqui quantos comentários você quer gerar
comentarios_finais = []

for i in range(total_comentarios):
    # Pega um comentário base de forma circular e adiciona um número para diferenciar
    texto = f"({i+1}) {comentarios_base[i % len(comentarios_base)]}"
    comentarios_finais.append({
        "id": str(uuid.uuid4()),
        "texto": texto
    })

# Salva a lista de comentários em um arquivo JSON
with open("comentarios_carga.json", "w", encoding="utf-8") as f:
    json.dump(comentarios_finais, f, indent=2, ensure_ascii=False)

print(f"Arquivo 'comentarios_carga.json' com {total_comentarios} comentários foi criado com sucesso!")