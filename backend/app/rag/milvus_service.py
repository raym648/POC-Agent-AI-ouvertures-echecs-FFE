# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/rag/milvus_service.py

"""
Service de gestion de Milvus.
Responsable de :
- Connexion à la base
- Création de collection
- Insertion de données
- Recherche vectorielle
"""

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

    def __init__(self):
        self.connect()
        self.collection = self._get_or_create_collection()

    def connect(self):
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
        )

    def _get_or_create_collection(self) -> Collection:
        collection_name = settings.VECTOR_COLLECTION_NAME

        if utility.has_collection(collection_name):
            return Collection(collection_name)

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
                max_length=2000,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=settings.VECTOR_DIMENSION,
            ),
        ]

        schema = CollectionSchema(fields)

        collection = Collection(
            name=collection_name,
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

    def insert_data(self, texts: List[str], embeddings: List[List[float]]):
        self.collection.insert([texts, embeddings])
        self.collection.flush()

    def search(self, query_embedding: List[float], top_k: int) -> List[Dict]:
        self.collection.load()

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=top_k,
            output_fields=["text"],
        )

        output = []
        for hits in results:
            for hit in hits:
                output.append(
                    {
                        "text": hit.entity.get("text"),
                        "score": float(hit.score),
                    }
                )

        return output


milvus_service = MilvusService()
