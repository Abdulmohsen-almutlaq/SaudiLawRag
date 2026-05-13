# Saudi Law RAG - Command Line Interface (CLI)

> **Central control interface for managing the Saudi Law RAG application.**
> From scraping the latest legislation to updating vector embeddings and executing test searches, `manage.py` safely and efficiently coordinates the data pipeline.

---

## 1. Execution Environment (Docker)

Since the application is configured for production using Docker, execute these commands **inside the running container**. 

> **Note:** Ensure your database and application containers are provisioned and active by using `docker compose up -d` prior to executing commands.

**The Base Command:**
```bash
docker compose exec app python manage.py [COMMAND] [OPTIONS]
```
*(If running natively outside Docker, execute `python manage.py [COMMAND]`)*

---

## 2. Command Reference 

### `scrape` | Fetch Ministry of Justice Data
Downloads statutes, regulations, and rules from the Ministry of Justice into structured JSON files. 
*Optimization: By default, the command skips records that have already been synchronized to minimize bandwidth and API execution time.*

| Goal | Exact Command |
| :--- | :--- |
| **Update only newly added laws** | `docker compose exec app python manage.py scrape` |
| **Force update all records** | `docker compose exec app python manage.py scrape --force` |
| **Update a specific record by ID** | `docker compose exec app python manage.py scrape --serial "XxHJGQ_123" --force` |

---

### `build-db` | Sync with PostgreSQL
Parses local JSON directory data, generates vector embeddings using the configured local models, and securely upserts them into the PostgreSQL (`pgvector`) instance.

> **Idempotency Guarantee**
> This command is safe to execute as frequently as needed. It relies on a deterministic update configuration. If a record remains unchanged, it resolves in place; no duplicate vectors or database anomalies are generated.

| Goal | Exact Command |
| :--- | :--- |
| **Synchronize Database with generated JSON** | `docker compose exec app python manage.py build-db` |

---

### `search` | Semantic Retrieval Validation
Instantly validate vector database accuracy directly from the terminal without engaging a web interface. The command translates query semantics into vector mathematics and retrieves the mathematically closest legal articles.

| Goal | Exact Command |
| :--- | :--- |
| **Basic Search (Standard limit: Top 3)** | `docker compose exec app python manage.py search "متى يحق للعامل طلب إجازة؟"` |
| **Expanded Search (Highest precision: Top 5)** | `docker compose exec app python manage.py search "عقوبة التزوير" --top 5` |

---

## 3. Automated Update Workflow

For configuring automated chronological synchronization protocols (e.g., cron jobs) to maintain system parity with the Ministry's data repositories, follow this sequence:

```bash
# Step 1: Force fetch the latest legislative changes from the Ministry endpoint
docker compose exec app python manage.py scrape --force

# Step 2: Push the new operational records and vectors into the AI Database
docker compose exec app python manage.py build-db
```