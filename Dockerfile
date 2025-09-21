FROM python:3.10-slim-bullseye


WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Portas do Flask e Streamlit usam
EXPOSE 5000 8501
