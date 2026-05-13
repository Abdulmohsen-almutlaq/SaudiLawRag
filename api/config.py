import os
from dotenv import load_dotenv
from llama_index.llms.openai_like import OpenAILike

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def get_llm():
    """Initializes and returns the OpenAILike LLM pointing to the local Llama.cpp server."""
    from llama_index.core import Settings

    LLM_HOST = os.getenv("LLM_API_HOST", "allam-llm")
    LLM_PORT = os.getenv("LLM_PORT", "8080")
    LLM_URL = f"http://{LLM_HOST}:{LLM_PORT}/v1"

    llm = OpenAILike(
        model="ALLaM",
        api_base=LLM_URL,
        api_key="sk-no-key-required",
        is_chat_model=False,
        temperature=0.3,
        max_tokens=2048,
    )

    Settings.llm = llm
    return llm