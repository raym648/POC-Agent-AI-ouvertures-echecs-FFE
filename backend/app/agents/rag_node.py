# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/rag_node.py

import asyncio
import logging

from app.agents.state import AgentState
from app.core.config import settings
from app.rag.embedding_service import (
    embedding_service,
)
from app.rag.milvus_service import (
    milvus_service,
)


logger = logging.getLogger(__name__)


async def rag_node(
    state: AgentState,
) -> AgentState:
    """
    Node LangGraph RAG.

    Pipeline :
        opening
            -> embedding
            -> vector search Milvus

    Architecture :
    - compatible FastAPI async
    - compatible LangGraph async
    - évite le blocage event loop
    - compatible services sync via asyncio.to_thread
    """

    try:

        # =================================================
        # OPENING EXTRACTION
        # =================================================

        opening = state.get("opening")

        if not opening:

            logger.warning(
                "[RAG NODE] Missing opening in state"
            )

            return {
                **state,
                "rag_context": [],
                "error": "Missing opening",
            }

        logger.info(
            "[RAG NODE] Starting retrieval "
            f"| opening={opening}"
        )

        # =================================================
        # EMBEDDING GENERATION
        # =================================================

        # IMPORTANT:
        # SentenceTransformer.encode()
        # est sync/blocking
        #
        # -> asyncio.to_thread obligatoire

        embedding = await asyncio.to_thread(
            embedding_service.embed_text,
            opening,
        )

        if not embedding:

            logger.warning(
                "[RAG NODE] Empty embedding generated "
                f"| opening={opening}"
            )

            return {
                **state,
                "rag_context": [],
                "error": (
                    "Failed to generate embedding"
                ),
            }

        logger.info(
            "[RAG NODE] Embedding generated successfully"
        )

        # =================================================
        # VECTOR SEARCH
        # =================================================

        # IMPORTANT:
        # milvus_service.search(...)
        # utilise :
        #
        # search(query_embedding, top_k=...)
        #
        # donc kwargs requis.
        #
        # asyncio.to_thread supporte mieux
        # lambda + kwargs explicites.

        results = await asyncio.to_thread(
            lambda: milvus_service.search(
                embedding,
                top_k=settings.RAG_TOP_K,
            )
        )

        logger.info(
            "[RAG NODE] Retrieved "
            f"{len(results)} RAG documents"
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

        logger.exception(
            f"[RAG NODE] Unexpected error: {e}"
        )

        return {
            **state,
            "rag_context": [],
            "error": str(e),
        }
