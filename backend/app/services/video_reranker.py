# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/video_reranker.py


from typing import List, Dict


def compute_score(video: Dict, opening: str) -> float:
    score = 0.0

    title = video.get("title", "").lower()
    description = video.get("description", "").lower()
    channel = video.get("channel_title", "").lower()

    # =========================
    # 1. Présence opening
    # =========================
    if opening.lower() in title:
        score += 5.0

    if opening.lower() in description:
        score += 2.0

    # =========================
    # 2. Longueur description
    # =========================
    score += min(len(description) / 100, 3.0)

    # =========================
    # 3. Autorité chaîne (heuristique)
    # =========================
    authority_channels = [
        "chessnetwork",
        "agadmator",
        "hanging pawns",
        "gothamchess"
    ]

    if any(auth in channel for auth in authority_channels):
        score += 4.0

    return score


def rerank_videos(videos: List[Dict], opening: str) -> List[Dict]:
    for video in videos:
        video["score"] = compute_score(video, opening)

    return sorted(videos, key=lambda x: x["score"], reverse=True)
