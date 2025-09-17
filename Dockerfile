# Escolhe uma imagem base com Python
FROM python:3.10-slim-bullseye

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala pacotes do sistema necessários
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential && rm -rf /var/lib/apt/lists/*

# Copia o restante do código da aplicação
COPY . .

# Define a porta que o Flask vai usar
EXPOSE 5000

# Comando para rodar o Flask
CMD ["flask", "run", "--host=0.0.0.0"]
