# 🎵 AluMusic Insights - Análise de Feedback com IA

## 1. Apresentação e Resultados

**AluMusic Insights** é uma plataforma de análise de dados projetada para processar e extrair insights valiosos a partir de milhares de comentários de ouvintes. A solução foi desenvolvida como parte de um desafio técnico da Alura, com foco em **Python**, **Grandes Modelos de Linguagem (LLMs)** e arquitetura de sistemas escaláveis.

O sistema ingere comentários em lote, utiliza a API do **Google Gemini** para classificação de sentimento e extração de tags, e apresenta os resultados em um **dashboard privado** e em um **relatório público em tempo real**. Nos testes de avaliação, o sistema demonstrou uma **acurácia de 97%** na classificação de categorias em um dataset de 100 exemplos, validado por um pipeline de testes automatizado.

---

## ✨ Funcionalidades Principais

- **Ingestão Assíncrona de Dados**: Um endpoint de API REST (`/api/comentarios`) protegido por JWT que recebe lotes de comentários e os enfileira para processamento em background.
- **Processamento com IA**: Utilização do **Celery** e **Redis** para gerenciar uma fila de tarefas, onde workers processam cada comentário individualmente, chamando a API do **Google Gemini** (`gemini-1.5-flash-latest`).
- **Dashboard Privado Interativo**: Uma interface moderna construída com **Streamlit**, protegida por login, que permite buscar, filtrar, visualizar o histórico de classificações e exportar os dados em formatos CSV e JSON.
- **Relatório Público em Tempo Real**: Uma página pública que exibe 6 visualizações de dados com os insights mais recentes, com um sistema de cache no Redis que garante que os dados sejam atualizados a cada 60 segundos.
- **Avaliação de Performance da IA**: Um fluxo de avaliação de ponta a ponta, automatizado com **Pytest**, que mede a qualidade da classificação do modelo.

---

## 🏛️ Arquitetura e Estrutura

O projeto é organizado de forma modular para separar as responsabilidades e facilitar a manutenção. O sistema é composto por serviços containerizados e orquestrados com **Docker Compose**, seguindo uma arquitetura desacoplada e escalável.

```mermaid
graph TD
    subgraph "Cliente Externo / Testes"
        A[Script de Carga / Pytest]
    end
    subgraph "Navegador do Usuário"
        B[Dashboard Streamlit]
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
    A -- JSON em lote c/ JWT --> D
    B -- Requisições REST c/ JWT --> D
    D -- Enfileira Tarefas --> G
    D -- Salva/Lê Dados --> F
    D -- Lê/Escreve Cache do Relatório --> G
    E -- Pega Tarefas --> G
    E -- Chama API --> H
    E -- Salva Resultados --> F
```

---

## 🛠️ Tech Stack

- **Linguagem Principal**: Python (3.10+)
- **Backend**: Flask, SQLAlchemy
- **Frontend (Dashboard)**: Streamlit
- **Banco de Dados**: PostgreSQL
- **Fila e Cache**: Celery, Redis
- **Inteligência Artificial**: Google Gemini (via `google-generativeai`)
- **Visualização de Dados**: Pandas, Matplotlib
- **Testes e Métricas**: Pytest, Scikit-learn
- **Containerização**: Docker, Docker Compose

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos

- **Docker**
- **Docker Compose**

### 2. Configuração

Clone o repositório e entre na branch correta:

```bash
git clone https://github.com/AnaBeatriz-Carvalho/alumusic.git
cd alumusic
```

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Abra o arquivo `.env` e preencha as variáveis, especialmente a sua `GOOGLE_API_KEY`.

### 3. Execução

Com o Docker em execução, suba todos os serviços. O banco de dados será criado e as migrações serão aplicadas automaticamente:

```bash
docker-compose up --build -d
```

Acesse o dashboard em [http://localhost:8501](http://localhost:8501) no seu navegador.

### 4. Avaliação e Métricas

O projeto inclui um fluxo de avaliação automatizado para medir a performance do modelo de classificação.

#### Comando de Execução

Para rodar os testes e gerar o relatório de métricas, execute o seguinte comando único:

```bash
docker-compose exec api pytest -m e2e -sv
```

#### Resultado Esperado

O comando irá orquestrar todo o fluxo de teste e, ao final, imprimir um relatório detalhado no console, similar a este:

```
============================================================
 Relatório Final de Avaliação da Pipeline de Classificação =
============================================================

>>> Métricas de Classificação de Categoria:
              precision    recall  f1-score   support
     CRÍTICA       1.00      0.97      0.98        31
      DÚVIDA       1.00      0.95      0.97        20
...
    accuracy                           0.97        98

>>> Matriz de Confusão (Real vs. Previsto):
               Prev: CRÍTICA  Prev: DÚVIDA ...
Real: CRÍTICA             30             0
Real: DÚVIDA               0            19

>>> Métricas de Extração de Tags:
Acurácia de Tags (correspondência exata): 10.20%
```

---

## ⚖️ Principais Decisões de Design

- **API Assíncrona com Celery/Redis**: A escolha de uma arquitetura assíncrona foi fundamental para atender ao requisito de processamento de grandes lotes. A API pode aceitar centenas de comentários instantaneamente, enfileirando o trabalho pesado para os workers.
- **Frontend Desacoplado com Streamlit**: Streamlit foi escolhido pela sua capacidade de criar rapidamente dashboards de dados interativos. A comunicação via API REST mantém o frontend e o backend desacoplados, e o uso de um arquivo `.css` externo permitiu a criação de um design moderno e customizado.
- **Cache para Relatório em Tempo Real**: Optou-se por uma estratégia de cache-on-demand na rota pública. A própria API gera o relatório se o cache do Redis estiver expirado (60s). Isso simplifica a arquitetura (removendo a necessidade do Celery Beat para esta função), mas ainda cumpre o requisito de atualização.
- **Serviço de LLM Isolado e Refinado**: Toda a lógica de interação com o Gemini, incluindo a engenharia de prompt, foi centralizada no módulo `llm_service.py`. O prompt foi aprimorado com técnicas de "Few-Shot Prompting" para aumentar a consistência e a acurácia na extração de tags.
- **Testes de Ponta a Ponta (E2E) com Pytest**: O fluxo de avaliação foi desenhado para validar toda a pipeline: da ingestão na API, passando pela fila do Celery, o processamento do worker e a persistência no banco, fornecendo métricas realistas.

---

## 🗺️ Endpoints Principais da API

- **POST** `/auth/register`: Registra um novo usuário da equipe.
- **POST** `/auth/login`: Autentica um usuário e retorna um token JWT.
- **POST** `/api/comentarios`: Recebe um lote de comentários para processamento.
- **GET** `/api/comentarios`: Lista os comentários processados, com suporte a filtros.
- **GET** `/api/comentarios/<uuid>`: Retorna os detalhes de um comentário específico.
- **GET** `/api/relatorio/semana`: Rota pública que retorna os dados do relatório em tempo real.

---

## 📞 Contato

**Ana Beatriz Carvalho Oliveira**  
📧 beatriz.carvalho0804@gmail.com