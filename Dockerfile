# ===================================
# Estágio 1: Build - O Construtor 👷
# ===================================
# Usamos uma imagem completa para ter as ferramentas de compilação
FROM python:3.10-bullseye as builder

# Instala as ferramentas necessárias para compilar dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências em um ambiente virtual para isolamento
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala os requirements (aproveitando o cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===================================
# Estágio 2: Final - A Aplicação 🚀
# ===================================
# Usamos uma imagem 'slim' que é muito menor e mais segura
FROM python:3.10-slim-bullseye

# Define o diretório de trabalho
WORKDIR /app

# Copia APENAS o ambiente virtual com as dependências já instaladas do estágio de build
# Não precisamos mais do gcc, build-essential, etc.
COPY --from=builder /opt/venv /opt/venv

# Copia o código da sua aplicação
COPY . .

# Ativa o ambiente virtual para todos os comandos subsequentes
ENV PATH="/opt/venv/bin:$PATH"

# Expõe as portas que nossos serviços usarão (Flask e Streamlit)
EXPOSE 5000 8501
