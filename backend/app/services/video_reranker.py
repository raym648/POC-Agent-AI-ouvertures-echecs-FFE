# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/video_reranker.py

from typing import Any, Dict, List


def compute_score(
    video: Dict[str, Any],
    opening: str,
) -> float:
    """
    Calcule un score de pertinence pédagogique
    pour une vidéo YouTube d'échecs.
    """

    score = 0.0

    opening_lower = opening.lower()

    title = (
        video.get("title", "")
        or ""
    ).lower()

    description = (
        video.get("description", "")
        or ""
    ).lower()

    # IMPORTANT:
    # youtube_service.py sérialise:
    # "channel"
    # et NON "channel_title"

    channel = (
        video.get("channel", "")
        or ""
    ).lower()

    # =================================================
    # 1. Matching ouverture
    # =================================================

    if opening_lower in title:
        score += 5.0

    if opening_lower in description:
        score += 2.0

    # =================================================
    # 2. Qualité description
    # =================================================

    score += min(
        len(description) / 100,
        3.0,
    )

    # =================================================
    # 3. Autorité chaîne
    # =================================================

    authority_channels = [
        "chessnetwork",
        "agadmator",
        "hanging pawns",
        "gothamchess",
        "daniel naroditsky",
        "saint louis chess club",
    ]

    if any(
        authority in channel
        for authority in authority_channels
    ):
        score += 4.0

    # =================================================
    # 4. Keywords pédagogiques
    # =================================================

    educational_keywords = [
        "opening",
        "theory",
        "lesson",
        "guide",
        "explained",
        "strategy",
        "course",
    ]

    if any(
        keyword in title
        for keyword in educational_keywords
    ):
        score += 2.0

    return score


def rerank_videos(
    videos: List[Dict[str, Any]],
    opening: str,
) -> List[Dict[str, Any]]:
    """
    Trie les vidéos par pertinence décroissante.
    """

    if not videos:
        return []

    reranked_videos: List[Dict[str, Any]] = []

    for video in videos:

        enriched_video = {
            **video,
            "score": compute_score(
                video,
                opening,
            ),
        }

        reranked_videos.append(
            enriched_video
        )

    return sorted(
        reranked_videos,
        key=lambda x: x["score"],
        reverse=True,
    )
