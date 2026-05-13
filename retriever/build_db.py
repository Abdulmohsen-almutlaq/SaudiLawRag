import os
import glob
import json
import psycopg2
from psycopg2.extras import Json
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# --- CONFIGURATION ---
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
# Using a high-quality, free multilingual model with excellent Arabic support:
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# POSTGRES CONFIGURATION
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create the vector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Create the table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS legal_articles (
            id SERIAL PRIMARY KEY,
            doc_id VARCHAR(255) UNIQUE,
            category VARCHAR(50),
            law_name VARCHAR(255),
            hierarchy JSONB,
            title VARCHAR(255),
            content TEXT,
            embedding vector(768)
        );
    """)
    
    # We will create the index after insertion for better performance
    conn.commit()
    cur.close()
    conn.close()
    print("Database table ensures and ready.")

def load_all_documents():
    """Reads all JSON files from the data directory and extracts records."""
    documents = []
    
    for category_path in glob.glob(os.path.join(DATA_DIR, "*")):
        if not os.path.isdir(category_path):
            continue
            
        category = os.path.basename(category_path)
        
        for json_path in glob.glob(os.path.join(category_path, "*.json")):
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    records = json.load(f)
                    for idx, record in enumerate(records):
                        documents.append({
                            "doc_id": f"{category}_{os.path.basename(json_path)}_{idx}",
                            "category": category,
                            "law_name": os.path.basename(json_path).replace(".json", ""),
                            "hierarchy": record.get("hierarchy", []),
                            "title": record.get("title", ""),
                            "text": record.get("text", "")
                        })
                except Exception as e:
                    print(f"Failed to load {json_path}: {e}")
                    
    return documents

def build_vector_database():
    print("Setting up PostgreSQL schema...")
    setup_database()

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    print("Loading documents from JSON files...")
    documents = load_all_documents()
    print(f"Total structured articles found: {len(documents)}")
    
    if not documents:
        print("No documents to process. Exiting.")
        return

    # 1. Prepare texts for embedding
    texts_to_embed = []
    for doc in documents:
        # BEST PRACTICE: Injecting hierarchy into the text so the vector knows which law this belongs to
        hierarchy_str = " > ".join(doc["hierarchy"])
        full_text = f"نظام: {doc['law_name']}\nالمسار: {hierarchy_str}\nالنص: {doc['text']}"
        texts_to_embed.append(full_text)

    # 2. Encode texts into vectors
    print("Generating vector embeddings...")
    embeddings = model.encode(texts_to_embed, batch_size=32, show_progress_bar=True)
    
    # 3. Store in PostgreSQL
    print("Inserting data into PostgreSQL...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    insert_query = """
        INSERT INTO legal_articles (doc_id, category, law_name, hierarchy, title, content, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (doc_id) DO UPDATE SET
            category = EXCLUDED.category,
            law_name = EXCLUDED.law_name,
            hierarchy = EXCLUDED.hierarchy,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding;
    """
    
    for i in tqdm(range(len(documents))):
        doc = documents[i]
        emb = embeddings[i].tolist() # Convert numpy array to list for Postgres
        cur.execute(insert_query, (
            doc["doc_id"],
            doc["category"],
            doc["law_name"],
            Json(doc["hierarchy"]),
            doc["title"],
            doc["text"],
            emb
        ))
        
    # Create HNSW index for fast vector searches
    print("Creating HNSW vector index... This may take a minute.")
    cur.execute("CREATE INDEX IF NOT EXISTS legal_articles_embedding_idx ON legal_articles USING hnsw (embedding vector_cosine_ops);")
    
    conn.commit()
    cur.close()
    conn.close()
        
    print("\\n✅ Build complete! All data pushed to PostgreSQL.")

if __name__ == "__main__":
    build_vector_database()
