# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/models/video_schema.py

from pydantic import BaseModel
from typing import List


class Video(BaseModel):
    """
    Modèle représentant une vidéo YouTube structurée.
    """
    title: str
    video_id: str
    url: str
    thumbnail: str
    description: str
    channel: str


class VideoResponse(BaseModel):
    """
    Réponse normalisée de l'API.
    """
    opening: str
    count: int
    videos: List[Video]
