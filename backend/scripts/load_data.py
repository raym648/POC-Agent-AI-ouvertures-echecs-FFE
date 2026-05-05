# POC-Agent-AI-ouvertures-echecs-FFE/scripts/load_data.py

"""
Script de chargement des données Wikichess dans Milvus.

Pipeline RAG :
- Chargement dataset structuré
- Normalisation document métier
- Embedding
- Indexation Milvus

Principe :
1 position d'ouverture = 1 document vectorisé + métadonnées métier
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.rag.embedding_service import embedding_service
from app.rag.milvus_service import milvus_service

DATASET_PATH = Path("./data/chess/wikichess_sample.json")


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    """
    Charge le dataset JSON Wikichess.

    Format attendu :
    [
        {
            "id": "...",
            "eco": "...",
            "opening": "...",
            "variation": "...",
            "line_san": "...",
            "position_fen": "...",
            "candidate_moves": [...],
            "stats": {...},
            "explanation": "...",
            "source_url": "...",
            "search_text": "..."
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


def normalize_text(value: Any, max_len: int = 4096) -> str:
    """Normalise une chaîne pour indexation."""
    if value is None:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    return " ".join(text.split())[:max_len]


def build_document(item: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Construit un document métier canonique indexable.
    """
    doc_id = normalize_text(item.get("id"), 256)
    eco = normalize_text(item.get("eco"), 16)
    opening = normalize_text(item.get("opening"), 256)
    variation = normalize_text(item.get("variation"), 256)
    line_san = normalize_text(item.get("line_san"), 1024)
    position_fen = normalize_text(item.get("position_fen"), 256)
    explanation = normalize_text(item.get("explanation"), 4096)
    source_url = normalize_text(item.get("source_url"), 1024)
    search_text = normalize_text(item.get("search_text"), 4096)

    if not doc_id:
        return None

    # Priorité au champ déjà préparé côté dataset
    text = search_text
    if not text:
        text = " ".join(
            part for part in [
                opening,
                variation,
                f"ECO {eco}" if eco else "",
                f"Line {line_san}" if line_san else "",
                explanation,
            ] if part
        )[:4096]

    if not text:
        return None

    return {
        "doc_id": doc_id,
        "eco": eco or "UNK",
        "opening": opening,
        "variation": variation,
        "line_san": line_san,
        "position_fen": position_fen,
        "source_url": source_url,
        "text": text,
    }


def main() -> None:
    dataset = load_dataset(DATASET_PATH)

    documents: List[Dict[str, Any]] = []

    for item in dataset:
        doc = build_document(item)
        if doc:
            documents.append(doc)

    if not documents:
        raise ValueError("No valid documents found in dataset.")

    print(f"Documents préparés pour indexation: {len(documents)}")

    texts = [doc["text"] for doc in documents]
    embeddings = embedding_service.embed_batch(texts)

    inserted = milvus_service.insert_data(documents, embeddings)

    print(f"✅ Documents insérés dans Milvus: {inserted}")


if __name__ == "__main__":
    main()
