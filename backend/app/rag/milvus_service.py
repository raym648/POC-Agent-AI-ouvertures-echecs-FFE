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

from typing import Any, Dict, List

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
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
            return Collection(self.collection_name)

        fields = [
            FieldSchema(
                name="pk",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            ),
            FieldSchema(
                name="doc_id",
                dtype=DataType.VARCHAR,
                max_length=256,
            ),
            FieldSchema(
                name="eco",
                dtype=DataType.VARCHAR,
                max_length=16,
            ),
            FieldSchema(
                name="opening",
                dtype=DataType.VARCHAR,
                max_length=256,
            ),
            FieldSchema(
                name="variation",
                dtype=DataType.VARCHAR,
                max_length=256,
            ),
            FieldSchema(
                name="line_san",
                dtype=DataType.VARCHAR,
                max_length=1024,
            ),
            FieldSchema(
                name="position_fen",
                dtype=DataType.VARCHAR,
                max_length=256,
            ),
            FieldSchema(
                name="source_url",
                dtype=DataType.VARCHAR,
                max_length=1024,
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

    def insert_data(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
        """
        Insère des documents métier vectorisés dans Milvus.
        """
        if not documents:
            raise ValueError("No documents provided for insertion.")

        if not embeddings:
            raise ValueError("No embeddings provided for insertion.")

        if len(documents) != len(embeddings):
            raise ValueError("documents and embeddings must have the same length.")

        doc_ids: List[str] = []
        ecos: List[str] = []
        openings: List[str] = []
        variations: List[str] = []
        lines_san: List[str] = []
        positions_fen: List[str] = []
        source_urls: List[str] = []
        texts: List[str] = []
        vectors: List[List[float]] = []

        for doc, embedding in zip(documents, embeddings):
            if len(embedding) != self.vector_dim:
                raise ValueError(
                    f"Invalid embedding dimension: expected {self.vector_dim}, got {len(embedding)}"
                )

            doc_ids.append(doc["doc_id"])
            ecos.append(doc["eco"])
            openings.append(doc["opening"])
            variations.append(doc["variation"])
            lines_san.append(doc["line_san"])
            positions_fen.append(doc["position_fen"])
            source_urls.append(doc["source_url"])
            texts.append(doc["text"])
            vectors.append(embedding)

        before_count = self.collection.num_entities

        self.collection.insert(
            [
                doc_ids,
                ecos,
                openings,
                variations,
                lines_san,
                positions_fen,
                source_urls,
                texts,
                vectors,
            ]
        )

        self.collection.flush()
        self.collection.load()

        after_count = self.collection.num_entities
        return after_count - before_count

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Recherche vectorielle.
        """
        if not query_embedding:
            return []

        if len(query_embedding) != self.vector_dim:
            raise ValueError(
                f"Invalid query embedding dimension: expected {self.vector_dim}, got {len(query_embedding)}"
            )

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={
                "metric_type": "COSINE",
                "params": {"nprobe": 10},
            },
            limit=top_k,
            output_fields=[
                "doc_id",
                "eco",
                "opening",
                "variation",
                "line_san",
                "position_fen",
                "source_url",
                "text",
            ],
        )

        output: List[Dict[str, Any]] = []

        for hits in results:
            for hit in hits:
                output.append(
                    {
                        "doc_id": hit.entity.get("doc_id"),
                        "eco": hit.entity.get("eco"),
                        "opening": hit.entity.get("opening"),
                        "variation": hit.entity.get("variation"),
                        "line_san": hit.entity.get("line_san"),
                        "position_fen": hit.entity.get("position_fen"),
                        "source_url": hit.entity.get("source_url"),
                        "text": hit.entity.get("text"),
                        "score": float(hit.score),
                    }
                )

        return output


milvus_service = MilvusService()
