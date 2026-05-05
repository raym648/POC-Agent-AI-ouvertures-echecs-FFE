# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/rag/milvus_service.py

"""
Service de gestion Milvus pour le RAG.

Responsabilités :
- Connexion à Milvus
- Création / chargement de collection
- Insertion validée
- Recherche vectorielle robuste
"""

from __future__ import annotations

from typing import List, Dict

from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
)

from app.core.config import settings


class MilvusService:
    def __init__(self) -> None:
        self.collection_name = settings.VECTOR_COLLECTION_NAME
        self.vector_dim = settings.VECTOR_DIMENSION

        self._connect()
        self.collection = self._get_or_create_collection()
        self.collection.load()

    def _connect(self) -> None:
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
        )

    def _get_or_create_collection(self) -> Collection:
        if utility.has_collection(self.collection_name):
            collection = Collection(self.collection_name)
            return collection

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=4096,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.vector_dim,
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Chess openings vector store",
        )

        collection = Collection(
            name=self.collection_name,
            schema=schema,
        )

        collection.create_index(
            field_name="embedding",
            index_params={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
            },
        )

        return collection

    def insert_data(self, texts: List[str], embeddings: List[List[float]]) -> int:
        """
        Insère des documents vectorisés dans Milvus.

        Args:
            texts: documents textuels canoniques
            embeddings: embeddings associés

        Returns:
            int: nombre de documents insérés
        """
        if not texts:
            raise ValueError("No texts provided for insertion.")

        if not embeddings:
            raise ValueError("No embeddings provided for insertion.")

        if len(texts) != len(embeddings):
            raise ValueError("texts and embeddings must have the same length.")

        sanitized_texts: List[str] = []
        sanitized_embeddings: List[List[float]] = []

        for text, embedding in zip(texts, embeddings):
            if not text or not text.strip():
                continue

            if not embedding:
                continue

            if len(embedding) != self.vector_dim:
                raise ValueError(
                    f"Invalid embedding dimension: expected {self.vector_dim}, got {len(embedding)}"
                )

            sanitized_texts.append(text.strip()[:4096])
            sanitized_embeddings.append(embedding)

        if not sanitized_texts:
            raise ValueError("No valid documents to insert after sanitization.")

        before_count = self.collection.num_entities

        self.collection.insert(
            [
                sanitized_texts,       # text
                sanitized_embeddings,  # embedding
            ]
        )
        self.collection.flush()
        self.collection.load()

        after_count = self.collection.num_entities
        inserted_count = after_count - before_count

        return inserted_count

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """
        Recherche vectorielle.

        Args:
            query_embedding: embedding de la requête
            top_k: nombre max de résultats

        Returns:
            List[Dict]
        """
        if not query_embedding:
            return []

        if len(query_embedding) != self.vector_dim:
            raise ValueError(
                f"Invalid query embedding dimension: expected {self.vector_dim}, got {len(query_embedding)}"
            )

        self.collection.load()

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={
                "metric_type": "COSINE",
                "params": {"nprobe": 10},
            },
            limit=top_k,
            output_fields=["text"],
        )

        output: List[Dict] = []

        for hits in results:
            for hit in hits:
                text = hit.entity.get("text")

                if not text:
                    continue

                output.append(
                    {
                        "text": text,
                        "score": float(hit.score),
                    }
                )

        return output


milvus_service = MilvusService()
