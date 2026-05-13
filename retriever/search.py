import os
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# POSTGRES CONFIGURATION
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

class SaudiLawRetriever:
    def __init__(self):
        print("Loading embedding model...")
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            
    def get_db_connection(self):
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
            
    def search(self, query, top_k=5, category=None):
        # Embed the Arabic search query
        query_vector = self.model.encode([query])[0].tolist()
        
        # Connect to Postgres
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Search using pgvector's cosine distance operator (<=>)
        if category:
            search_query = """
                SELECT 
                    category,
                    law_name,
                    hierarchy,
                    title,
                    content,
                    1 - (embedding <=> %s::vector) AS similarity_score
                FROM legal_articles
                WHERE category = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            cur.execute(search_query, (query_vector, category, query_vector, top_k))
        else:
            search_query = """
                SELECT 
                    category,
                    law_name,
                    hierarchy,
                    title,
                    content,
                    1 - (embedding <=> %s::vector) AS similarity_score
                FROM legal_articles
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            cur.execute(search_query, (query_vector, query_vector, top_k))
        
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Format results into a list of dicts
        formatted_results = []
        for row in results:
            formatted_results.append({
                "category": row[0],
                "law_name": row[1],
                "hierarchy": row[2],
                "title": row[3],
                "text": row[4],
                "score": float(row[5])
            })
            
        return formatted_results

if __name__ == "__main__":
    # Test the retriever
    retriever = SaudiLawRetriever()
    
    question = "ما هي شروط تملك المستثمر الأجنبي للعقار في السعودية؟"
    print(f"\\nQuestion: {question}\\n")
    
    try:
        results = retriever.search(question, top_k=3)
        
        for i, res in enumerate(results):
            print(f"--- Result {i+1} ---")
            print(f"Law: {res['law_name']}")
            print(f"Hierarchy: {' > '.join(res['hierarchy'])}")
            print(f"Article Text: {res['text'][:200]}...") # Print first 200 chars
            print(f"Similarity Score: {res['score']:.4f}")
            print()
    except psycopg2.OperationalError:
        print("Database not running! Make sure to start the PostgreSQL Docker container.")
