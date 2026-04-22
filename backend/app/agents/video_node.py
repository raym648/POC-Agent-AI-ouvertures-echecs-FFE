# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/video_node.py

from typing import Dict, Any
from app.services.youtube_service import YouTubeService
from app.services.youtube_cache_service import YouTubeCacheService
from app.services.lichess_enrichment_service import LichessEnrichmentService
from app.services.video_reranker import rerank_videos


def video_retriever_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node LangGraph pour récupérer des vidéos pédagogiques.

    Version enrichie :
    - Cache MongoDB
    - Enrichissement Lichess
    - Re-ranking
    - Fallback intelligent conservé
    """

    opening = state.get("opening")
    cache = YouTubeCacheService()

    # =========================
    # 1. CACHE (uniquement si opening connue)
    # =========================
    if opening:
        cached = cache.get(opening)
        if cached:
            state["videos"] = cached
            return state

    # =========================
    # 2. CONSTRUCTION QUERY
    # =========================
    query = None

    # Cas 1 : opening connue → enrichie
    if opening:
        enrich = LichessEnrichmentService()
        query = enrich.enrich_opening(opening)

    # Cas 2 : fallback moves
    elif state.get("moves"):
        moves = state["moves"]
        moves_text = " ".join([m.get("san", "") for m in moves[:3]])
        query = f"chess opening {moves_text} explanation"

    # Cas 3 : fallback evaluation
    elif state.get("evaluation"):
        query = "chess strategy middlegame plan explanation"

    else:
        return state

    # =========================
    # 3. APPEL YOUTUBE
    # =========================
    service = YouTubeService()
    videos = service.search_videos(query, opening)

    videos_dict = [video.dict() for video in videos]

    # =========================
    # 4. RE-RANKING (si opening connue)
    # =========================
    if opening:
        videos_dict = rerank_videos(videos_dict, opening)

    # =========================
    # 5. CACHE SET
    # =========================
    if opening:
        cache.set(opening, videos_dict)

    # =========================
    # 6. STATE UPDATE
    # =========================
    state["videos"] = videos_dict

    return state
