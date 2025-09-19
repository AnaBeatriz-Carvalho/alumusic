# 🎵 AluMusic Insights

## Sobre o Projeto

**AluMusic Insights** é uma plataforma de análise de dados projetada para processar e extrair insights valiosos a partir de milhares de comentários de ouvintes. A solução foi desenvolvida como parte de um desafio técnico para a Alura, com foco em Python, Grandes Modelos de Linguagem (LLMs) e arquitetura de sistemas escaláveis.

O serviço ingere comentários em lote, utiliza a API do Google Gemini para realizar uma classificação de sentimento e extração de tags, e apresenta os resultados em um dashboard privado para análise e em um relatório público em tempo real.

## ✨ Funcionalidades Principais

* **Ingestão Assíncrona de Dados:** Um endpoint de API REST (`/api/comentarios`) protegido por JWT que recebe lotes de comentários e os enfileira para processamento em background, garantindo alta disponibilidade e resposta rápida ao cliente.
* **Processamento com IA:** Utilização do Celery e Redis para gerenciar uma fila de tarefas, onde workers processam cada comentário individualmente, chamando a API do Google Gemini para classificação e extração de tags.
* **Dashboard Privado Interativo:** Uma interface construída com Streamlit para a equipe de curadoria, protegida por login, que permite buscar, filtrar, visualizar o histórico de classificações e exportar os dados em formatos CSV e JSON.
* **Relatório Público em Tempo Real:** Uma página pública que exibe 5 visualizações de dados com os insights mais recentes, com um sistema de cache no Redis que garante que os dados sejam atualizados a cada 60 segundos sem sobrecarregar o banco de dados.
* **Avaliação de Performance da IA:** Um fluxo de avaliação de ponta a ponta, automatizado com Pytest, que mede a qualidade da classificação do modelo através de métricas como Acurácia, Precisão, Recall, F1-Score e uma Matriz de Confusão.

## 🏛️ Arquitetura

O sistema é composto por microsserviços containerizados e orquestrados com Docker Compose, seguindo uma arquitetura desacoplada e escalável.

```mermaid
graph TD
    subgraph "Cliente Externo"
        A[Script de Carga / Outro Serviço]
    end

    subgraph "Navegador do Usuário"
        B[Dashboard Streamlit]
        C[Relatório Público]
    end

    subgraph "Infraestrutura Docker"
        D[API Flask]
        E[Worker Celery]
        F[Banco de Dados PostgreSQL]
        G[Fila e Cache Redis]
    end

    subgraph "Serviço Externo"
        H[API Google Gemini]
    end

    A -- JSON em lote --> D
    B -- Requisições c/ JWT --> D
    C -- Requisições públicas --> D

    D -- Enfileira Tarefas --> G
    D -- Salva/Lê Dados --> F
    D -- Lê Cache do Relatório --> G

    E -- Pega Tarefas --> G
    E -- Chama API --> H
    E -- Salva Resultados --> F
```

## 🛠️ Tech Stack

* **Backend:** Flask, SQLAlchemy
* **Frontend (Dashboard):** Streamlit
* **Banco de Dados:** PostgreSQL
* **Fila e Cache:** Celery, Redis
* **Inteligência Artificial:** Google Gemini (via `google-generativeai`)
* **Visualização de Dados:** Pandas, Matplotlib
* **Testes e Métricas:** Pytest, Scikit-learn
* **Containerização:** Docker, Docker Compose

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e rodar a aplicação localmente.

### Pré-requisitos

* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Configuração do Ambiente

1.  Clone este repositório:
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd nome-do-repositorio
    ```

2.  Crie uma cópia do arquivo de exemplo de variáveis de ambiente:
    ```bash
    cp .env.example .env
    ```

3.  Abra o arquivo `.env` e preencha as variáveis. A mais importante é a sua chave da API do Google Gemini:
    ```env
    # Chave secreta para o Flask e JWT
    SECRET_KEY="uma_chave_super_secreta_aqui"
    JWT_SECRET_KEY="outra_chave_super_secreta_aqui"

    # Credenciais do Banco de Dados PostgreSQL
    POSTGRES_USER=alumusic
    POSTGRES_PASSWORD=alumusic
    POSTGRES_DB=alumusic

    # URL de conexão para a aplicação (não altere o host 'alumusic')
    DATABASE_URL=postgresql://alumusic:alumusic@alumusic:5432/alumusic

    # URL do Broker para o Celery (não altere o host 'redis')
    CELERY_BROKER_URL=redis://redis:6379/0
    CELERY_RESULT_BACKEND=redis://redis:6379/0

    # Chave da API do Google Gemini
    GOOGLE_API_KEY="AIzaSy..."
    ```

### 2. Executando a Aplicação

Com o Docker em execução, suba todos os serviços com um único comando:
```bash
docker-compose up --build -d
```
O comando `--build` é importante na primeira vez para construir a imagem Docker. O `-d` executa os contêineres em segundo plano.

### 3. Acessando e Usando a Aplicação

* **Dashboard Privado:** Acesse `http://localhost:8501` no seu navegador.
    * Use a aba "Registrar" na barra lateral para criar uma conta para a equipe de curadoria.
    * Após o registro, faça o login para acessar o dashboard de análise.

* **Relatório Público:** A aba "Relatório Público" pode ser acessada sem login e é atualizada a cada 60 segundos.

---
### 4. Avaliação e Métricas

O projeto inclui um fluxo de avaliação automatizado para medir a performance do modelo de classificação de ponta a ponta.

#### Comando de Execução

Para rodar os testes e gerar o relatório de métricas, execute o seguinte comando único na raiz do projeto:
```bash
docker-compose exec api pytest -m e2e -sv
```
*(**Nota:** Certifique-se de que o usuário de teste definido em `tests/evals/test_classification_pipeline.py` já foi registrado na aplicação.)*

#### O Que o Comando Faz

Este comando orquestra o seguinte fluxo:
1.  Carrega um dataset de teste ("gabarito") a partir de `tests/evals/dataset.json`.
2.  Envia os dados para a API e aguarda o processamento em background pelos workers do Celery.
3.  Busca os resultados processados diretamente do banco de dados.
4.  Compara os resultados da IA com o gabarito.
5.  Imprime um relatório detalhado no console com métricas de **Acurácia, Precisão, Recall, F1-Score** e uma **Matriz de Confusão**.

---
### ⚖️ Principais Decisões de Design

* **API Assíncrona com Celery/Redis:** A escolha de uma arquitetura assíncrona foi fundamental для atender ao requisito de processamento de grandes lotes sem degradar a experiência do cliente. A API pode aceitar centenas de comentários instantaneamente, enfileirando o trabalho pesado para os workers.
* **Frontend Desacoplado com Streamlit:** Streamlit foi escolhido pela sua capacidade de criar rapidamente dashboards de dados interativos e visualmente ricos, ideal para o público-alvo da ferramenta (equipe de curadoria). A comunicação via API REST mantém o frontend e o backend desacoplados.
* **Cache para Relatório em Tempo Real:** Optou-se por uma estratégia de cache-on-demand na rota pública. Isso simplifica a arquitetura, mas ainda cumpre o requisito de atualização de 60 segundos, garantindo performance e baixo custo de consulta.
* **Serviço de LLM Isolado (`llm_service.py`):** Toda a lógica de interação com o Gemini, incluindo a engenharia de prompt, foi centralizada em um único módulo. Isso torna o sistema mais modular, fácil de testar e permite trocar o modelo de IA no futuro com impacto mínimo no resto da aplicação.
* **Testes de Ponta a Ponta (E2E) com Pytest:** O fluxo de avaliação foi desenhado não apenas para testar a função de classificação isoladamente, mas para validar toda a pipeline: da ingestão na API, passando pela fila do Celery, o processamento do worker e a persistência no banco. Isso garante que o sistema funciona como um todo.

---
### 🔮 Próximos Passos (Não Implementados)

* **Resumo semanal por e-mail:** Implementar uma tarefa agendada (com Celery Beat) para, ao final da semana, usar a LLM para gerar um resumo das tendências e enviar por e-mail.
* **Mini Insight-Q&A:** Adicionar a rota autenticada `/insights/perguntar` para permitir que stakeholders façam perguntas em linguagem natural sobre os dados recentes.