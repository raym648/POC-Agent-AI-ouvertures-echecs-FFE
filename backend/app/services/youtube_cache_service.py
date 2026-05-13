# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/youtube_cache_service.py

import logging

from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


logger = logging.getLogger(__name__)


class YouTubeCacheService:
    """
    Service de cache MongoDB pour les vidéos YouTube.

    Objectifs :
    - réduire les appels API YouTube
    - améliorer les performances
    - mutualiser les résultats d'ouverture
    - fournir un cache TTL automatique
    """

    def __init__(self) -> None:
        """
        Initialise la connexion MongoDB.
        """

        self.client: MongoClient = MongoClient(
            "mongodb://mongodb:27017"
        )

        self.db: Database = self.client[
            "ai_chess_agent"
        ]

        self.collection: Collection = self.db[
            "youtube_cache"
        ]

        # =================================================
        # TTL INDEX
        # =================================================

        # IMPORTANT:
        # Mongo supprimera automatiquement
        # les documents après 24h.

        self.collection.create_index(
            "created_at",
            expireAfterSeconds=86400,
        )

        logger.info(
            "[YOUTUBE CACHE] MongoDB cache initialized"
        )

    def get(
        self,
        opening: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère les vidéos depuis le cache MongoDB.

        Args:
            opening:
                nom de l'ouverture

        Returns:
            liste des vidéos ou None
        """

        try:

            result = self.collection.find_one(
                {
                    "opening": opening,
                }
            )

            if not result:

                logger.info(
                    "[YOUTUBE CACHE] Cache miss "
                    f"| opening={opening}"
                )

                return None

            logger.info(
                "[YOUTUBE CACHE] Cache hit "
                f"| opening={opening}"
            )

            return result.get(
                "videos",
                [],
            )

        except Exception as e:

            logger.exception(
                f"[YOUTUBE CACHE] Cache read error: {e}"
            )

            return None

    def set(
        self,
        opening: str,
        videos: List[Dict[str, Any]],
    ) -> None:
        """
        Sauvegarde les vidéos dans le cache MongoDB.

        Args:
            opening:
                nom de l'ouverture

            videos:
                vidéos sérialisées
        """

        try:

            self.collection.update_one(
                {
                    "opening": opening,
                },
                {
                    "$set": {
                        "opening": opening,
                        "videos": videos,
                        "created_at": datetime.utcnow(),
                    }
                },
                upsert=True,
            )

            logger.info(
                "[YOUTUBE CACHE] Cache updated "
                f"| opening={opening}"
            )

        except Exception as e:

            logger.exception(
                f"[YOUTUBE CACHE] Cache write error: {e}"
            )
