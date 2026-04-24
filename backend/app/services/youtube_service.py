# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/youtube_service.py


import os
from googleapiclient.discovery import build
from typing import List
from app.models.video_schema import Video


class YouTubeService:
    """
    Service métier pour interagir avec l'API YouTube Data v3.

    RESPONSABILITÉ :
    - Exécuter une requête YouTube
    - Transformer la réponse en objets Video
    - Appliquer un filtrage léger

    ⚠️ IMPORTANT :
    - La construction de la query est externalisée (video_node)
    """

    def __init__(self):
        """
        Initialise le client YouTube avec la clé API.
        """
        self.api_key = os.getenv("YOUTUBE_API_KEY")

        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY manquante dans .env")

        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def search_videos(
        self,
        query: str,
        opening: str = None,
        max_results: int = 5
    ) -> List[Video]:
        """
        Recherche des vidéos pertinentes sur YouTube.

        Args:
            query (str): requête déjà construite (ex: enrichie via Lichess)
            opening (str, optional): ouverture pour filtrage sémantique
            max_results (int): nombre max de résultats

        Returns:
            List[Video]
        """

        request = self.youtube.search().list(
            q=query,
            part="snippet",
            maxResults=max_results,
            type="video",
            order="relevance"
        )

        response = request.execute()

        videos: List[Video] = []

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")

            # Sécurité minimale
            if not video_id:
                continue

            video = Video(
                title=snippet.get("title", ""),
                video_id=video_id,
                url=f"https://www.youtube.com/watch?v={video_id}",
                thumbnail=snippet.get("thumbnails", {}).get("high", {}).get("url", ""),  # noqa: E501
                description=snippet.get("description", ""),
                channel=snippet.get("channelTitle", "")
            )

            # Filtrage optionnel
            if self._is_relevant(video, opening):
                videos.append(video)

        return videos

    def _is_relevant(self, video: Video, opening: str = None) -> bool:
        """
        Filtrage basique pour éviter le bruit (live, blitz, etc.)
        + amélioration du recall
        """

        title = video.title.lower()
        description = video.description.lower()

        # =========================
        # 1. Blacklist (bruit)
        # =========================
        blacklist = ["blitz", "bullet", "live", "stream"]

        if any(word in title for word in blacklist):
            return False

        # =========================
        # 2. Filtrage sémantique (souple)
        # =========================
        if opening:
            opening_lower = opening.lower()

            # Accepte si présent dans titre OU description
            if opening_lower not in title and opening_lower not in description:
                return False

        return True
