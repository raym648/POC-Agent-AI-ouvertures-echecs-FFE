# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/rag/embedding_service.py 

"""
Service d'embedding basé sur sentence-transformers.
Responsable de transformer du texte en vecteurs numériques exploitables.
"""

from sentence_transformers import SentenceTransformer
from typing import List
# from backend.app.core.config import settings
from app.core.config import settings


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()


embedding_service = EmbeddingService()
