# Alumusic

## 1. Apresentação
Alumusic é uma aplicação composta por:
- **API (Flask)** que recebe e processa comentários, classifica e gera relatórios.
- **Front-end (Streamlit)** para visualização de dados e envio de comentários.
- **Relatório em tempo real** disponível em `/api/relatorio/semana`, com 5 gráficos e JSON associado.

O relatório semanal traz:
- Categorias mais frequentes por artista;
- Evolução diária de comentários (últimos 7 dias);
- Tags mais citadas (últimas 48 horas);
- Distribuição de status dos comentários;
- Top 5 músicas/artistas mais comentados.

## 2. Como executar o projeto (local / docker)
**Pré-requisitos**
- Docker & docker-compose (recomendado) ou Python 3.10+ (execução local)
- Banco Postgres (configurado via `docker-compose`)

**Via Docker**
```bash
git clone https://github.com/<user>/alumusic.git
cd alumusic
docker-compose up --build
# A API ficará em http://localhost:5000
# O Streamlit será exposto em http://localhost:8501 (confirma no docker-compose)
