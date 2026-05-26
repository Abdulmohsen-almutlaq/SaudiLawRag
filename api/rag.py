from api.engines import build_expert_agent


class SaudiLawRAG:
    """Orchestrator unified RAG Engine"""

    def __init__(self):
        # Increased top_k to provide more context to the LLM
        self.engine = build_expert_agent(top_k=7)

    def generate_answer(self, query: str, top_k: int = 3):
        response = self.engine.query(query)
        full_response = str(response)

        print(full_response)
        print("\n")

        sources = []
        if hasattr(response, "source_nodes") and response.source_nodes:
            for node_score in response.source_nodes:
                metadata = node_score.node.metadata
                sources.append({
                    "law_name": metadata.get("law_name", "Unknown File"),
                    "hierarchy": metadata.get("hierarchy", []),
                    "score": node_score.score or 0.0,
                })

        return full_response, sources

    def stream_answer_api(self, query: str, top_k: int = 3):
        import json
        
        response = self.engine.query(query)
        final_answer = str(response)

        # Retrieve the rephrased query from our custom retriever wrapper
        rephrased = getattr(self.engine.retriever, "last_rephrased", query)
        
        # Send metadata first
        yield json.dumps({"type": "meta", "rephrased_query": rephrased}, ensure_ascii=False) + "\n"

        # Stream text chunks
        chunk_size = 5
        for i in range(0, len(final_answer), chunk_size):
            yield json.dumps({"type": "chunk", "text": final_answer[i:i+chunk_size]}, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    rag = SaudiLawRAG()
    rag.generate_answer("من هو المسؤول عن تنظيم المحاكم؟")