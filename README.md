# Saudi Law RAG Assistant

```text
  ____                  _ _   _                     ____      _    ____ 
 / ___|  __ _ _   _  __| (_) | |    __ ___      __ |  _ \    / \  / ___|
 \___ \ / _` | | | |/ _` | | | |   / _` \ \ /\ / / | |_) |  / _ \ | |  _ 
  ___) | (_| | |_| | (_| | | | |__| (_| |\ V  V /  |  _ <  / ___ \| |_| |
 |____/ \__,_|\__,_|\__,_|_| |_____\__,_| \_/\_/   |_| \_\/_/   \_\____|
```

## 📖 Overview

The Saudi Law RAG Assistant is an intelligent system designed to bridge the gap between complex legal texts and accessible legal knowledge. By utilizing state-of-the-art Arabic native language models and robust vector search methodologies, the assistant retrieves specific articles from structured Saudi laws to generate accurate and context-aware responses to user queries.

## ✨ Key Features

- **Natural Language Understanding**: Understands and processes Arabic legal questions seamlessly without requiring explicit domain specification.
- **Precision Retrieval**: Employs FAISS (Facebook AI Similarity Search) to accurately isolate and locate the most pertinent legal articles.
- **Accurate Citations**: Every response is meticulously backed by citations, detailing the source law, chapter, and specific article number.
- **Powered by SDAIA**: Optimized for the robust **[ALLaM-7B-Instruct](https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview)** model, ensuring high-quality formatting and Arabic reasoning.
- **Structured Data Pipeline**: Operates on a structured dataset systematically parsed directly from official government legal sources.

## 🏗️ Technical Architecture

This project implements an advanced Retrieval-Augmented Generation (RAG) pipeline:
1. **Data Ingestion**: Raw legal documents are collected, structured into JSON by law and chapter, and appropriately chunked.
2. **Indexing & Vectorization**: Legal text is converted to embeddings and indexed utilizing FAISS for low-latency searches.
3. **Retrieval**: Incoming user queries are transformed into vectors to query the FAISS index.
4. **Generation**: The retrieved context is formatted alongside the prompt and passed to the `ALLaM-7B-Instruct` model to generate a legally sound, well-crafted Arabic response.

## 🗄️ Data Sources & Structure

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

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.x
- FAISS and relative ML dependencies

### Installation & Run
1. Clone the repository.
2. Ensure data mapping logic within the `./data` directory is properly populated.
3. Build the database using the retriever scripts.
4. Run the application via `docker compose up --build -d`.

## 💻 How to Use (Interface & CLI)

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

