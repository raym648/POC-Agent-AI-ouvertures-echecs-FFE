# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/youtube_cache_service.py


from datetime import datetime, timedelta  # noqa: F401
from typing import List, Dict, Any, Optional
from pymongo import MongoClient


class YouTubeCacheService:
    def __init__(self):
        self.client = MongoClient("mongodb://mongodb:27017")
        self.db = self.client["ai_chess_agent"]
        self.collection = self.db["youtube_cache"]

        # Index TTL (expire après 24h)
        self.collection.create_index(
            "created_at",
            expireAfterSeconds=86400
        )

    def get(self, opening: str) -> Optional[List[Dict[str, Any]]]:
        result = self.collection.find_one({"opening": opening})
        if result:
            return result.get("videos")
        return None

    def set(self, opening: str, videos: List[Dict[str, Any]]):
        self.collection.update_one(
            {"opening": opening},
            {
                "$set": {
                    "opening": opening,
                    "videos": videos,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
