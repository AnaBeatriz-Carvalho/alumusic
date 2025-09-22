# 🎵 AluMusic Insights - Análise de Feedback com IA


## 1. Apresentação e Resultados

**AluMusic Insights** é uma plataforma de análise de dados projetada para processar e extrair insights valiosos a partir de milhares de comentários de ouvintes.  
O sistema foi desenvolvido como parte de um **desafio técnico da Alura**, com foco em **Python**, **LLMs** e arquitetura escalável.

### Resultados
- Ingestão de comentários em tempo real com processamento assíncrono.  
- Classificação automática via **Google Gemini** (`gemini-1.5-flash-latest`).  
- **Dashboard privado** para curadoria + **Relatório público** atualizado a cada 60 s.  
- **Testes automatizados** com PyTest (unitários, integração e evals).  
- Pipeline de avaliação demonstrou **97% de acurácia** em dataset de 100 exemplos.  

---

## 2. ⚙️ Requisitos

- Python **3.10+**  
- Docker + Docker Compose  
- Variáveis de ambiente definidas em `.env`  

---

## 3. 🚀 Como Executar o Projeto

### Configuração do Ambiente
Crie um arquivo `.env` na raiz com as variáveis abaixo:

```ini
# Segurança
SECRET_KEY="uma_chave_secreta_local"
JWT_SECRET_KEY="uma_chave_jwt_local"

# Banco de dados Postgres
POSTGRES_USER=alumusic
POSTGRES_PASSWORD=alumusic
POSTGRES_DB=alumusic
DATABASE_URL=postgresql://alumusic:alumusic@alumusic:5432/alumusic

# Celery (broker e backend de resultado)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Google Gemini API key (LLM)
GOOGLE_API_KEY="SUA_CHAVE_GOOGLE_GEMINI"

# --- Configurações de E-mail para Resumo Semanal (para MailHog) ---
SMTP_SERVER=mailhog
SMTP_PORT=1025
SMTP_USER=""
SMTP_PASSWORD=""
SENDER_EMAIL=noreply@alumusic.com

```

### Passos para Execução
1. Subir os containers:
    ```bash
    docker-compose down -v
    docker-compose up --build -d
    ```

2. Aplicar migrações do banco:
    ```bash
    docker-compose exec api flask db migrate
    docker-compose exec api flask db upgrade
    ```

3. Popular dados iniciais:
    ```bash
    python seed_weekly.py
    ```

4. Acesse o dashboard em [http://localhost:8501](http://localhost:8501).

5. Executar testes e evals:
    ```bash
    docker-compose exec api pytest -m e2e -sv
    ```

---

## 4. ✨ Funcionalidades Principais

### Ingestão Assíncrona de Dados
- Endpoints de ingestão:
    - `POST /api/llm/analyze` — aceita upload de arquivo (.csv, .json) ou formulário com campo `text`. Enfileira comentários para classificação (requer JWT).
    - `POST /api/comentarios` — aceita JSON (objeto ou lista) com comentários e enfileira para processamento (requer JWT).
- Suporte a lotes grandes (processados em paralelo com Celery + Redis).

### Processamento com IA (LLM)
- Classificação em {**ELOGIO**, **CRÍTICA**, **SUGESTÃO**, **DÚVIDA**, **SPAM**}.
- Extração de `tags_funcionalidades` e score de confiança (0–1).

### Dashboard Privado Interativo
- Construído em **Streamlit**.
- Login + busca, histórico, filtros e exportação (CSV/JSON).

### Relatório Público em Tempo Real
- Rota pública: `GET /relatorio/semana` — retorna dados e gráficos do relatório semanal em tempo real (cache Redis, TTL ~60s).
- Pelo menos 5 gráficos obrigatórios (categorias, evolução temporal, top tags, distribuição por confiança, evolução por semana).

### Evals e Métricas de IA
- Executados com PyTest + dataset de teste (veja `tests/evals`).
- Relatório automático de métricas.

### Extras Implementados
- Resumo semanal com LLM (CLI: `flask generate-summary`).
- Seed histórico de até 8 semanas (CLI: `flask seed-historical-data --weeks N`).
- Endpoint Q&A para insights: `POST /api/insights/perguntar` (requer JWT).

---

## 5. 🗺️ Endpoints Principais da API

Observação: as rotas protegidas requerem um header Authorization: Bearer <JWT_TOKEN> gerado pelo endpoint de login.

- **Auth (public)**  
    - `POST /auth/register` — cria um usuário.  
    - `POST /auth/login`  

- **API (requer JWT)**  
    - `POST /api/llm/analyze` — upload de arquivo (.csv/.json) no campo `file` ou em texto.  
    - `POST /api/comentarios` — aceita JSON (objeto ou lista) com campos mínimos {"texto": "..."} e enfileira.  
    - `GET /api/comentarios` — lista comentários.  
    - `GET /api/comentarios/<uuid:comentario_id>` — detalhes de um comentário específico.  
    - `POST /api/insights/perguntar` — Q&A sobre os últimos resumos semanais.  
    - `POST /api/stakeholders` — cadastra stakeholder.  

- **Public (não requer JWT)**  
    - `GET /relatorio/semana` — retorna os gráficos e dados do relatório semanal.

---

## 6. 🏛️ Arquitetura e Estrutura

### Estrutura do Projeto

```plaintext
alumusic/
├── app/                 # Extensões e comandos Flask
├── tasks/               # Tarefas Celery (processamento, relatórios, resumos semanais)
├── migrations/          # Migrações do banco (Alembic)
├── tests/               # Testes unitários, integração e evals
├── streamlit_app.py     # Dashboard privado
├── seed_weekly.py       # Seed inicial de dados semanais
├── docker-compose.yml   # Orquestração de containers
├── Dockerfile           # Build da API Flask
└── requirements.txt     # Dependências
```

### Diagrama de Arquitetura

```mermaid
graph TD

    subgraph "Navegador do Utilizador"
        B["Dashboard Streamlit"]
    end

    subgraph "Infraestrutura Docker"
        D["API Flask"]
        E["Worker Celery"]
        J["Agendador (Beat)"]
        F["Banco de Dados (PostgreSQL)"]
        G["Fila e Cache (Redis)"]
        M["Capturador de E-mail (MailHog)"]
    end

    subgraph "Serviço Externo"
        H["API Google Gemini"]
    end

    subgraph "Ambiente de Teste"
        A["Testes Pytest"]
    end

    %% Fluxo Principal de Análise de Comentários
    B -- "Upload de Ficheiro / Texto c/ JWT" --> D["/api/llm/analyze"]
    A -- "Lote de JSON c/ JWT" --> D["/api/comentarios"]
    D -- "Enfileira Tarefa de Classificação" --> G

    E -- "Pega Tarefa de Classificação" --> G
    E -- "1. Envia Texto para Análise" --> H
    H -- "2. Retorna Classificação" --> E
    E -- "3. Salva Resultado" --> F["Comentários"]

    %% Fluxo do Relatório Público
    B -- "Requisição Pública" --> D["/api/relatorio/semana"]
    D -- "Lê Cache do Relatório" --> G

    %% Fluxo do Resumo Semanal (Agendado)
    J -- "1. Aciona Tarefa Semanal" --> G
    E -- "2. Pega Tarefa de Resumo" --> G
    E -- "3. Lê Comentários da Semana" --> F
    E -- "4. Envia Comentários para Resumo" --> H
    H -- "5. Retorna Resumo Gerado" --> E
    E -- "6. Salva Resumo" --> F["Resumos Semanais"]
    E -- "7. Envia E-mail" --> M

    %% Fluxo do Insights Q&A
    B -- "Pergunta em Linguagem Natural c/ JWT" --> D["/api/insights/perguntar"]
    D -- "1. Busca Últimos Resumos" --> F
    D -- "2. Envia Pergunta + Contexto" --> H
    H -- "3. Retorna Resposta" --> D
    D -- "4. Devolve Resposta JSON" --> B
```
---

## 7. 📊 Funcionalidades Extras

### Resumo Semanal Automático por E-mail
- Gera um resumo das principais tendências usando LLM.  
- E-mails dos stakeholders podem ser cadastrados diretamente na aplicação.  
- Envio realizado via [Mailhog](https://github.com/mailhog/MailHog).  
- Acesse [http://localhost:8025/](http://localhost:8025/) para validar os e-mails enviados.

### Seed de Dados Históricos
- Popular dados das últimas 8 semanas:
  ```bash
  docker-compose exec api flask seed-historical-data --weeks 8
  ```

### Insight Q&A
- Endpoint `/insights/perguntar` responde perguntas em linguagem natural com base nos resumos semanais.

---

## 📞 Contato

**Ana Beatriz Carvalho Oliveira**  
📧 beatriz.carvalho0804@gmail.com
