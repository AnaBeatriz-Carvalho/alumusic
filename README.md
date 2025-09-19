# 🎵 AluMusic Insights



## Apresentação e resultados do case

AluMusic Insights foi desenvolvido para demonstrar uma pipeline prática e escalável para processamento de feedback de ouvintes. O case mostra como integrar LLMs na análise de texto, mantendo confiabilidade operacional com processamento assíncrono.

Resultados esperados / demonstrados:
- Classificação automática de comentários em categorias (ELOGIO, CRÍTICA, SUGESTÃO, DÚVIDA, SPAM).
- Extração de tags relevantes por comentário (tópicos/assuntos).
- Persistência de comentários e histórico consultável via dashboard e API.
- Processamento assíncrono (Celery) permitindo ingestão em lote sem bloquear a API.
- Geração de resumos semanais via LLM e persistência do resumo (envio por email foi removido conforme pedido do usuário).

---

## Funcionalidades principais
- API REST (Flask) para registro/login, ingestão de comentários e endpoint de análise por LLM (`POST /api/llm/analyze`).
- Dashboard Streamlit privado para curadores, com upload (.csv/.json) e envio de texto bruto para análise por LLM.
- Histórico de comentários com filtros, exportação CSV/JSON, e exibição de tags e classificação.
- Workers Celery que processam comentários individualmente e atualizam a base de dados.
- Tarefa agendada (`weekly_summary_task`) para gerar e persistir sumários semanais usando o LLM; emails automáticos foram removidos — os resumos ficam disponíveis via API/admin.

---

## Pré-requisitos
- Docker Desktop + Docker Compose (recomendado)
-  Python 3.10+ com PostgreSQL e Redis localmente instalados (opcional)

Recomendado (para Windows PowerShell):
- PowerShell 7+ (opcional, mas mais moderno)
- Suficiente memória/CPU para rodar containers (mínimo 2 CPUs e 4GB RAM para desenvolvimento)

---

## Execução com Docker Compose (recomendado)
Abaixo estão instruções orientadas para Windows PowerShell.

1) Clone o repositório

```powershell
git clone <URL_DO_REPOSITORIO>
cd alumusic
```

2) Crie um arquivo `.env` na raiz com as variáveis necessárias (exemplo mínimo):

```ini
SECRET_KEY="uma_chave_secreta"
JWT_SECRET_KEY="uma_chave_jwt"
POSTGRES_USER=alumusic
POSTGRES_PASSWORD=alumusic
POSTGRES_DB=alumusic
DATABASE_URL=postgresql://alumusic:alumusic@alumusic:5432/alumusic
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
GOOGLE_API_KEY="SUA_CHAVE_GOOGLE_GEMINI"
```

---

3) Suba os serviços com Docker Compose

No PowerShell (na pasta do projeto):

```powershell
docker-compose up --build -d
```

Serviços principais (nomeados no compose):
- `api` — Flask + Gunicorn (API REST)
- `worker` — Celery worker
- `beat` — Celery Beat (scheduler para weekly_summary_task)
- `streamlit` — Streamlit dashboard (porta 8501)
- `alumusic` / `postgres` — PostgreSQL
- `redis` — Redis (broker/result backend)

4) Acessos
- Streamlit (dashboard privado): http://localhost:8501
- API (externa/local): dependendo do compose, o container pode mapear porta 5001 -> 5000; verifique `docker-compose.yml`.

5) Logs e comandos úteis (PowerShell)

Ver logs do API:

```powershell
docker-compose logs -f api
```

Entrar no shell do serviço (ex.: para rodar migrações manualmente):

```powershell
docker-compose exec api bash
# dentro do container
flask db upgrade
```

---

## Execução local (sem Docker) — breve
1) Crie virtualenv e instale dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Configure variáveis de ambiente (ou use `.env` loader) e garanta PostgreSQL + Redis rodando localmente.
3) Rode migrações:

```powershell
flask db upgrade
```

4) Inicie a API e o worker separadamente (em terminais distintos):

```powershell
# API
flask run --host=0.0.0.0 --port=5000
# Worker (novo terminal)
celery -A celery_app.celery worker --loglevel=info
# Beat (opcional)
celery -A celery_app.celery beat --loglevel=info
```

---

## Tests & Evals
O projeto contém testes pytest. Em particular há um E2E de classificação em `tests/evals/test_classification_pipeline.py`.

Rodando os testes dentro do container `api` (compose):

```powershell
docker-compose exec api pytest -q
# ou apenas os evals

```

Observações sobre o teste E2E:
- O E2E carrega `tests/evals/dataset.json` e envia comentários para a API, aguarda processamento e valida classificações.
- Os testes E2E podem esperar alguns minutos (o tempo depende do processamento dos workers).

Rodando testes localmente:

```powershell
# com venv ativado e serviços DB/Redis locais
pytest -q
```

---

## Endpoints importantes (resumo)
- POST /auth/register — registrar novo usuário
- POST /auth/login — autenticar e receber JWT
- GET /api/comentarios — listar comentários com filtros
- POST /api/llm/analyze — enviar arquivo (.csv/.json) ou texto para análise por LLM
- GET /api/tasks/<task_id> — checar status de uma tarefa enfileirada (quando aplicável)
- GET /admin/weekly_summary/latest — buscar o último WeeklySummary persistido (JWT necessário)

---

## Principais decisões de design
1. Assincronismo com Celery + Redis
- Razão: processamento de centenas/milhares de comentários deve ser feito fora do request cycle.
- Como: API persiste Comentario com status PENDENTE e enfileira task por comentário. Workers processam e atualizam o registro.

2. Serviço LLM centralizado (`app/core/llm_service.py`)
- Razão: separa prompts, chamadas à API do provedor (Gemini) e parsing; facilita troca de modelo no futuro.

3. Arquitetura simples de front/back
- Streamlit como frontend independente que consome a API, reduz acoplamento e facilita deploy independente.

4. Migrações e versionamento (Alembic)
- Notas: as revisões de migration devem ter ids curtas (varchar(32) no alembic_version). Evite nomes muito longos que causem erros no banco.


---

## Troubleshooting comum
- Erro Alembic: "Can't locate revision..."
  - Certifique-se de que o container de migrate/construa a imagem depois de atualizar as migrations: `docker-compose build --no-cache migrate && docker-compose up -d migrate` ou apenas `docker-compose up --build -d`.
- Erro DataError: value too long for type character varying(32)
  - Renomeie/recrie a revisão para uma id curta (<=32 chars).
- Streamlit: depois de enviar um arquivo, o uploader não some
  - A interface já foi ajustada para limpar o uploader usando uma chave dinâmica de widget; atualize a página/clear cache do browser se necessário.

---

## Observações operacionais
- As credenciais da API LLM (Google Gemini) devem ser adicionadas via `GOOGLE_API_KEY` como variável de ambiente.

---


## Contato
Se precisar de ajuda para rodar o projeto ou adaptar para produção, descreva o ambiente (local/Docker/Kubernetes) e os erros/logs que surgirem.

---

Arquivo gerado automaticamente: README.md — atualizado para refletir o estado atual do projeto (branch: alumusic-refactor).

