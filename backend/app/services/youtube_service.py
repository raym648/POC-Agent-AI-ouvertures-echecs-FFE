# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/youtube_service.py

import logging
import os

from typing import List

from googleapiclient.discovery import build

from app.models.video_schema import Video


logger = logging.getLogger(__name__)


class YouTubeService:
    """
    Service métier pour interagir avec l'API YouTube Data v3.

    RESPONSABILITÉS :
    - exécuter les requêtes YouTube
    - transformer les réponses en objets Video
    - appliquer un filtrage sémantique léger
    - réduire le bruit (live/blitz/etc.)
    """

    def __init__(self):
        """
        Initialise le client YouTube Data API v3.
        """

        self.api_key = os.getenv(
            "YOUTUBE_API_KEY"
        )

        if not self.api_key:

            raise ValueError(
                "YOUTUBE_API_KEY manquante dans .env"
            )

        self.youtube = build(
            "youtube",
            "v3",
            developerKey=self.api_key,
        )

    def search_videos(
        self,
        query: str,
        opening: str = None,
        max_results: int = 5,
    ) -> List[Video]:
        """
        Recherche des vidéos pédagogiques YouTube.

        Args:
            query:
                requête enrichie générée par video_node

            opening:
                ouverture utilisée pour filtrage sémantique

            max_results:
                nombre maximum de vidéos retournées

        Returns:
            List[Video]
        """

        logger.info(
            f"[YOUTUBE SERVICE] Searching videos | query={query}"
        )

        request = self.youtube.search().list(
            q=query,
            part="snippet",
            maxResults=max_results,
            type="video",
            order="relevance",
        )

        response = request.execute()

        videos: List[Video] = []

        for item in response.get("items", []):

            snippet = item.get("snippet", {})
            video_id = (
                item.get("id", {})
                .get("videoId")
            )

            # =============================================
            # Minimal validation
            # =============================================

            if not video_id:
                continue

            title = snippet.get(
                "title",
                "",
            )

            description = snippet.get(
                "description",
                "",
            )

            channel = snippet.get(
                "channelTitle",
                "",
            )

            video = Video(
                title=title,
                video_id=video_id,
                url=(
                    "https://www.youtube.com/watch"
                    f"?v={video_id}"
                ),
                thumbnail=(
                    snippet.get(
                        "thumbnails",
                        {},
                    )
                    .get("high", {})
                    .get("url", "")
                ),
                description=description,
                channel=channel,
            )

            # =============================================
            # Semantic filtering
            # =============================================

            if self._is_relevant(
                video,
                opening,
            ):

                videos.append(video)

        logger.info(
            "[YOUTUBE SERVICE] Retrieved "
            f"{len(videos)} filtered videos"
        )

        return videos

    def _is_relevant(
        self,
        video: Video,
        opening: str = None,
    ) -> bool:
        """
        Filtrage pédagogique léger.

        Objectifs :
        - éliminer le bruit
        - améliorer la pertinence
        - conserver un recall élevé
        """

        title = (
            video.title or ""
        ).lower()

        description = (
            video.description or ""
        ).lower()

        # =============================================
        # 1. Noise filtering
        # =============================================

        blacklist = [
            "blitz",
            "bullet",
            "live",
            "stream",
        ]

        if any(
            word in title
            for word in blacklist
        ):

            return False

        # =============================================
        # 2. Semantic opening filtering
        # =============================================

        if opening:

            opening_lower = (
                opening.lower()
            )

            # IMPORTANT:
            # Ancienne version :
            # strict exact match
            #
            # Nouveau :
            # keyword semantic matching
            #
            # améliore fortement le recall

            keywords = [
                keyword.strip()
                for keyword in opening_lower.split()
                if keyword.strip()
            ]

            if keywords:

                matched = any(
                    (
                        keyword in title
                        or keyword in description
                    )
                    for keyword in keywords
                )

                if not matched:
                    return False

        return True
