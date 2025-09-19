FROM python:3.10-slim-bullseye

# Define o diretório de trabalho
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe as portas que nossos serviços Flask e Streamlit usam
EXPOSE 5000 8501
