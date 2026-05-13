# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/video_node.py

import asyncio
import logging

from typing import Any, Dict, List

from app.services.lichess_enrichment_service import (
    LichessEnrichmentService,
)
from app.services.video_reranker import rerank_videos
from app.services.youtube_cache_service import (
    YouTubeCacheService,
)
from app.services.youtube_service import YouTubeService


logger = logging.getLogger(__name__)


async def video_retriever_node(
    state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Node LangGraph de récupération de vidéos pédagogiques.

    Architecture :
    - async-compatible
    - non bloquant pour FastAPI
    - compatible LangGraph
    - résilient aux erreurs externes

    Pipeline :
        opening
            -> cache MongoDB
            -> enrichissement requête
            -> recherche YouTube
            -> reranking pédagogique
    """

    try:

        opening = state.get("opening")
        moves = state.get("moves", [])
        evaluation = state.get("evaluation")

        logger.info(
            f"[VIDEO NODE] Starting retrieval | opening={opening}"
        )

        cache_service = YouTubeCacheService()

        # =================================================
        # 1. CACHE LOOKUP
        # =================================================

        if opening:

            cached_videos = await asyncio.to_thread(
                cache_service.get,
                opening,
            )

            if cached_videos:

                logger.info(
                    f"[VIDEO NODE] Cache hit | opening={opening}"
                )

                return {
                    **state,
                    "videos": cached_videos,
                }

        # =================================================
        # 2. QUERY GENERATION
        # =================================================

        query: str | None = None

        # ---------------------------------------------
        # Opening enrichment
        # ---------------------------------------------

        if opening:

            enrichment_service = (
                LichessEnrichmentService()
            )

            query = await asyncio.to_thread(
                enrichment_service.enrich_opening,
                opening,
            )

        # ---------------------------------------------
        # Moves fallback
        # ---------------------------------------------

        elif moves:

            # IMPORTANT:
            # Lichess retourne :
            # { "move": "e2e4" }
            # et NON "san"

            moves_text = " ".join(
                [
                    move.get("move", "")
                    for move in moves[:3]
                    if move.get("move")
                ]
            )

            query = (
                f"chess opening {moves_text} explanation"
            )

        # ---------------------------------------------
        # Evaluation fallback
        # ---------------------------------------------

        elif evaluation:

            query = (
                "chess middlegame strategy "
                "plan explanation"
            )

        # ---------------------------------------------
        # No usable context
        # ---------------------------------------------

        else:

            logger.warning(
                "[VIDEO NODE] No usable retrieval context"
            )

            return {
                **state,
                "videos": [],
            }

        logger.info(
            f"[VIDEO NODE] Generated query={query}"
        )

        # =================================================
        # 3. YOUTUBE SEARCH
        # =================================================

        youtube_service = YouTubeService()

        # IMPORTANT:
        # search_videos est sync/blocking
        # -> asyncio.to_thread obligatoire

        videos = await asyncio.to_thread(
            lambda: youtube_service.search_videos(
                query=query,
                opening=opening,
            )
        )

        videos_dict: List[Dict[str, Any]] = [
            video.dict()
            for video in videos
        ]

        logger.info(
            "[VIDEO NODE] Retrieved "
            f"{len(videos_dict)} videos"
        )

        # =================================================
        # 4. PEDAGOGICAL RERANKING
        # =================================================

        if opening and videos_dict:

            videos_dict = await asyncio.to_thread(
                rerank_videos,
                videos_dict,
                opening,
            )

            logger.info(
                "[VIDEO NODE] Reranking completed"
            )

        # =================================================
        # 5. CACHE STORE
        # =================================================

        if opening and videos_dict:

            await asyncio.to_thread(
                cache_service.set,
                opening,
                videos_dict,
            )

            logger.info(
                f"[VIDEO NODE] Cache updated | opening={opening}"
            )

        # =================================================
        # 6. SUCCESS
        # =================================================

        return {
            **state,
            "videos": videos_dict,
        }

    except Exception as e:

        logger.exception(
            f"[VIDEO NODE] Unexpected error: {e}"
        )

        return {
            **state,
            "videos": [],
            "error": str(e),
        }
