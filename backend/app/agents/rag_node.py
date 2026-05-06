# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/rag_node.py

from app.agents.state import AgentState
from app.rag.embedding_service import embedding_service
from app.rag.milvus_service import milvus_service
from app.core.config import settings


def rag_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    try:
        if state.get("moves"):
            query = " ".join([m.get("san", "") for m in state["moves"][:3]])
        elif state.get("evaluation"):
            query = f"chess analysis {state['fen']}"
        else:
            query = state["fen"]

        embedding = embedding_service.embed_text(query)

        results = milvus_service.search(
            embedding,
            top_k=settings.RAG_TOP_K,
        )

        return {
            **state,
            "rag_context": results,
        }

    except Exception as e:
        return {
            **state,
            "rag_context": [],
            "error": str(e),
        }
