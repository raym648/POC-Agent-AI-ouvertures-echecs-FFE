# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/rag/embedding_service.py

"""
Service d'embedding basé sur sentence-transformers.
Responsable de transformer du texte en vecteurs numériques exploitables.
"""

from __future__ import annotations

from typing import List

from sentence_transformers import SentenceTransformer
from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = self._infer_dimension()

    def _infer_dimension(self) -> int:
        """
        Détecte dynamiquement la dimension réelle du modèle.
        """
        vector = self.model.encode("dimension_check")
        dim = len(vector)

        if dim != settings.VECTOR_DIMENSION:
            raise ValueError(
                f"Embedding model dimension mismatch: "
                f"model={dim}, settings.VECTOR_DIMENSION={settings.VECTOR_DIMENSION}"
            )

        return dim

    def embed_text(self, text: str) -> List[float]:
        """
        Encode un texte unique.
        """
        if not text or not text.strip():
            return []

        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode un batch de textes.
        """
        valid_texts = [text.strip() for text in texts if text and text.strip()]

        if not valid_texts:
            return []

        return self.model.encode(
            valid_texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True,
        ).tolist()


embedding_service = EmbeddingService()
