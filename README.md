# 🎵 AluMusic Insights — README detalhado

Este README descreve o projeto AluMusic Insights com instruções completas para execução local, testes/evals, arquitetura, decisões de design e notas operacionais. Está escrito em português para facilitar o onboarding da equipe.

Sumário
- Apresentação e resultados do case
- Como executar o projeto (passo a passo)
- Como rodar testes e evals
- Principais decisões de design
- Estrutura do repositório e referências rápidas

## Apresentação do projeto e resultados do case

AluMusic Insights é uma aplicação para ingestão, processamento e visualização de comentários de ouvintes. O objetivo do case foi demonstrar uma pipeline de processamento assíncrono que combina infra tradicional (Flask, PostgreSQL, Celery, Redis) com LLMs (Google Gemini) para:

- Classificar categoria (ex.: ELOGIO, CRÍTICA, SUGESTÃO, DÚVIDA, SPAM).
- Extrair tags funcionais (códigos de tópicos extraídos por IA).
- Apresentar um dashboard privado para curadores e um relatório público atualizado periodicamente.

Resultados esperados do case:

- Pipeline E2E capaz de processar lotes grandes sem bloquear a API (Celery + Redis).
- Classificação automática com métricas geradas por scripts de avaliação (Acurácia, Precisão, Recall, F1-Score, Matriz de Confusão).
- Dashboard interativo (Streamlit) com filtros, exportação CSV/JSON e autorefresh para curadoria.

## Passo a passo detalhado para executar o projeto

Pré-requisitos
- Docker e Docker Compose instalados localmente.
- (Opcional) Python 3.10+ se quiser rodar partes fora de contêiner.

1) Clone o repositório

   git clone <URL_DO_REPOSITORIO>
   cd alumusic

2) Variáveis de ambiente

Crie um arquivo `.env` na raiz com as variáveis necessárias. Não há um arquivo `.env.example` no repositório; seguem as variáveis mínimas necessárias para rodar:

   SECRET_KEY="uma_chave_secreta"
   JWT_SECRET_KEY="uma_chave_jwt"
   POSTGRES_USER=alumusic
   POSTGRES_PASSWORD=alumusic
   POSTGRES_DB=alumusic
   DATABASE_URL=postgresql://alumusic:alumusic@alumusic:5432/alumusic
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   GOOGLE_API_KEY="SUA_CHAVE_GOOGLE_GEMINI"

3) Build e run com Docker Compose (recomendado)

Suba todos os serviços com:

   docker-compose up --build -d

O compose já define os serviços principais:

- api: serviço Flask + Gunicorn (porta mapeada 5001:5000)
- worker: Celery worker
- streamlit: frontend privado (porta 8501)
- alumusic: PostgreSQL
- redis: Redis para broker/result backend e cache

4) Acesse as interfaces

- Dashboard (privado): http://localhost:8501 — registre um usuário na aba "Registrar" e faça login.
- API (interno/externo): http://localhost:5001 (o container expõe 5000 internamente; o compose mapeia para 5001 localmente).

5) Logs e troubleshooting básicos

Visualizar logs do API:

   docker-compose logs -f api

Verificar status dos contêineres:

   docker ps -a

Se o PostgreSQL falhar no healthcheck, confirme as variáveis `POSTGRES_*` e se o volume não está corrompido.

## Como rodar testes e evals

Testes unitários e de integração usam Pytest. O repositório inclui um teste E2E para avaliar a pipeline de classificação em `tests/evals/test_classification_pipeline.py`.

Passos recomendados para rodar os evals em ambiente replicável (dentro do compose):

1) Assegure que os serviços estejam up (veja acima).
2) Garanta que exista um usuário de teste com as credenciais definidas em `tests/evals/test_classification_pipeline.py` (por padrão `email@teste.com` / `teste123`). Você pode registrar via dashboard Streamlit ou via endpoint `/auth/register`.
3) Execute os testes E2E:

   docker-compose exec api pytest -m e2e -sv

O teste realiza o seguinte: carrega o arquivo `tests/evals/dataset.json`, envia comentários para a API, aguarda o processamento assíncrono (o teste dorme por ~180s) e, em seguida, consulta o banco para comparar previsões com o gabarito. O resultado impresso inclui classification_report e matriz de confusão.

Rodando testes localmente (sem Docker)

1) Crie e ative um virtualenv com Python 3.10+.
2) Instale dependências:

   pip install -r requirements.txt

3) Configure variáveis de ambiente (como acima) e execute as migrações:

   flask db migrate && flask db upgrade

4) Execute os testes:

   pytest -m e2e -sv

Observação: rodar E2E fora do Docker exige que PostgreSQL e Redis também estejam disponíveis localmente e configurados conforme `DATABASE_URL` e `CELERY_BROKER_URL`.

## Principais decisões de design

Aqui estão as decisões arquiteturais mais relevantes e por que foram adotadas:

- Assincronismo (Celery + Redis): permite ingestão massiva sem bloquear a API. A escolha reduz a latência percebida pelo cliente e facilita escalabilidade horizontal dos workers.
- Desacoplamento Frontend/Backend: Streamlit consome a API REST (Flask). Isso torna a interface rápida de desenvolver e independente da lógica de backend.
- Serviço isolado para LLM (`core/llm_service.py`): concentra prompts, parsing e chamadas ao Google Gemini num único módulo, tornando testes, substituições de modelo e manutenção mais fáceis.
- Cache simples para relatórios: o uso do Redis como cache com TTL (atualização a cada 60s) reduz a carga no banco e mantém o relatório "quase em tempo real".
- Testes E2E que cobrem a pipeline completa: validar somente funções do LLM não é suficiente; os E2E garantem que enfileiramento, workers e persistência também funcionem.

## Estrutura do repositório (resumo rápido)

- `app/` — pacote principal (API, auth, modelos, comandos, extensões)
- `core/` — serviços internos (llm_service.py, email_service.py, reporting_service.py)
- `tasks/` — lógica de processamento assíncrono (ex.: `process_comment.py`)
- `streamlit_app.py` — dashboard Streamlit
- `docker-compose.yml`, `Dockerfile` — orquestração e build
- `requirements.txt` — dependências Python
- `tests/` — testes, incluindo E2E de avaliação em `tests/evals`

## Notas operacionais e considerações finais

- Chave do Google Gemini: mantenha em segredo e não a commit no repositório.
- Migrações: o compose já executa `flask db migrate && flask db upgrade` antes de iniciar o gunicorn no serviço `api`.
- Timeout de processamento nos testes: o teste E2E usa uma espera de ~180s; ajuste conforme o desempenho da sua máquina/infra.

