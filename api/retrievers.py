from typing import List
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, TextNode, QueryBundle
from retriever.search import SaudiLawRetriever

class LlamaIndexSaudiRetriever(BaseRetriever):
    """Custom Retriever for LlamaIndex bridging to the Vector Database."""
    def __init__(self, top_k: int = 3, category: str = None):
        self.retriever = SaudiLawRetriever()
        self.top_k = top_k
        self.category = category
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        # Search via existing Vector setup
        results = self.retriever.search(query_bundle.query_str, top_k=self.top_k, category=self.category)
        
        nodes = []
        for i, res in enumerate(results):
            hierarchy = " > ".join(res['hierarchy'])
            law_name = res['law_name']
            text = f"[المصدر {i+1}]: {law_name} - {hierarchy}\n{res['text']}"
            
            node = TextNode(text=text)
            # Store metadata tracking
            node.metadata = {
                "law_name": law_name,
                "hierarchy": res['hierarchy']
            }
            nodes.append(NodeWithScore(node=node, score=res['score']))
            
        return nodes
