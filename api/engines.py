from typing import List
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import Settings
from llama_index.core.prompts import PromptTemplate
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle

from api.config import get_llm
from api.retrievers import LlamaIndexSaudiRetriever


QA_PROMPT = PromptTemplate(
    """
أنت مساعد قانوني ذكي متخصص في الأنظمة والقوانين السعودية.

أجب على سؤال المستخدم بناءً على السياق القانوني المرفق فقط.

التعليمات:
- أجب باللغة العربية فقط.
- لا تكتب Thought أو Action أو Observation أو Answer.
- لا تشرح طريقة تفكيرك الداخلية.
- إذا لم يحتوِ السياق على الإجابة، قل بوضوح:
  "لا يحتوي السياق المتاح على معلومات كافية للإجابة عن هذا السؤال."
- قدم إجابة مهنية ودقيقة ومنظمة.

السياق القانوني:
---------------------
{context_str}
---------------------

سؤال المستخدم:
{query_str}

الإجابة:
"""
)


REWRITE_PROMPT = PromptTemplate(
    "أنت مستشار قانوني سعودي. مهمتك تحويل قصة أو سؤال المستخدم إلى 'استعلام بحث قانوني' يحافظ على تفاصيل الوقائع المذكورة ويضيف إليها المصطلحات القانونية المناسبة للبحث في الأنظمة السعودية.\n"
    "التعليمات:\n"
    "- استخرج أهم وقائع القصة (مثل: حادث مروري، مشادة كلامية، اعتداء جسدي، دفاع شرعي، دعوى كيدية).\n"
    "- استخدم مصطلحات قانونية دقيقة (مثل: الحق الخاص، الحق العام، الإجراءات الجزائية، الاختصاص).\n"
    "- لا تقم بحذف تفاصيل الأحداث الجوهرية لأنها مهمة للبحث.\n"
    "- لا تقم بالإجابة على السؤال، فقط اكتب الاستعلام.\n"
    "- اكتب الاستعلام المعاد صياغته فقط في فقرة واحدة متصلة بدون أي مقدمات أو شروحات.\n\n"
    "السؤال الأصلي: {query_str}\n\n"
    "استعلام البحث المعدل:"
)


class RephrasingRetriever(BaseRetriever):
    """A wrapper retriever that rephrases the query using an LLM before fetching documents."""
    
    def __init__(self, base_retriever: BaseRetriever, llm):
        self.base_retriever = base_retriever
        self.llm = llm
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        # 1. Rephrase the query
        formatted_prompt = REWRITE_PROMPT.format(query_str=query_bundle.query_str)
        response = self.llm.complete(formatted_prompt)
        rephrased_text = str(response).strip()
        
        # Save it to instance so the orchestrator can read it
        self.last_rephrased = rephrased_text
        
        print(f"\n[Agentic Rephraser] Original Query : {query_bundle.query_str}")
        print(f"[Agentic Rephraser] Rephrased Query: {rephrased_text}\n")
        
        # 2. Update the query bundle with the new string
        new_bundle = QueryBundle(query_str=rephrased_text)
        
        # 3. Retrieve using the base retriever
        return self.base_retriever.retrieve(new_bundle)
7

def build_expert_agent(top_k: int = 3) -> RetrieverQueryEngine:
    llm = get_llm()
    Settings.llm = llm

    # Base retriever
    base_retriever = LlamaIndexSaudiRetriever(top_k=top_k)
    
    # Wrap with our agentic rephraser
    agentic_retriever = RephrasingRetriever(base_retriever=base_retriever, llm=llm)

    return RetrieverQueryEngine.from_args(
        retriever=agentic_retriever,
        llm=llm,
        text_qa_template=QA_PROMPT,
    )