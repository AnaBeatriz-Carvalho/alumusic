# Estágio de construção
FROM python:3.10-slim-bullseye AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Imagem final
FROM python:3.10-slim-bullseye

WORKDIR /app

COPY --from=builder /app /app
COPY . .

ENV FLASK_APP=src/app.py
EXPOSE 5000

CMD ["python", "--bind", "0.0.0.0:5000", "src.app:app"]
