from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from api.rag import SaudiLawRAG
import uvicorn
import os

app = FastAPI(title="Saudi Law RAG API", description="FastAPI wrapper for ALLaM + Vector DB RAG")

# This assumes the script is run from the project root where 'frontend' is a subdirectory.
# In a Docker context, this path is relative to the WORKDIR /app
frontend_dir = "frontend"

# Mount the 'frontend' directory to serve static files like CSS and JS
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Add CORS middleware (keeping it for flexibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_engine = SaudiLawRAG()

class ChatRequest(BaseModel):
    query: str
    top_k: int = 3

@app.get("/")
async def read_index():
    """Serves the main index.html file."""
    return FileResponse(os.path.join(frontend_dir, 'index.html'))

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Streams the LLM response back to the client word-by-word."""
    return StreamingResponse(
        rag_engine.stream_answer_api(request.query, top_k=request.top_k), 
        media_type="text/plain"
    )

def start_server():
    print("Starting FastAPI server on http://0.0.0.0:8000 ...")
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    start_server()