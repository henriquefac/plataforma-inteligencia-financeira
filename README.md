# Backend (Inteligência Financeira)

Este é o motor da plataforma de Inteligência Financeira, construído para processar dados transacionais, calcular métricas de negócio e fornecer insights baseados em IA através de uma abordagem de Agente Analítico.

## Decisões Técnicas e Arquitetura

### Por que FastAPI?
A escolha do **FastAPI** foi fundamentada em:
- **Alta Performance**: Um dos frameworks Python mais rápidos, essencial para processamento de dados.
- **Assincronismo Nativo**: Permite lidar com múltiplas chamadas de LLM (que são demoradas) sem bloquear o servidor.
- **Tipagem com Pydantic**: Garante a integridade dos dados desde a entrada da API até o processamento interno.
- **Documentação Automática**: Swagger/OpenAPI gerado automaticamente em `/docs`.

### Agente Analítico vs. RAG Tradicional
Embora o projeto tenha explorado o uso de RAG (Retrieval-Augmented Generation) com **ChromaDB**, optei por evoluir para um **Agente Analítico**.
- **O Problema do RAG**: Em dados financeiros, a busca semântica por proximidade vetorial muitas vezes falha em trazer números exatos ou realizar agregações (ex: "Qual a soma total de inadimplência?").
- **A Solução (Agente)**: O sistema agora utiliza o LLM para atuar como um **Analista de Dados**. Ele interpreta a pergunta do usuário, entende o esquema do banco de dados e gera queries **Pandas** precisas que são executadas diretamente sobre o dataset. Foi observado uma melhora muito grande na precisão das respostas.

### Sistema de Caching
Devido à natureza do Streamlit (frontend) de recarregar a página a cada interação, implementei um sistema de **SimpleCache** no backend:
- **TTL (Time To Live)**: Resultados de processamentos custosos (como insights de IA e queries analíticas) são cacheados em memória por um tempo determinado.
- **Eficiência**: Reduz drasticamente os custos de API de LLM e o tempo de resposta para o usuário final.

## Tecnologias Principais

- **FastAPI**: Framework web.
- **Pandas/PyArrow**: Processamento de dados e armazenamento em csv.
- **LlamaIndex**: Orquestração da lógica do agente e integração com LLMs.
- **Ollama & OpenRouter**: Provedores de modelos de linguagem (IA).
- **Pydantic Settings**: Gestão de configurações via `.env`.

## Estrutura de Pastas

- `app/api`: Definição das rotas e endpoints.
- `app/core`: Configurações centrais (LLM, Cache, Segurança).
- `app/domain`: Modelos de dados e entidades de negócio.
- `app/service`: Lógica de negócio (Cálculo de métricas, Agente Analítico, Ingestão).

## Instalação e Execução

### Pré-requisitos
- Python 3.12+
- Gerenciador de pacotes `uv`.

### Passo a Passo
1. Instale as dependências:
   ```bash
   uv sync
   ```
2. Configure o arquivo `.env` (use o `.env.example` da raiz do projeto como base).
3. Inicie o servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

A API estará disponível em `http://localhost:8000`.
