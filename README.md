# Saudi Law RAG Assistant

```text
  ____                  _ _   _                     ____      _    ____ 
 / ___|  __ _ _   _  __| (_) | |    __ ___      __ |  _ \    / \  / ___|
 \___ \ / _` | | | |/ _` | | | |   / _` \ \ /\ / / | |_) |  / _ \ | |  _ 
  ___) | (_| | |_| | (_| | | | |__| (_| |\ V  V /  |  _ <  / ___ \| |_| |
 |____/ \__,_|\__,_|\__,_|_| |_____\__,_| \_/\_/   |_| \_\/_/   \_\____|
```

## Overview

The Saudi Law RAG Assistant is an intelligent system designed to bridge the gap between complex legal texts and accessible legal knowledge. By utilizing state-of-the-art Arabic native language models and robust vector search methodologies, the assistant retrieves specific articles from structured Saudi laws to generate accurate and context-aware responses to user queries.

## Tech Stack

This project uses the following technologies:

- Python for the backend and data pipeline
- FastAPI for the HTTP API and streaming chat endpoint
- Uvicorn as the ASGI server
- LlamaIndex for the RAG orchestration layer
- Sentence Transformers for text embeddings
- PostgreSQL with pgvector for vector storage and retrieval
- llama.cpp for running the local ALLaM model server in Docker
- Docker and Docker Compose for local development and deployment
- HTML, CSS, and JavaScript for the frontend

## Key Features

- **Natural Language Understanding**: Understands and processes Arabic legal questions seamlessly without requiring explicit domain specification.
- **Precision Retrieval**: Uses a vector database-backed retrieval flow to isolate and rank the most pertinent legal articles.
- **Accurate Citations**: Every response is meticulously backed by citations, detailing the source law, chapter, and specific article number.
- **Powered by SDAIA**: Optimized for the robust **[ALLaM-7B-Instruct](https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview)** model, ensuring high-quality formatting and Arabic reasoning.
 - **Powered by SDAIA**: Optimized for the robust **[ALLaM-7B-Instruct](https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview)** model (also available from the `humain-ai` repo: **[ALLaM-7B-Instruct-preview](https://huggingface.co/humain-ai/ALLaM-7B-Instruct-preview)**), ensuring high-quality formatting and Arabic reasoning.
- **Structured Data Pipeline**: Operates on a structured dataset systematically parsed directly from official government legal sources.

## Technical Architecture

This project implements an advanced Retrieval-Augmented Generation (RAG) pipeline:
1. **Data Ingestion**: Raw legal documents are collected, structured into JSON by law and chapter, and appropriately chunked.
2. **Indexing & Vectorization**: Legal text is converted to embeddings and stored for similarity search using PostgreSQL with pgvector.
3. **Retrieval**: Incoming user queries are transformed into vectors and matched against the stored embeddings.
4. **Generation**: The retrieved context is formatted alongside the prompt and passed to the `ALLaM-7B-Instruct` model to generate a legally sound, well-crafted Arabic response.

## Data Sources & Structure

**Primary Source**: Official [Saudi Ministry of Justice Portal](https://laws.moj.gov.sa).

Data is parsed from these repositories and converted into a highly structured JSON format to maintain the hierarchy of the legal documents:

```json
[
  {
    "law_title": "نظام العمل",
    "chapters": [
      {
        "chapter_title": "الفصل الأول",
        "articles": [
          {
            "article_number": 74,
            "text": "يجوز لأي من الطرفين إنهاء العقد خلال فترة التجربة بدون إشعار..."
          }
        ]
      }
    ]
  }
]
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.x
- Sentence Transformers and other machine learning dependencies

### Installation & Run
1. Clone the repository.
2. Ensure data mapping logic within the `./data` directory is properly populated.
3. Build the database using the retriever scripts.
4. Run the application via `docker compose up --build -d`.

## Database & .env Setup

Follow these steps to prepare your PostgreSQL database and configure the project's `.env` file.

- **Edit `.env`:** Open the project's `.env` and set the database values:

```text
DB_HOST=db          # or localhost for local Postgres
DB_PORT=5432
DB_USER=saudi_law_user
DB_PASS=saudi_law_secret_password_123
DB_NAME=saudi_law_rag
```

- **Start Postgres (Docker):**

```bash
docker compose up -d db
```

- **Create the DB user and database (psql):**

If you have `psql` available or can run it inside the Postgres container:

```bash
# enter the container (when using Docker Compose)
docker compose exec db psql -U postgres

# then in psql run:
CREATE USER saudi_law_user WITH PASSWORD 'saudi_law_secret_password_123';
CREATE DATABASE saudi_law_rag OWNER saudi_law_user;
\q
```

- **Enable `pgvector` extension:**

```bash
docker compose exec db psql -U postgres -d saudi_law_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

- **Build the project DB & load embeddings:**

The project provides a management command to create schema and populate the vector data. Run inside the `app` service:

```bash
docker compose exec app python manage.py build-db
# or locally
python manage.py build-db
```

- **Verify connection:**

```bash
docker compose exec app python -c "import os; print(os.getenv('DB_HOST'), os.getenv('DB_NAME'))"
docker compose exec app python manage.py search "متى يحق للعامل طلب إجازة؟" --top 3
```

- **Run the app:**

```bash
docker compose up --build -d
# or locally
uvicorn api.server:app --reload
```

- **Security note:** Do not commit `.env` to version control. Use strong passwords and consider secret managers for production.

## LLM Setup

This project uses a local `llama.cpp`-based model server to host the `ALLaM-7B-Instruct` model. Follow these steps to prepare and run the LLM.

- **Place the model file:** Download the model `.gguf` file and put it in the project's `llm/` folder (or change `LLM_MODEL_DIR` in `.env` to point to a different directory). Make sure the filename matches `LLM_MODEL_FILE` in `.env`.

- **Update LLM vars in `.env`:**

```text
LLM_MODEL_DIR=./llm
LLM_MODEL_FILE=ALLaM-AI_ALLaM-7B-Instruct-preview-Q6_K.gguf
LLM_PORT=8080
LLM_CONTEXT_SIZE=4096
LLM_THREADS=8
LLM_GPU_LAYERS=28
LLM_PARALLEL=2
```

- **GPU vs CPU:** The default Docker Compose service uses a CUDA-enabled image and requires an NVIDIA GPU + Docker GPU support. If you don't have a GPU, change the `allam-llm` service image in `docker-compose.yml` from `ghcr.io/ggml-org/llama.cpp:server-cuda` to a CPU image like `ghcr.io/ggml-org/llama.cpp:server`.

- **Start only the LLM service:**

```bash
docker compose up -d allam-llm
```

- **Test the LLM health endpoint:**

```bash
curl http://localhost:${LLM_PORT:-8080}/health
```

- **Example quick inference (optional):** Use the project's client or send a request to the LLM server. The repo includes `llm/ollama_client.py` and `llm/model.py` as examples of how the application connects to the local server.

- **Bring up full stack:** Once the LLM is healthy and `.env` is configured, start the full stack:

```bash
docker compose up --build -d
```

- **Notes:**
  - Ensure `LLM_MODEL_FILE` matches the exact filename in `LLM_MODEL_DIR`.
  - Model files can be large — ensure you have sufficient disk space.
  - For production, consider using a managed model service or a dedicated inference host.

## Contact

If you want to reach the project author or discuss improvements, use the following:

- Email: [abdul.almutlaq@hotmail.com](mailto:abdul.almutlaq@hotmail.com)
- LinkedIn: [abdulmohsen-almutlaq-589b01300](https://www.linkedin.com/in/abdulmohsen-almutlaq-589b01300/)

## How to Use (Interface & CLI)

Once the Docker container is actively running, you can interact with the Saudi Law RAG system in two primary ways:

### 1. Web Interface
Access the local frontend (typically at `http://localhost:8000` or depending on your docker setup) to directly ask questions in Arabic. The interface will converse with the `ALLaM` model and display retrieved legal citations visually.

### 2. Command Line Interface (CLI)
You can manage the complete RAG data pipeline and test semantic retrieval directly from your terminal using `manage.py`. When running through Docker, prefix commands with `docker compose exec app`:

```bash
# 1. Scrape latest regulations (skips existing by default)
docker compose exec app python manage.py scrape

# 2. Generate embeddings and build database
docker compose exec app python manage.py build-db

# 3. Test Retrieval Validation instantly
docker compose exec app python manage.py search "متى يحق للعامل طلب إجازة؟" --top 3
```

> **Note:** For more advanced CLI flags, forced updates, and automated scripts, see the full [CLI Command Reference](CLI.md).

---
*Disclaimer: This tool is for informational purposes and does not replace official legal counsel.*

