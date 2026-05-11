# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/rag_node.py

from app.agents.state import AgentState
from app.rag.embedding_service import embedding_service
from app.rag.milvus_service import milvus_service
from app.core.config import settings


def rag_node(state: AgentState) -> AgentState:
    """
    Node LangGraph RAG.

    Workflow spécialisé opening-based :
        opening
            -> embedding
                -> Milvus search

    IMPORTANT :
    - ne dépend plus de validate_fen
    - ne dépend plus de is_valid
    - ne dépend plus du workflow FEN
    """

    try:

        # =================================================
        # OPENING EXTRACTION
        # =================================================

        opening = state.get("opening")

        if not opening:

            return {
                **state,
                "rag_context": [],
                "error": "Missing opening",
            }

        # =================================================
        # EMBEDDING
        # =================================================

        embedding = embedding_service.embed_text(
            opening
        )

        # =================================================
        # VECTOR SEARCH
        # =================================================

        results = milvus_service.search(
            embedding,
            top_k=settings.RAG_TOP_K,
        )

        # =================================================
        # SUCCESS
        # =================================================

        return {
            **state,
            "rag_context": results,
            "source": "milvus",
        }

    except Exception as e:

        return {
            **state,
            "rag_context": [],
            "error": str(e),
        }
