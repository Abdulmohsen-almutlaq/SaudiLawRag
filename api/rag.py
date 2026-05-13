from api.engines import build_expert_agent


class SaudiLawRAG:
    """Orchestrator unified RAG Engine"""

    def __init__(self):
        self.engine = build_expert_agent(top_k=3)

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
        """
        Generator for streaming over HTTP / FastAPI.

        Uses query() because build_expert_agent now returns RetrieverQueryEngine.
        RetrieverQueryEngine does not have chat().
        """
        response = self.engine.query(query)
        final_answer = str(response)

        chunk_size = 5
        for i in range(0, len(final_answer), chunk_size):
            yield final_answer[i:i + chunk_size]


if __name__ == "__main__":
    rag = SaudiLawRAG()
    rag.generate_answer("من هو المسؤول عن تنظيم المحاكم؟")