from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import Settings
from llama_index.core.prompts import PromptTemplate

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


def build_expert_agent(top_k: int = 3) -> RetrieverQueryEngine:
    llm = get_llm()
    Settings.llm = llm

    return RetrieverQueryEngine.from_args(
        retriever=LlamaIndexSaudiRetriever(top_k=top_k),
        llm=llm,
        text_qa_template=QA_PROMPT,
    )