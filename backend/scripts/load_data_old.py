# POC-Agent-AI-ouvertures-echecs-FFE/scripts/load_data.py

"""
Script de chargement des données Wikichess dans Milvus.

Pipeline RAG corrigé :
- Chargement dataset structuré
- Construction d'un document métier canonique
- Embedding
- Indexation Milvus

Principe :
1 position d'ouverture = 1 document vectorisé
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.rag.embedding_service import embedding_service
from app.rag.milvus_service import milvus_service

DATASET_PATH = Path("./data/chess/wikichess_sample.json")


def load_dataset(path: Path) -> List[dict]:
    """
    Charge le dataset JSON.

    Format attendu :
    [
        {
            "text": "..."
        }
    ]
    """
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Dataset must be a list of JSON objects.")

    return data


def build_search_text(item: dict) -> str:
    """
    Construit un document canonique vectorisable.

    Priorité :
    - exploite item['text'] si dataset minimal
    - normalise et compacte le texte
    """
    raw_text = item.get("text", "")

    if not raw_text or not raw_text.strip():
        return ""

    normalized = " ".join(raw_text.split())
    return normalized[:4096]


def main() -> None:
    dataset = load_dataset(DATASET_PATH)

    documents: List[str] = []

    for item in dataset:
        text = build_search_text(item)

        if text:
            documents.append(text)

    if not documents:
        raise ValueError("No valid documents found in dataset.")

    print(f"Documents préparés pour indexation: {len(documents)}")

    embeddings = embedding_service.embed_batch(documents)

    inserted = milvus_service.insert_data(documents, embeddings)

    print(f"✅ Documents insérés dans Milvus: {inserted}")


if __name__ == "__main__":
    main()
